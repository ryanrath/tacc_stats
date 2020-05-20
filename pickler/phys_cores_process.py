# Post processing to map virtual CPU cores to physical cores
import numpy
import os

def intel_skx_map(virtcore):
    """ return the physical core index given the (virtual) cpu number """
    return virtcore % 48

def intel_skx_rescale(a, idleidx):

    totalticks = sum(a)
    if totalticks == 0:
        # has been seen in the data
        return a

    idle = a[idleidx] / sum(a)

    if idle > 0.5:
        a[idleidx] -= numpy.uint64(0.5 * sum(a))
    else:
        # total counts
        newticks = 0.5 * sum(a)

        # Set idle to zero and preserve the relative proportions of the other counters
        a[idleidx] = numpy.uint64(0)
        nonidleticks = sum(a)
        a = numpy.uint64(a * newticks / nonidleticks)

    return a

def intel_knl_map(virtcore):
    """ return the physical core index given the (virtual) cpu number """
    return virtcore % 68

def intel_knl_rescale(a, idleidx):

    totalticks = sum(a)
    if totalticks == 0:
        # has been seen in the data
        return a

    idle = a[idleidx] / sum(a)

    if idle > 0.75:
        a[idleidx] -= numpy.uint64(0.75 * sum(a))
    else:
        # total counts
        newticks = 0.25 * sum(a)

        # Set idle to zero and preserve the relative proportions of the other counters
        a[idleidx] = numpy.uint64(0)
        nonidleticks = sum(a)
        a = numpy.uint64(a * newticks / nonidleticks)

    return a

def process_job(job):
    if 'cpu' not in job.schemas:
        return

    for host in job.hosts.itervalues():
        if 'cpu' not in host.stats:
            continue

        cpustats = host.stats['cpu']

        if len(cpustats) == 272:
            output = {}
            for cpuidx, data in cpustats.iteritems():
                realidx = str(intel_knl_map(int(cpuidx)))
                if realidx not in output:
                    output[realidx] = data
                else:
                    output[realidx] += data

            cpuschema = job.get_schema('cpu')
            cpuidle = cpuschema['idle'].index

            for key in output.keys():
                if len(output[key][:, ]) > 1:
                    rates = numpy.diff(output[key], 1, 0)
                    scaled_rates = numpy.apply_along_axis(intel_knl_rescale, 1, rates, cpuidle)
                    output[key] = numpy.concatenate(( (output[key][0], ), scaled_rates), 0).cumsum(0)

            host.stats['cputhreads'] = host.stats['cpu']
            job.get_schema('cputhreads', cpuschema.desc)
            host.stats['cpu'] = output

        if len(cpustats) == 96:
            output = {}
            for cpuidx, data in cpustats.iteritems():
                realidx = str(intel_skx_map(int(cpuidx)))
                if realidx not in output:
                    output[realidx] = data
                else:
                    output[realidx] += data

            cpuschema = job.get_schema('cpu')
            cpuidle = cpuschema['idle'].index

            for key in output.keys():
                if len(output[key][:, ]) > 1:
                    rates = numpy.diff(output[key], 1, 0)
                    scaled_rates = numpy.apply_along_axis(intel_skx_rescale, 1, rates, cpuidle)
                    output[key] = numpy.concatenate(( (output[key][0], ), scaled_rates), 0).cumsum(0)

            host.stats['cputhreads'] = host.stats['cpu']
            job.get_schema('cputhreads', cpuschema.desc)
            host.stats['cpu'] = output
