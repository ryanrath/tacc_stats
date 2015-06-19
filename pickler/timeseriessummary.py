#!/usr/bin/env python
import job_stats
import numpy
import itertools

# Stupid python incompatiblities
from sys import version as python_version
if python_version.startswith("2.6"):
    from backport_collections import Counter
else:
    from collections import Counter

TIMESERIES_VERSION = 4

MEGA = 1024.0 * 1024.0
GIGA = MEGA * 1024.0

def getallstats(j, times, host, metricname, interface, indices):

    ifidx = None
    if interface != "all":
        ifidx = indices[metricname][interface]

    result = {}
    for devname, devstats in host.stats[metricname].iteritems():
        if interface == "all":
            result[devname] = numpy.interp(times, host.times, numpy.sum(devstats, axis = 1))
        else:
            result[devname] = numpy.interp(times, host.times, numpy.array(devstats[:,ifidx]))

    return result

def getinterfacestats(hoststats, metricname, interface, indices):

    ifidx = None
    if interface != "all":
        ifidx = indices[metricname][interface]

    totals = None
    for devstats in hoststats[metricname].itervalues():
        if totals == None:
            if interface == "all":
                totals = numpy.sum(devstats, axis = 1)
            else:
                totals = numpy.array(devstats[:,ifidx])
        else:
            if interface == "all":
                totals += numpy.sum(devstats, axis = 1)
            else:
                totals += numpy.array(devstats[:,ifidx])

    return totals

def nativefloatlist(numpyarray):
    return numpyarray.tolist()

def computesubsamples(hosttimes, timedeltas):
    MINTIMEDELTA = 5
    LEAD_IN_OUT = 3
    MAX_DATAPOINTS = 100

    if len(timedeltas) < 100:
        valid =  [ True ] + [ True if x > MINTIMEDELTA else False for x in timedeltas ]
        return numpy.compress(valid, hosttimes)

    times = [ hosttimes[0] ]

    leadin = hosttimes[LEAD_IN_OUT]
    leadout = hosttimes[-LEAD_IN_OUT]
    interval = (leadout - leadin) / (100 - 2 * LEAD_IN_OUT)

    lastvalid = leadin
    for t,dt in itertools.izip(hosttimes[1:], timedeltas):
        if t < leadin:
            if dt > MINTIMEDELTA:
                times.append(t)
        elif t > leadout:
            if dt > MINTIMEDELTA:
                times.append(t)
        else:
            if t > lastvalid:
                times.append(t)
                lastvalid += interval
    
    return numpy.array(times)


class TimeSeriesSummary(object):

    def __init__(self):
        self.hostmap = {}
        self.metrics = {
            "cpuuser": [ {
                "metric": "cpu",
                "devicebased": True,
                "formula": "numpy.diff(a[0]) * 100.0 / numpy.diff(a[1])",
                "interfaces": [ "user", "all" ]
            } ] ,
            "membw": [ {
                "metric": "intel_snb_imc",
                "formula": "numpy.diff( 64.0 *( a[0] + a[1] ) / GIGA) / delta_t",
                "interfaces": [ "CAS_READS", "CAS_WRITES" ]
            }, {
                "metric": "intel_hsw_imc",
                "formula": "numpy.diff( 64.0 *( a[0] + a[1] ) / GIGA) / delta_t",
                "interfaces": [ "CAS_READS", "CAS_WRITES" ]
            }, {
                "metric": "intel_uncore",
                "formula": "numpy.diff( 64.0 *( a[0] + a[1] ) / GIGA) / delta_t",
                "interfaces": [ "L3_MISS_READ", "L3_MISS_WRITE" ]
            }],
            "simdins": [ {
                "metric": "intel_snb",
                "formula": "numpy.diff( a[0] + a[1] + a[2] ) / delta_t",
                "interfaces": ["SIMD_DOUBLE_256", "SSE_DOUBLE_PACKED", "SSE_DOUBLE_SCALAR"]
            }, {
                "metric": "intel_pmc3",
                "formula":  "numpy.diff( a[0] ) / delta_t",
                "interfaces": [ "FP_COMP_OPS_EXE_SSE" ]
            } ],
            "memused_minus_diskcache": [ {
                "metric": "mem",
                "formula": "numpy.array(a[0] - a[1] - a[2])[1:] / GIGA",
                "interfaces": ["MemUsed", 'FilePages', "Slab"]
            } ], 
            "lnet": [ {
                "metric": "lnet",
                "formula": "numpy.diff( a[0] + a[1] ) / delta_t / MEGA",
                "interfaces": [ "tx_bytes", "rx_bytes" ]
            } ],
            "ib_lnet": [ {
                "metric": "ib_sw",
                "formula": "numpy.diff( a[0] + a[1] ) / delta_t / MEGA",
                "interfaces": [ "tx_bytes", "rx_bytes" ]
                # TODO - subtract the lnet.tx and rx_bytses data
            } ]
        }

    def process(self, j, indices):

        self.times = computesubsamples(j.times, numpy.diff(j.times))

        if len(j.hosts) > 64:
            return self.getminmaxmed(j, indices)
        else:
            return self.gettimeseries(j, indices)

    def collatedata(self, hostindexes, values):

        result = []
        for timepoint, hostidx in enumerate(hostindexes):
            try:
                result.append( [ values[hostidx, timepoint], int(hostidx) ] )
            except IndexError as e:
                pass

        return result

    def getminmaxmed(self, j, indices):

        for hostidx, host in enumerate(j.hosts.itervalues()):
            self.hostmap[str(hostidx)] = host.name

        outdata = { "version": TIMESERIES_VERSION,  "hosts": self.hostmap }
        for outmetric, setlist in self.metrics.iteritems():
            for settings in setlist:
                outdata[outmetric] = self.get_minmaxmed_data(j, indices, settings)
                if outdata[outmetric] == None:
                    del outdata[outmetric]
                else:
                    break

        return outdata

    def getvalues(self, metric, formula, interfaces, j, host, indices):
        if metric not in host.stats:
            return None

        a = []
        for interface in interfaces:
            if interface != "all" and interface not in indices[metric]:
                return None
            a.append( numpy.interp(self.times, host.times, getinterfacestats(host.stats, metric, interface, indices) ) )

        delta_t = numpy.diff(self.times)

        return eval(formula)

    def getdevicevalues(self, metric, formula, interfaces, j, host, indices):
        if metric not in host.stats:
            return None

        devs = []
        for interface in interfaces:
            if interface != "all" and interface not in indices[metric]:
                return None
            devs.append( getallstats(j, self.times, host, metric, interface, indices) )

        delta_t = numpy.diff(self.times)

        res = {}
        devnames = {}

        for devname in devs[0].iterkeys():
            a = []
            for ifidx, interface in enumerate(interfaces):
                a.append(devs[ifidx][devname])
            
            res[str(devname)] = eval(formula).tolist()
            devnames[str(devname)] = metric + str(devname)

        return res, devnames

    def get_timeseries_data(self, j, indices, settings):

        results = { "hosts": {}, "times": self.times[1:].tolist() }

        for hostidx, host in enumerate(j.hosts.itervalues()):
            data = self.getvalues(settings['metric'], settings['formula'], settings['interfaces'], j, host, indices)
            if data == None:
                return None

            results['hosts'][str(hostidx)] = {}

            if ('devicebased' in settings) and (settings['devicebased'] == True):
                devicedata, devnames = self.getdevicevalues(settings['metric'], settings['formula'], settings['interfaces'], j, host, indices)
                results['hosts'][str(hostidx)]["dev"] = devicedata
                results['hosts'][str(hostidx)]["names"] = devnames

            results['hosts'][str(hostidx)]["all"] = data.tolist()

        return results

    def get_minmaxmed_data(self, j, indices, settings):

        d = numpy.zeros( (len(j.hosts), len(self.times) - 1) )

        for hostidx, host in enumerate(j.hosts.itervalues()):
            data = self.getvalues(settings['metric'], settings['formula'], settings['interfaces'], j, host, indices)
            if data == None:
                return None
            d[hostidx,:] = data

        sortarr = numpy.argsort(d, axis=0)

        results = {
            "min": self.collatedata(sortarr[0,:], d),
            "max": self.collatedata(sortarr[-1,:], d),
            "med": self.collatedata(sortarr[sortarr.shape[0] / 2, :], d),
            "times": self.times[1:].tolist(),
            "hosts": {}
        }

        # Ensure head node is always in list
        uniqhosts = Counter( [ 0 ] )
        uniqhosts.update(sortarr[0, :])
        uniqhosts.update(sortarr[-1, :])
        uniqhosts.update(sortarr[sortarr.shape[1] / 2, :])

        for hostidx, host in enumerate(j.hosts.itervalues()):
            if hostidx not in uniqhosts.keys():
                continue

            results['hosts'][str(hostidx)] = {}
            if ('devicebased' in settings) and (settings['devicebased'] == True):
                devicedata, devnames = self.getdevicevalues(settings['metric'], settings['formula'], settings['interfaces'], j, host, indices)
                results['hosts'][str(hostidx)]["dev"] = devicedata
                results['hosts'][str(hostidx)]["names"] = devnames

            results['hosts'][str(hostidx)]["all"] = d[hostidx].tolist()

        return results

    def gettimeseries(self, j, indices):

        for hostidx, host in enumerate(j.hosts.itervalues()):
            self.hostmap[str(hostidx)] = host.name

        outdata = { "version": TIMESERIES_VERSION,  "hosts": self.hostmap }
        for outmetric, setlist in self.metrics.iteritems():
            for settings in setlist:
                outdata[outmetric] = self.get_timeseries_data(j, indices, settings)
                if outdata[outmetric] == None:
                    del outdata[outmetric]
                else:
                    break

        return outdata
    
