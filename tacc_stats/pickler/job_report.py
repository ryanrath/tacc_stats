#!/usr/bin/env python
import sys
from pickler import *
import human, job_stats, numpy, signal, string

if __name__ == '__main__':
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

amd64_core_by_dev = False
amd64_sock_by_dev = False

# FIXME jobs with no good hosts may break this.

class Report(object):
    def __init__(self, job):
        self.cols = []
        self.dict = {}
        self.comments = {}
        self.add_info('id', job.id)
        self.add_info('owner', job.acct['owner'])
        self.add_info('queue', job.acct['queue'])
        self.add_info('queue_wait_time', job.start_time - long(job.acct['submission_time']))
        self.add_info('begin', job.start_time, comment=human.ftime(job.start_time))
        self.add_info('end', job.end_time, comment=human.ftime(job.end_time))
        self.add_info('run_time', job.end_time - job.start_time)
        self.add_info('nr_hosts', len(job.hosts))
        self.add_info('nr_slots', long(job.acct['slots']))
        self.add_info('pe', job.acct['granted_pe'])
        self.add_info('failed', job.acct['failed'])
        self.add_info('exit_status', job.acct['exit_status'])
        if amd64_core_by_dev:
            for core in range(0, 16):
                self.add_events(job, 'amd64_core', dev=str(core), keys=['USER', 'SSE_FLOPS', 'DCSF'])
        else:
            self.add_events(job, 'amd64_core', keys=['USER', 'SSE_FLOPS', 'DCSF'])
        if amd64_sock_by_dev:
            for sock in range(0, 4):
                self.add_events(job, 'amd64_sock', dev=str(sock), keys=['DRAM', 'HT0', 'HT1', 'HT2'])
        else:
            self.add_events(job, 'amd64_sock', keys=['DRAM', 'HT0', 'HT1', 'HT2'])
        self.add_events(job, 'cpu', keys=['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq'])
        self.add_events(job, 'llite', dev='/share', keys=['open', 'read_bytes', 'write_bytes'])
        self.add_events(job, 'llite', dev='/work', keys=['open', 'read_bytes', 'write_bytes'])
        self.add_events(job, 'llite', dev='/scratch', keys=['open', 'read_bytes', 'write_bytes'])
        self.add_events(job, 'lnet', keys=['rx_bytes', 'tx_bytes'])
        self.add_events(job, 'ib_sw', keys=['rx_bytes', 'tx_bytes'])
        self.add_events(job, 'net', keys=['rx_bytes', 'tx_bytes'])
        self.add_gauges(job, 'mem', keys=['MemTotal', 'MemUsed', 'FilePages', 'Mapped', 'AnonPages', 'Slab'])
        self.cpu_total = sum(self.dict.get(("cpu", None, key), 0) for key in ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq'])
        # self.add_events(job, 'vm', keys=['pgactivate', 'pgdeactivate'])
        self.add_events(job, 'ps', keys=['ctxt', 'processes'])

    def add_key_val(self, type_name, dev, key, val, comment=None):
        col = (type_name, dev, key)
        self.cols.append(col)
        self.dict[col] = val
        if comment:
            self.comments[col] = comment

    def add_info(self, key, val, comment=None):
        self.add_key_val(None, None, key, val, comment=comment)

    def add_events(self, job, type_name, dev=None, keys=None):
        schema = job.schemas.get(type_name)
        if not schema:
            for key in keys:
                self.add_key_val(type_name, dev, key, None)
            return
        vals = numpy.zeros(len(schema), numpy.uint64)
        for host in job.hosts.itervalues():
            stats = host.stats[type_name]
            if dev:
                vals += stats[dev][-1]
            else:
                for dev_stats in stats.itervalues():
                    vals += dev_stats[-1]
        for key in keys:
            self.add_key_val(type_name, dev, key, vals[schema[key].index])

    def add_gauges(self, job, type_name, dev=None, keys=None):
        schema = job.schemas.get(type_name)
        if not schema:
            for key in keys:
                self.add_key_val(type_name, dev, key, None)
            return
        vals = numpy.zeros(len(schema), numpy.uint64)
        for host in job.hosts.itervalues():
            stats = host.stats[type_name]
            nr_times = len(job.times)
            if dev:
                stats = stats[dev]
            else:
                stats = sum(stats.itervalues()) # Sum over all devices.
            if nr_times == 1 or nr_times == 2:
                vals += stats[-1]
            else:
                vals += sum(stats[1:-1]) / (nr_times - 2) # Interior average.
        for key in keys:
            self.add_key_val(type_name, dev, key, vals[schema[key].index])

    def col_str(self, type_name, dev, key):
        str = ""
        if type_name and type_name not in ["amd64_core", "amd64_sock", "cpu", "llite", "mem"]:
            str += type_name + ":"
        if dev:
            str += dev + ":"
        return str + key

    def print_header(self, **kwargs):
        prefix = kwargs.get('prefix', '+')
        delim = kwargs.get('delim', ' ')
        file = kwargs.get('file')
        header = delim.join(self.col_str(type_name, dev, key) for type_name, dev, key in self.cols)
        print >>file, prefix + header

    def print_record(self, **kwargs):
        prefix = kwargs.get('prefix', '+')
        delim = kwargs.get('delim', ' ')
        file = kwargs.get('file')
        record = delim.join(str(self.dict.get(col, 0)) for col in self.cols)
        print >>file, prefix + record

    def comment(self, type_name, dev, key, val):
        str = self.comments.get((type_name, dev, key))
        if str:
            return " # " + str
        if val == None:
            return ""
        str = ""
        if type_name == "amd64_core":
            str = human.fsize(long(val), align=True, space=" ")
            if key == "DCSF":
                str += "B"
        elif type_name == "amd64_sock":
            str = human.fsize(long(val), align=True, space=" ") + "B"
        elif type_name == "cpu":
            if self.cpu_total == 0:
                pct = 0.0
            else:
                pct = 100.0 * float(val) / float(self.cpu_total)
            str = "%5.2f %%" % pct
        elif type_name == "mem":
            str = human.fsize(long(val), align=True, space=" ") + "B"
            if key == "MemUsed":
                pct = 100.0 * float(val) / float(self.dict[("mem", None, "MemTotal")])
                str += " (%5.2f %%)" % pct
        elif key and key.endswith("_bytes"):
            str = human.fsize(long(val), align=True, space=" ") + "B"
        elif key and key.endswith("_time"):
            str = human.fhms(long(val))
        if str != "":
            str = " # " + str
        return str

    def display(self, **kwargs):
        if kwargs.get('print_header'):
            self.print_header(**kwargs)
        if kwargs.get('print_record'):
            self.print_values(**kwargs)
        file = kwargs.get('file')
        col_width = 24 # max(len(col) for col in self.cols) + 1
        val_width = 20 # max(len(str(val)) for val in self.dict.itervalues()) + 1
        for col in self.cols:
            type_name, dev, key = col
            val = self.dict[col]
            col_str = self.col_str(type_name, dev, key)
            if val != None:
                val_str = str(val)
            else:
                val_str = '-'
            comment = self.comment(type_name, dev, key, val)
            print >>file, (col_str + ' ').ljust(col_width, '.') + \
                  (' ' + val_str).rjust(val_width, '.') + comment


def display(arg, **kwargs):
    """display(arg, file=None, print_header=False, print_record=False, prefix='+', delim=' ')
    """
    if type(arg) is Report:
        report = arg
    elif type(arg) is job_stats.Job:
        report = Report(arg)
    elif type(arg) is int or type(arg) is long or type(arg) is str:
        job = job_stats.from_id(str(arg))
        if not job:
            job_stats.error("no job for id `%s'\n", str(arg))
            return
        report = Report(arg)
    else:
        raise ValueError("cannot convert arg `%s' to Job or Report" % str(arg))
    report.display(**kwargs)


def display_list(lis, **kwargs):
    id_dict = {}
    for arg in lis:
        if type(arg) is Report or type(arg) is job_stats.Job:
            pass
        elif str(arg).isdigit(): # XXX
            id_dict[str(arg)] = None
        else:
            raise ValueError("cannot convert arg `%s' to Job or Report" % str(arg))
    if id_dict:
        sge_acct.fill(id_dict)
    for arg in lis:
        report = None
        if type(arg) is Report:
            report = arg
        elif type(arg) is job_stats.Job:
            report = Report(arg)
        else:
            acct = id_dict[str(arg)]
            if acct:
                job = job_stats.from_acct(acct,os.getenv('TACC_STATS_HOME','/scratch/projects/tacc_stats'))
                report = Report(job)
            else:
                job_stats.error("no accounting data found for job `%s'\n", arg)
        if report:
            report.display(**kwargs)
            kwargs['print_header'] = False


if __name__ == '__main__':
    job_stats.verbose = False
    display_list(argv[1:])
