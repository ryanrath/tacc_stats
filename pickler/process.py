#!/usr/bin/env python
import warnings
import job_stats
import batch_acct
import account
import summarize
import sys
import time
from multiprocessing import Process
import socket
from getopt import getopt
import logging
import output
import os

from scripthelpers import setuplogger
from journal import Journal

PROCESS_VERSION = 4
ERROR_INCOMPLETE = -1001


class RateCalculator:
    def __init__(self, procid):
        self.count_good = 0
        self.count = 0
        self.starttime = 0
        self.rate = 0
        self.procid = procid

    def increment(self, isGood):
        if self.count == 0:
            self.starttime = time.time()
        else:
            diff = time.time() - self.starttime
            if diff > 0:
                self.rate = self.count * 1.0 / diff

                if (self.count % 20) == 0:
                    logging.info("Instance %s Processed %s records in %s seconds (%s per second)",
                                 self.procid, self.count, diff, self.rate)

        self.count += 1
        if isGood:
            self.count_good += 1

    def rate(self):
        return self.rate


def construct_host_list(acct):
    """
    When working with OpenXDMoD information we do not have a `host_list_dir` as the hosts are included in the slurm
    accounting information as the `node_list` property. This property is provided in the form:
    {
        "node_list": "c105-[013-014,021-022,031-034,041,071-074,081]"
    }
    """
    if 'node_list' not in acct:
        return

    hosts = []
    node_list = acct['node_list']

    # it's possible that there were no nodes assigned to the job
    if 'None assigned' in node_list:
        hosts.append('None assigned')
        return hosts

    # this covers the format: c105-[013-014,021-022,031-034,041,071-074,081]
    if '[' in node_list and ']' in node_list:
        left_bracket = node_list.find('[')
        right_bracket = node_list.find(']')

        # everything to the left of the left bracket is the host
        host = node_list[:left_bracket - 1]

        # everything between the brackets are the nodes
        nodes = (node_list[left_bracket + 1:right_bracket]).split(',')

        for node in nodes:

            # if this is a range of nodes then we need to ensure there is one entry per value in the range.
            if '-' in node:
                delim_idx = node.find('-')
                start = int(node[:delim_idx])
                end = int(node[delim_idx + 1:])
                for num in range(start, end + 1):
                    hosts.append("%s-%s" % (host, num))
            else:
                hosts.append("%s-%s" % (host, node))
    else:
        hosts.append(node_list)

    return hosts


def createsummary(options, totalprocs, procid):

    procidstr = "%s of %s " % (procid, totalprocs) if totalprocs != None else ""

    logging.info("Processor " + procidstr + "starting")

    referencetime = int(time.time()) - ( 7 * 24 * 3600 ) 

    config = account.getconfig(options['config'])
    dbconf = config['accountdatabase']

    outdb = output.factory(config['outputdatabase'])

    ratecalc = RateCalculator(procid)
    timewindows = dict()

    for resourcename, settings in config['resources'].iteritems():

        if 'enabled' in settings:
            if settings['enabled'] == False:
                continue

        if options['resource'] not in (None, resourcename, str(settings['resource_id'])):
            continue

        processtimes = { "mintime": 2**64, "maxtime": 0 }

        dbreader = account.DbAcct( settings['resource_id'], dbconf, PROCESS_VERSION, totalprocs, procid, options['localjobid'], options['large_jobs'], options['small_jobs'])

        bacct = batch_acct.factory(settings['batch_system'], settings['acct_path'], settings['host_name_ext'] )

        if 'lariat_path' in settings and settings['lariat_path'] != "":
            lariat = summarize.LariatManager(settings['lariat_path'])
        else:
            lariat = None

        dbwriter = account.DbLogger( dbconf["dbname"], dbconf["tablename"], dbconf["defaultsfile"] )

        for acct in dbreader.reader():
            logging.debug("%s local_job_id = %s", resourcename, acct['id'])
            acct['host_list'] = construct_host_list(acct)
            job = job_stats.from_acct( acct, settings['tacc_stats_home'], settings['host_list_dir'] if 'host_list_dir' in settings else None, bacct)
            summary,timeseries = summarize.summarize(job, lariat)

            insertOk = outdb.insert(resourcename, summary, timeseries)

            if summary['complete'] == False and summary["acct"]['end_time'] > referencetime:
                # Do not mark incomplete jobs as done unless they are older than the
                # reference time (which defaults to 7 days ago)
                dbwriter.logprocessed(acct, settings['resource_id'], ERROR_INCOMPLETE)
                ratecalc.increment(False)
                continue
            
            if insertOk:
                dbwriter.logprocessed( acct, settings['resource_id'], PROCESS_VERSION )
                processtimes['mintime'] = min( processtimes['mintime'], summary["acct"]['end_time'] )
                processtimes['maxtime'] = max( processtimes['maxtime'], summary["acct"]['end_time'] )
                ratecalc.increment(True)
            else:
                # Mark as negative process version to indicate that it has been processed
                # but no summary was output
                dbwriter.logprocessed( acct, settings['resource_id'], 0 - PROCESS_VERSION )
                ratecalc.increment(False)

        if processtimes['maxtime'] != 0:
            timewindows[resourcename] = processtimes

    logging.info("Processor " + procidstr + "exiting. Processed %s", ratecalc.count)

    if ratecalc.count == 0:
        # No need to generate a report if no docs were processed
        return

    proc = { "host": socket.getfqdn(),
            "instance": procid,
            "totalinstances": totalprocs,
            "start_time": ratecalc.starttime,
            "end_time": time.time() ,
            "rate": ratecalc.rate,
            "records": ratecalc.count,
            "good": ratecalc.count_good
            }

    report = { "proc": proc, "resources": timewindows }

    outdb.logreport(report)

    journal = Journal(config)
    journal.logreport(report)

def usage():
    """ print usage """
    print "usage: {0} [OPTS] [N SUBPROCESSES] [TOTAL INSTANCES] [INSTANCE ID]".format(os.path.basename(__file__))
    print "  -r --resource=RES     process only jobs for the specified resource,"
    print "                        if absent then all resources are processed"
    print "  -l --localjobid=JOBID process only the job with the specified id"
    print "                        this option requires the resource to be specified"
    print "  -c --config=PATH      specify the path to the configuration directory"
    print "  -d --debug            set log level to debug"
    print "  -q --quiet            only log errors"
    print "  -h --help             print this help message"


def getoptions():
    """ process comandline options """

    retdata = {
        "log": logging.INFO,
        "logfile": None,
        "resource": None,
        "localjobid": None,
        "config": None,
        "large_jobs": False,
        "small_jobs": False
    }

    opts, args = getopt(sys.argv[1:], "r:l:c:dqgsho", ["resource=", "logfile=", "localjobid=", "config=", "debug", "quiet", "large", "small", "help"])

    for opt in opts:
        if opt[0] in ("-r", "--resource"):
            retdata['resource'] = opt[1]
        elif opt[0] in ("-l", "--localjobid"):
            retdata['localjobid'] = opt[1]
        elif opt[0] in ("-d", "--debug"):
            retdata['log'] = logging.DEBUG
        elif opt[0] == "--logfile":
            retdata['logfile'] = opt[1]
        elif opt[0] in ("-q", "--quiet"):
            retdata['log'] = logging.ERROR
        elif opt[0] in ("-g", "--large_jobs"):
            retdata["large_jobs"] = True
        elif opt[0] in ("-s", "--small-jobs"):
            retdata["small_jobs"] = True
        elif opt[0] in ("-c", "--config"):
            retdata['config'] = opt[1]
        elif opt[0] in ("-h", "--help"):
            usage()
            sys.exit(0)

    retdata['nprocs'] = int(args[0]) if len(args) > 0 else 1
    retdata['total_instances'] = int(args[1]) if len(args) > 1 else 1
    retdata['instance_id'] = int(args[2]) if len(args) > 2 else 0

    return retdata


def main():

    warnings.filterwarnings("ignore", "Degrees of freedom <= 0 for slice", RuntimeWarning)

    options = getoptions()
    if options['small_jobs'] and options['large_jobs']:
        raise Exception('You can may only specify either small_jobs or large_jobs, not both.')

    setuplogger(options['log'], options['logfile'], logging.INFO)

    total_procs = options['nprocs'] * options['total_instances']
    start_offset = options['instance_id'] * options['nprocs']

    exit_code = 0

    if options['nprocs'] == 1:
        createsummary(options, None, None)
    else:
        proclist = []
        for procid in xrange(options['nprocs']):
            p = Process( target=createsummary, args=(options, total_procs, start_offset + procid) )
            p.start()
            proclist.append(p)

        for proc in proclist:
            proc.join()
            exit_code += proc.exitcode

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
