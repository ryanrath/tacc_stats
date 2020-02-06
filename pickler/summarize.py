#!/usr/bin/env python

import datetime
import job_stats
import math
import numpy
import os
import scipy
import sys
import json
import traceback
from scipy import stats
from extra.catastrophe import Catastrophe
from procdump import TaccProcDump
import logging

from timeseriessummary import TimeSeriesSummary

SUMMARY_VERSION = "0.9.37"

VERBOSE = False

# Max discrepency between walltime and records time
TIMETHRESHOLD = 60

# Minimum time difference between two consecutive data points
MINTIMEDELTA = 5

# Compact format
COMPACT_OUTPUT = True

#ignore warnings from numpy
numpy.seterr(all='ignore')

TOO_FEW_DATAPOINTS = 1

def removeDotKey(obj):

    for key in obj.keys():
        new_key = key.replace(".", "-")
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj

def compute_catastrophe(j):

    try:
        c = Catastrophe()
        if c.setup(j):
            c.compute_metric()
            if c.metric > 1000000.0:
                c.metric = 999999.0
            return c.metric
        else:
            return { 'error': 'setup failed' }
    except Exception as e:
        return { 'error': "{}".format(e) }


def compute_ratio(stats, indices, numerator, denominator, out):
    if numerator in indices and denominator in indices and 'ERROR' not in indices:
        cidx = indices[numerator]
        insidx = indices[denominator]
        if stats[-1, insidx] > 0:
            out.append( 1.0 * stats[-1,cidx] / stats[-1, insidx] )

def compute_sum(stats, indices, a, b, out, hostwalltime):
    if a in indices and b in indices and 'ERROR' not in indices:
        cidx = indices[a]
        insidx = indices[b]
        out.append( (1.0 * stats[-1,cidx] + 1.0 * stats[-1, insidx])/ hostwalltime )

def addtoseries(interface, series, enties, data):
    if interface not in series:
        series[interface] = numpy.array(data)
        enties[interface] = 1
    else:
        series[interface] += data
        enties[interface] += 1

def gentimedata(j, indices, ignorelist, isevent):

    # Do the special derived metrics:
    derived = { 
            "intel_snb": { 
                "meancpiref":  [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "INSTRUCTIONS_RETIRED" ],
                "meancpldref": [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "LOAD_L1D_ALL" ],
                "flops":   [ "4.0*numpy.diff(a[0]) + 2.0*numpy.diff(a[1])", "SIMD_DOUBLE_256", "SSE_DOUBLE_ALL" ],
                "flops":   [ "4.0*numpy.diff(a[0]) + 2.0*numpy.diff(a[1]) + numpy.diff(a[2])", "SIMD_DOUBLE_256", "SSE_DOUBLE_PACKED", "SSE_DOUBLE_SCALAR" ] 
            },
            "intel_hsw": { 
                "meancpiref":  [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "INSTRUCTIONS_RETIRED" ],
                "meancpldref": [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "LOAD_L1D_ALL" ],
                "flops":   [ "4.0*numpy.diff(a[0]) + 2.0*numpy.diff(a[1])", "SIMD_DOUBLE_256", "SSE_DOUBLE_ALL" ],
                "flops":   [ "4.0*numpy.diff(a[0]) + 2.0*numpy.diff(a[1]) + numpy.diff(a[2])", "SIMD_DOUBLE_256", "SSE_DOUBLE_PACKED", "SSE_DOUBLE_SCALAR" ] 
            },
            "intel_ivb": {
                "meancpiref":  [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "INSTRUCTIONS_RETIRED" ],
                "meancpldref": [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "LOAD_L1D_ALL" ]
            },
        "intel_knl": {
            "meancpiref":  ["numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "INSTRUCTIONS_RETIRED"]
        },
        "intel_skx": {
            "meancpiref":  ["numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "INSTRUCTIONS_RETIRED"],
            "flops": ["8.0*numpy.diff(a[0]) + 4.0*numpy.diff(a[1]) + 2.0*numpy.diff(a[2]) + numpy.diff(a[3])",
                      "FP_ARITH_INST_RETIRED_512B_PACKED_DOUBLE",
                      "FP_ARITH_INST_RETIRED_256B_PACKED_DOUBLE",
                      "FP_ARITH_INST_RETIRED_128B_PACKED_DOUBLE",
                      "FP_ARITH_INST_RETIRED_SCALAR_DOUBLE"]
        },
            "intel_pmc3": {
                "meancpiref":  [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "INSTRUCTIONS_RETIRED" ],
                "meancpldref": [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "MEM_LOAD_RETIRED_L1D_HIT" ],
            },
        "intel_8pmc3": {
            "meancpiref":  [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "INSTRUCTIONS_RETIRED" ],
            "meancpldref": [ "numpy.diff(a[0])/numpy.diff(a[1])", "CLOCKS_UNHALTED_REF", "MEM_LOAD_RETIRED_L1D_HIT" ],
        }
    }

    computed = {
        "intel_snb_imc": {
            "membw": [ "64.0 * (a[0] + a[1])", "CAS_READS", "CAS_WRITES" ]
        },
        "intel_skx_imc": {
            "membw": [ "64.0 * (a[0] + a[1])", "CAS_READS", "CAS_WRITES" ]
        },
        "mem": {
            "mem_used_minus_cache": [ "a[0] - a[1] - a[2]", "MemUsed", "FilePages", "Slab" ]
        }
    }

    if "intel_snb_imc" in isevent:
        isevent["intel_snb_imc"]["membw"] = True
    if "intel_skx_imc" in isevent:
        isevent["intel_skx_imc"]["membw"] = True
    if "mem" in isevent:
        isevent["mem"]["mem_used_minus_cache"] = False

    ndatapoints = len(j.times)
    if ndatapoints < 3:
        return { "error": TOO_FEW_DATAPOINTS }

    times = numpy.linspace(j.start_time, j.end_time, ndatapoints)

    # Data for each host is normalized to ndatapoints data points using
    # piecewise linear interpolation. The host data is then combined to 
    # produce job-timeseries data.

    hostdata = {}

    for host in j.hosts.itervalues():  # for all the hosts present in the file
        for metric in host.stats.iterkeys():
            if metric in ignorelist:
                continue

            if metric not in indices:
                logging.warning('%s not in index list for %s', metric, host.name)
                continue

            for interface in indices[metric].keys() + ["all"]:
                if metric not in hostdata:
                    hostdata[metric] = {}
                if interface not in hostdata[metric]:
                    hostdata[metric][interface] = numpy.interp(times, host.times, getinterfacestats(host.stats, metric, interface, indices))
                else:
                    hostdata[metric][interface] += numpy.interp(times, host.times, getinterfacestats(host.stats, metric, interface, indices))

            if metric in computed:
                for outname, formula in computed[metric].iteritems():
                    a = []
                    for interface in formula[1:]:
                        if interface in indices[metric]:
                            a.append(getinterfacestats(host.stats, metric, interface, indices))
                        else:
                            break

                    if len(a) != (len(formula)-1):
                        break;

                    if outname not in hostdata[metric]:
                        hostdata[metric][outname] = numpy.interp(times, host.times, eval(formula[0]))
                    else:
                        hostdata[metric][outname] += numpy.interp(times, host.times, eval(formula[0]))

    results = {}
    for m,v in hostdata.iteritems():
        results[m] = {}
        for i,a in v.iteritems():
            if i == "all":
                continue
            if '.' in i:
                continue
            if m == "cpu":
                results[m][i] = calculate_stats( numpy.diff(a) / numpy.diff(hostdata[m]["all"]) )
            elif isevent[m][i]:
                results[m][i] = calculate_stats( numpy.diff(a) / numpy.diff(times) )
            else:
                results[m][i] = calculate_stats( a )

        if m in derived:
            if 'analysis' not in results:
                results['analysis'] = {}

            for outname, formula in derived[m].iteritems():
                func = formula[0]
                a = []
                for interface in formula[1:]:
                    if interface in v:
                        a.append(v[interface])
                    else:
                        break

                if len(a) != (len(formula)-1):
                    break;

                results['analysis'][outname] = calculate_stats( eval(func) )

    return results

def converttooutput(series, summaryDict, j):
    for l in series.keys():
        for k in series[l].keys():
            if isinstance(series[l][k], dict):
                for i in series[l][k].keys():
                    v = calculate_stats(series[l][k][i])
                    addinstmetrics(summaryDict,j.overflows, l, i, k, v)
            else:
                v = calculate_stats(series[l][k])
                addmetrics(summaryDict,j.overflows, l, k, v)

class LariatManager:
    def __init__(self, lariatpath):
        self.lariatpath = lariatpath
        self.lariatdata = dict()
        self.filesprocessed = []
        self.errors = dict()

    def find(self, jobid, jobstarttime, jobendtime):

        if jobid in self.lariatdata:
            return self.lariatdata[jobid]

        for days in (0, -1, 1):
            searchday = datetime.datetime.utcfromtimestamp(jobendtime) + datetime.timedelta(days)
            lfilename = os.path.join(self.lariatpath, searchday.strftime('%Y'), searchday.strftime('%m'), searchday.strftime('lariatData-sgeT-%Y-%m-%d.json'))
            self.loadlariat(lfilename)
            if jobid in self.lariatdata:
                return self.lariatdata[jobid]

        for days in (0, -1, 1):
            searchday = datetime.datetime.utcfromtimestamp(jobstarttime) + datetime.timedelta(days)
            lfilename = os.path.join(self.lariatpath, searchday.strftime('%Y'), searchday.strftime('%m'), searchday.strftime('lariatData-sgeT-%Y-%m-%d.json'))
            self.loadlariat(lfilename)

            if jobid in self.lariatdata:
                return self.lariatdata[jobid]

        return None

    def loadlariat(self, filename):

        if filename in self.filesprocessed:
            # No need to reparse file. If the job data was in the file, then this search
            # function would not have been called.
            return

        try:
            with open(filename, "rb") as fp:

                # Unfortunately, the lariat data is not in valid json
                # This workaround converts the illegal \' into valid quotes
                content = fp.read().replace("\\'", "'")
                lariatJson = json.loads(content, object_hook=removeDotKey)

                for k,v in lariatJson.iteritems():
                    if k not in self.lariatdata:
                        self.lariatdata[k] = v[0]
                    else:
                        # Have already got a record for this job. Keep the record
                        # that has longer recorded runtime since this is probably
                        # the endofjob record.
                        if 'runtime' in v[0] and 'runtime' in self.lariatdata[k] and self.lariatdata[k]['runtime'] < v[0]['runtime']:
                            self.lariatdata[k] = v[0]

                self.filesprocessed.append(filename)

        except Exception as e:
            self.errors[filename] = "Error processing {}. Error was {}.".format(filename, e)


def calculate_stats(v):
    res = { }

    if len(v) > 0:

        try:
            (
              v_n,
              (v_min, v_max),
              v_avg,
              v_var,
              v_skew,
              v_kurt,
              ) = scipy.stats.describe(v)
        except TypeError as e:
            return { 'error': 'TypeError' }

        res['max'] = float(v_max)
        res['avg'] = v_avg
        res['krt'] = v_kurt
        res['min'] = float(v_min)
        res['skw'] = v_skew
        res['cnt'] = len(v)
        if res['min'] == res['max']:
            res['med'] = res['min']
            res['std'] = 0.0
        else:
            res['med'] = float(numpy.median(v, axis=0))
            if len(v) > 2:
                res['std'] = scipy.stats.tstd(v)

        if len(v) > 1 and abs(v_avg) > 0:
            res['cov'] = math.sqrt(v_var) / v_avg
        else:
            res['cov'] = 0.0

    return res

def addinstmetrics(summary, overflows, device, interface, instance, values):

    key = (device + "-" + interface + "-" + instance).replace(".", "-")

    data = values

    if COMPACT_OUTPUT and 'avg' in values and values['avg'] == 0.0:
        # Don't bother including redundant information
        data = { 'avg': 0.0 }

    if device in overflows and interface in overflows[device] and instance in overflows[device][interface]:
        data = { "error": 2048, "error_msg": "Counter overflow on hosts " + str(list(overflows[device][interface][instance])) }
    
    if device not in summary:
        summary[device.replace(".","-")] = {}
    if interface not in summary[device]:
        summary[device.replace(".","-")][interface.replace(".","-")] = {}

    summary[device.replace(".","-")][interface.replace(".","-")][instance.replace(".","-")] = data

def addmetrics(summary, overflows, device, interface, values):

    data = values

    if COMPACT_OUTPUT and 'avg' in values and values['avg'] == 0.0:
        return

    if device in overflows:
        # The cpu device is special because all of the counters are summed together - an overflow in one
        # impacts all cpu metrics.
        if (device == "cpu") or ( interface in overflows[device]):
            data = { "error": 2048, "error_msg": "Counter overflow on hosts " + str(overflows[device]) }
    
    if device not in summary:
        summary[device.replace(".","-")] = {}

    summary[device.replace(".","-")][interface.replace(".","-")] = data

# Unfortunately, due to historical reasons, the type and content of the accounting
# records differ for different resources. I have no idea why the data isn't put in 
# normalised form.
def getnumhosts(acct):
    if 'nodes' in acct and acct['nodes'] is not None:
        return int(acct['nodes'])
    if 'nnodes' in acct:
        return int(acct['nnodes'])
    if 'slots' in acct:
        if 'hostname' in acct and acct['hostname'].find('ranger') != -1:
            return int(acct['slots']) / 16
        else:
            return int(acct['slots']) / 12
    return -1

def getinterfacestats(hoststats, metricname, interface, indices):

    ifidx = None
    if interface != "all":
        ifidx = indices[metricname][interface]

    totals = None
    for devstats in hoststats[metricname].itervalues():
        if totals is None:
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

def getperinterfacemetrics():
    return [ "cpu", "mem", "sched", "intel_pmc3", "intel_uncore", "intel_hsw", "intel_hsw_cbo", "intel_hsw_hau", "intel_hsw_imc", "intel_hsw_qpi", "intel_hsw_pcu", "intel_hsw_r2pci", "intel_snb", "intel_snb_cbo", "intel_snb_imc", "intel_snb_pcu", "intel_snb_hau", "intel_snb_qpi", "intel_snb_r2pci",
             "cputhreads",
             "amd64_core",
             "amd64_sock",
             "intel_skx",
             "intel_skx_imc",
             "intel_knl",
             "intel_knl_mc_uclk",
             "intel_knl_mc_dclk",
             "intel_knl_edc_eclk",
             "intel_knl_edc_uclk",
                     "intel_ivb",
                     "intel_ivb_cbo",
                     "intel_ivb_hau",
                     "intel_ivb_imc",
                     "intel_ivb_pcu",
                     "intel_ivb_r2pci"]


def fix_unicode(value):
    if type(value) == unicode:
        return value.encode('ascii', 'ignore')
    elif type(value) == dict:
        temp = {}
        for k, v in value.iteritems():
            temp[k.encode('ascii', 'ignore')] = fix_unicode(v)
        return temp
    elif type(value) == list:
        temp = []
        for i in value:
            temp.append(fix_unicode(i))
        return temp
    else:
        return value


def summarize(j, lariatcache):

    summaryDict = {}
    summaryDict['Error'] = list(j.errors)
    
    # TODO summarySchema = {}

    # Data for a host is calculated in the munge_times() function.
    # A job is marked as complete if either it had zero-walltime or
    # if all hosts had data.

    summaryDict['complete'] = True

    if j.acct['end_time'] - j.acct['start_time'] > 0:
        if getnumhosts(j.acct) != len(j.hosts):
            summaryDict['complete'] = False
        else:
            for hdata in j.hosts.itervalues():
                if not hdata.complete:
                    summaryDict['complete'] = False
                    break

    metrics = None
    statsOk = True

    perinterface = getperinterfacemetrics()

    conglomerates = [ "irq" ]

    # The ib and ib_ext counters are known to be incorrect on all tacc_stats systems
    ignorelist = [ "ib", "ib_ext", "intel_knl_mc_dclk", "intel_knl_mc_uclk" ]

    # nfs metrics take up alot of space
    ignorelist.append("nfs")
    ignorelist.append("irq")

    # proc metrics are handled by dedicated proc code
    ignorelist.append("proc")

    logging.debug("ID: %s", j.acct['id'])

    walltime = max(j.end_time - j.start_time, 0)

    if len(j.times) == 0:
        summaryDict['Error'].append("No timestamp records")
        statsOk = False

    if j.hosts.keys():
        summaryDict['nHosts'] = len(j.hosts)
    else:
        summaryDict['nHosts'] = 0
        summaryDict['Error'].append('No Host Data')

    if 0 == walltime:
        summaryDict['Error'].append('Walltime is 0')

    metrics = {}
    for t in j.schemas.keys():
        metrics[t] = []
        if t == 'cpu':
            metrics[t].append('all')
        for m in j.schemas[t]:
            metrics[t].append(m)

    indices = {}
    totals = {}
    series = {}  # we keep the time series data here, because we need to calculate min/max/median & 1/2/3/4th order of moments
    enties = {}
    isevent = {}

    for metricname, metric in metrics.iteritems():
        indices[metricname] = {}
        isevent[metricname] = {}
        totals[metricname] = {}
        series[metricname] = {}
        enties[metricname] = {}
        for interface in metric:
            try:
                if interface in j.get_schema(metricname):
                    indices[metricname][interface] = j.get_schema(metricname)[interface].index
                    isevent[metricname][interface] = j.get_schema(metricname)[interface].is_event
            except:
                logging.error("summary metric %s not in the schema", str(interface))
                logging.error("%s", sys.exc_info()[0])
                logging.error("%s", traceback.format_exc())
                summaryDict['Error'].append('summary metric ' + str(interface) + ' not in the schema')

    nHosts = 0
    corederived = { "cpicore": [], "cpiref": [], "cpldref": [] }
    nodederived = {'maxmem': [], 'maxmemminus': [], 'maxMemBytes': [], 'maxMemMinusBytes': []}
    socketderived = { "membw": [] }

    totaltimes = []
    starttimes = []
    endtimes = []

    # Naming convention:
    #  metricname - the name of the metric (such as cpu, mem etc).
    #  interface  - the interface exposed for the metric (such as user, system)
    #  device     - the name of the device (ie cpu0, numanode0, eth0 )
    tacc_version = []
    cpus_combined = False

    for host in j.hosts.itervalues():  # for all the hosts present in the file
        nHosts += 1
        nCoresPerSocket = 1
        hostwalltime = host.times[-1] - host.times[0]

        totaltimes.append(hostwalltime - walltime)
        starttimes.append(host.times[0] - j.start_time)
        endtimes.append(host.times[-1] - j.end_time)

        if not host.tacc_version in tacc_version:
            tacc_version.append(host.tacc_version)

        if abs(hostwalltime - walltime) > TIMETHRESHOLD:
            summaryDict['Error'].append("Large discrepency between job account walltime and tacc_stats walltime for {}. {} != {}.".format(host.name, walltime, hostwalltime) )

        if hostwalltime < MINTIMEDELTA:
            summaryDict['Error'].append("Insufficient data points for host {}. {}".format(host.name, host.times) )
            continue
        
        if 'cpu' in host.stats.keys() and 'mem' \
          in host.stats.keys():
            nCoresPerSocket = len(host.stats['cpu']) \
              // len(host.stats['mem'])

        if 'cpu' in host.stats.keys():
            cpukeys = host.stats['cpu'].keys()
            if len(cpukeys) == 1 and '-' in cpukeys:
                cpus_combined = True


        hostmemory = {}

        for metricname in indices.keys():
            if metricname in ignorelist:
                continue
            if metricname not in host.stats.keys():
                continue

            for device in host.stats[metricname].keys():
                for interface, index in indices[metricname].iteritems():

                    if isevent[metricname][interface]:
                        # Counter-type metrics get converted into average rates

                        if metricname in perinterface:
                            # Generate per-interface values
                            if interface not in totals[metricname]:
                                totals[metricname][interface] = []

                            totals[metricname][interface].append( host.stats[metricname][device][-1,index] / hostwalltime )
                        else:
                            # Generate values for all enties
                            if interface not in totals[metricname]:
                                totals[metricname][interface] = {}
                            if device not in totals[metricname][interface]:
                                totals[metricname][interface][device] = []
                            
                            totals[metricname][interface][device].append( host.stats[metricname][device][-1,index] / hostwalltime  )
                    else:
                        # Instantaneous metrics have all timeseries values processed except
                        # the first and last
                        ndatapoints = len(host.stats[metricname][device][:,index])
                        if ndatapoints > 2:
                            end = ndatapoints - 1
                        else:
                            end = ndatapoints

                        data = host.stats[metricname][device][1:ndatapoints,index]

                        # Special case - memory is raw per node, but averaged per core
                        if metricname == "mem":
                            data = numpy.array(data / nCoresPerSocket)

                        if metricname in perinterface:
                            addtoseries(interface, series[metricname], enties[metricname], data)
                        else:
                            # Generate values for all enties
                            if interface not in series[metricname]:
                                series[metricname][interface] = {}
                                enties[metricname][interface] = {}
                            if device not in series[metricname][interface]:
                                series[metricname][interface][device] = data
                                enties[metricname][interface][device] = 1
                            else:
                                series[metricname][interface][device] += data
                                enties[metricname][interface][device] += 1
                # end for interface, index in indices[metricname].iteritems()

                # Special cases
                if metricname == "cpu":
                    if "all" not in totals["cpu"]:
                        totals["cpu"]["all"] = []
                    totals["cpu"]["all"].append( sum( 1.0 * host.stats[metricname][device][-1,:] / hostwalltime) )

                elif metricname == "intel_snb" or metricname == "intel_hsw" or metricname == "intel_ivb":
                    if metricname not in j.overflows:
                        compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_CORE', 'INSTRUCTIONS_RETIRED', corederived["cpicore"])
                        compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_REF', 'INSTRUCTIONS_RETIRED', corederived["cpiref"])
                        compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_REF', 'LOAD_L1D_ALL', corederived["cpldref"])

                elif metricname == "intel_knl" or metricname == "intel_skx":
                    if metricname not in j.overflows:
                        compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_CORE', 'INSTRUCTIONS_RETIRED', corederived["cpicore"])
                        compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_REF', 'INSTRUCTIONS_RETIRED', corederived["cpiref"])

                elif metricname == "intel_pmc3":
                    compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_CORE', 'INSTRUCTIONS_RETIRED', corederived["cpicore"])
                    compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_REF', 'INSTRUCTIONS_RETIRED', corederived["cpiref"])
                    compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_REF', 'MEM_LOAD_RETIRED_L1D_HIT', corederived["cpldref"])

                elif metricname == "intel_4pmc3" or metricname == 'intel_8pmc3':
                    compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_CORE', 'INSTRUCTIONS_RETIRED', corederived["cpicore"])
                    compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_REF', 'INSTRUCTIONS_RETIRED', corederived["cpiref"])
                    compute_ratio(host.stats[metricname][device], indices[metricname], 'CLOCKS_UNHALTED_REF', 'LOAD_L1D_ALL', corederived["cpldref"])

                elif metricname == "intel_snb_imc" or metricname == "intel_skx_imc" or metricname == "intel_hsw_imc" or metricname == "intel_ivb_imc" or metricname == "intel_knl_mc_dclk":
                    if metricname not in j.overflows:
                        compute_sum(host.stats[metricname][device], indices[metricname], 'CAS_READS', 'CAS_WRITES', socketderived["membw"], hostwalltime / 64.0 )

                elif metricname == "mem":
                    if 'MemUsed' in indices[metricname] and 'FilePages' in indices[metricname] and 'Slab' in indices[metricname]:

                        muindex = indices[metricname]['MemUsed']
                        fpindex = indices[metricname]['FilePages']
                        slindex = indices[metricname]['Slab']

                        ndatapoints = len(host.stats[metricname][device][:,muindex])
                        if ndatapoints > 2:
                            end = ndatapoints - 1
                        else:
                            end = ndatapoints

                        memstat = (host.stats[metricname][device][1:ndatapoints,muindex] - \
                                host.stats[metricname][device][1:ndatapoints,fpindex] - \
                                host.stats[metricname][device][1:ndatapoints,slindex] ) / nCoresPerSocket

                        addtoseries("used_minus_diskcache", series[metricname], enties[metricname], memstat)

                        addtoseries('hosttotal', hostmemory, enties[metricname], host.stats[metricname][device][1:ndatapoints,indices['mem']['MemTotal']])
                        addtoseries('hostused',  hostmemory, enties[metricname], host.stats[metricname][device][1:ndatapoints, muindex])
                        addtoseries('hostusedminus',  hostmemory, enties[metricname], memstat * nCoresPerSocket)

            # end for device

        # end loop over interfaces

        if 'hostused' in hostmemory:
            nodederived['maxmem'].append(numpy.amax(hostmemory['hostused'] * 1.0 / hostmemory['hosttotal']))
            nodederived['maxmemminus'].append(numpy.amax(hostmemory['hostusedminus'] * 1.0 / hostmemory['hosttotal']))
            nodederived['maxMemBytes'].append(numpy.amax(hostmemory['hostused']))
            nodederived['maxMemMinusBytes'].append(numpy.amax(hostmemory['hostusedminus']))

    # end loop over hosts

    if 'cpu' not in totals or 'all' not in totals['cpu']:
        statsOk = False
        summaryDict['Error'].append( "No CPU information" )

    if 'intel_knl' in totals and 'CLOCKS_UNHALTED_REF' in totals['intel_knl']:
        if numpy.max(totals['intel_knl']['CLOCKS_UNHALTED_REF']) > (j.end_time - j.start_time)* 1.0e9 * 10:
            statsOk = False
            summaryDict['Error'].append( "Corrupt H/W counters")

    # Change series values into per entity values e.g. Memory per node or IO per node
    for metricname, ifstats in series.iteritems():
        for interface, devstats in ifstats.iteritems():
            if isinstance(devstats, dict):
                for devname, dstats in devstats.iteritems():
                    dstats /= enties[metricname][interface][devname]
            else:
                devstats /= enties[metricname][interface]

    if statsOk:

        # cpu usage
        totalcpus = numpy.array(totals['cpu']['all'])
        summaryDict['cpuall'] = calculate_stats(totalcpus)

        if cpus_combined == False and (summaryDict['cpuall']['med'] > 105.0 or summaryDict['cpuall']['med'] < 90.0):
            summaryDict['Error'].append("Corrupt CPU counters")
            statsOk = False
        else:
            # Effective CPUS defined as those cores where the average activity was higher
            # than 5%
            effective = (numpy.array(totals['cpu']['idle']) / totalcpus) < 0.95

            for interface, cdata in totals['cpu'].iteritems():
                if interface != "all":
                    ncdata = numpy.array(cdata) / totalcpus
                    v = calculate_stats(ncdata)
                    addmetrics(summaryDict,j.overflows, "cpu", interface, v)

                    eff = calculate_stats(numpy.compress(effective, ncdata))
                    addmetrics(summaryDict,j.overflows, "cpueff", interface, eff)

    timeseries = None
    timedata = None
    if statsOk:
        ttt = TimeSeriesSummary(cpus_combined)
        timeseries = ttt.process(j,indices)
        timedata = gentimedata(j, indices, ignorelist, isevent)

    if statsOk:
        for mname, mdata in corederived.iteritems():
            # Store CPI per core
            if len(mdata) > 0:
                summaryDict[mname] = calculate_stats(mdata)
                if len(mdata) <= len( totals['cpu']['all'] ):
                    summaryDict[mname]['error'] = 2
                    summaryDict[mname]['error_msg'] = 'Not all cores have counters'

        for mname, mdata in socketderived.iteritems():
            # Store socket derived metrics
            if len(mdata) > 0:
                summaryDict[mname] = calculate_stats(mdata)

        for mname, mdata in nodederived.iteritems():
            if len(mdata) > 0:
                summaryDict[mname] = calculate_stats(mdata)

        # flops
        if 'intel_snb' in totals.keys():

            if 'ERROR' not in totals['intel_snb']:
                if 'SSE_DOUBLE_ALL' in totals['intel_snb'] and 'SIMD_DOUBLE_256' in totals['intel_snb']:
                    flops = 4.0 * numpy.array(totals['intel_snb']['SIMD_DOUBLE_256']) + 2.0 * numpy.array(totals['intel_snb']['SSE_DOUBLE_ALL'])
                    summaryDict['FLOPS'] = calculate_stats(flops)
                elif 'SSE_DOUBLE_SCALAR' in totals['intel_snb'] and 'SSE_DOUBLE_PACKED' in totals['intel_snb'] and 'SIMD_DOUBLE_256' in totals['intel_snb']:
                    flops = 4.0 * numpy.array(totals['intel_snb']['SIMD_DOUBLE_256']) + 2.0 * numpy.array(totals['intel_snb']['SSE_DOUBLE_PACKED']) + numpy.array(totals['intel_snb']['SSE_DOUBLE_SCALAR'])
                    summaryDict['FLOPS'] = calculate_stats(flops)
            else:
                summaryDict['FLOPS'] = { 'error': 2, "error_msg": 'Counters were reprogrammed during job' }

        # TODO Nehalem/Westmere flops


        # TODO - make this stuff configurable
        if 'lnet' in totals.keys() and 'rx_bytes' in totals['lnet'] and '-' in totals['lnet']["rx_bytes"]:
            if 'ib_sw' in totals.keys() and "rx_bytes" in totals['ib_sw'] and 'mlx4_0/1' in totals['ib_sw']["rx_bytes"]:
                if len(totals['ib_sw']["rx_bytes"]['mlx4_0/1']) == len(totals['lnet']["rx_bytes"]['-']):
                    mpitraff = numpy.array(totals['ib_sw']["rx_bytes"]['mlx4_0/1']) -  numpy.array(totals['lnet']["rx_bytes"]['-'])
                    stats = calculate_stats(mpitraff)
                    if stats['min'] < 0.0:
                        summaryDict['mpirx'] = { 'error': 2, 'error_msg': 'lnet counts exceed ib counts' }
                    else:
                        summaryDict['mpirx'] = calculate_stats(mpitraff);
                else:
                    summaryDict['mpirx'] = { 'error': 2, 'error_msg': 'missing ib_sw or lnet data points' }

        del totals['cpu']

        converttooutput(series, summaryDict, j)
        converttooutput(totals, summaryDict, j)

        summaryDict['analysis'] = {}
        summaryDict['analysis']['catastrophe'] = compute_catastrophe(j)

    # add in lariat data
    if lariatcache != None:
        lariatdata = lariatcache.find(j.id, j.acct['start_time'], j.acct['end_time'])
        if lariatdata != None:
            summaryDict['lariat'] = lariatdata
        else:
            summaryDict['Error'].append("Lariat data not found")

    # add hosts
    summaryDict['hosts'] = []
    for i in j.hosts.keys():
        summaryDict['hosts'].append(i.encode('ascii', 'ignore') if type(i) == unicode else i)

    summaryDict['collection_sw'] = "tacc_stats " + " ".join(tacc_version)

    # add account info from slurm accounting files
    summaryDict['acct'] = fix_unicode(j.acct)

    # add schema outline
    if statsOk and not COMPACT_OUTPUT:
        summaryDict['schema'] = {}
        try:
            for k in metrics:
                for l in metrics[k]:
                    if l in j.get_schema(k):
                        if k not in summaryDict['schema']:
                            summaryDict['schema'][k]={}
                        summaryDict['schema'][k][l] = str( j.get_schema(k)[l] )
        except:
            if (summaryDict['nHosts'] != 0):
                logging.error('%s', sys.exc_info()[0])
                logging.error('%s', traceback.format_exc())
                summaryDict['Error'].append("schema data not found")

    summaryDict['summary_version'] = SUMMARY_VERSION
    summaryDict['created'] = datetime.datetime.utcnow()

    uniq = str( j.acct['local_jobid'] if 'local_jobid' in j.acct else j.acct['id'])
    if 'cluster' in j.acct:
        uniq += "-" + j.acct['cluster']
    if 'job_array_index' in j.acct:
        uniq += "-" + j.acct['job_array_index']
    uniq += "-" + str(j.acct['end_time'])

    summaryDict['_id'] = uniq

    if len(summaryDict['Error']) == 0:
        del summaryDict['Error']

    # Process procDump information from the tacc_stats file itself
    taccproc = TaccProcDump()
    pl = taccproc.getproclist(j, int(j.acct['uid']) if 'uid' in j.acct and (isinstance(j.acct['uid'], (int, long)) or j.acct['uid'].isdigit()) else None)

    if len(pl) > 0:
        summaryDict['procDump'] = pl

    if walltime > 0 and len(totaltimes) > 0:
        summaryDict['timeoffset'] = { 'total': calculate_stats(totaltimes), 'start': calculate_stats(starttimes), 'end': calculate_stats(endtimes) }

    if timeseries != None:
        timeseries['_id'] = uniq

    if timedata != None:
        summaryDict['timedata'] = timedata 

    return (summaryDict, timeseries)

if __name__ == '__main__':
    pass
