#!/usr/bin/env python
import job_stats
import batch_acct
import account
import summarize
import sys
import time
import datetime
import socket
from getopt import getopt
import logging
import output
import os
import re

from mpi4py import MPI

PROCESS_VERSION = 4

def parsetime(strtime):
    """ Try to be flexible in the time formats supported:
           1) unixtimestamp prefixed with @
           2) year-month-day zero-padded
           3) year-month-day hour:minute:second zero padded optional T between date and time
           4) locale specific format
    """
    m = re.search(r"^@(\d*)$", strtime)
    if m:
        return datetime.datetime.fromtimestamp(int(m.group(1)))
    if re.search(r"^\d{4}-\d{2}-\d{2}$", strtime):
        return datetime.datetime.strptime(strtime, "%Y-%m-%d")
    m = re.search(r"^(\d{4}-\d{2}-\d{2}).(\d{2}:\d{2}:\d{2})$", strtime)
    if m:
        return datetime.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S")

    return datetime.datetime.strptime(strtime, "%c")

class RateCalculator:
    def __init__(self, procid):
        self.count = 0
        self.starttime = 0
        self.rate = 0
        self.procid = procid

    def increment(self):
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

    def rate(self):
        return self.rate

def createsummary(options, totalprocs, procid):

    procidstr = "%s of %s " % (procid, totalprocs) if totalprocs != None else ""

    logging.info("Processor " + procidstr + "starting")

    referencetime = int(time.time()) - ( 3 * 24 * 3600 ) 

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

        if options['start'] == None:
            dbreader = account.DbAcct( settings['resource_id'], dbconf, PROCESS_VERSION, totalprocs, procid, options['localjobid'])
        else:
            # Choose a process version that doesn't exist so that all jobs are selected
            dbreader = account.DbAcct( settings['resource_id'], dbconf, PROCESS_VERSION + 1, totalprocs, procid, None)

        bacct = batch_acct.factory(settings['batch_system'], settings['acct_path'], settings['host_name_ext'] )

        if settings['lariat_path'] != "":
            lariat = summarize.LariatManager(settings['lariat_path'])
        else:
            lariat = None

        dbwriter = account.DbLogger( dbconf["dbname"], dbconf["tablename"], dbconf["defaultsfile"] )

        for acct in dbreader.reader(options['start'], options['end']):
            logging.debug("%s local_job_id = %s", resourcename, acct['id'])
            job = job_stats.from_acct( acct, settings['tacc_stats_home'], settings['host_list_dir'], bacct )
            summary,timeseries = summarize.summarize(job, lariat)

            if summary['complete'] == False and summary["acct"]['end_time'] > referencetime:
                # Do not mark incomplete jobs as done unless they are older than the
                # reference time (which defaults to 3 days ago)
                continue

            insertOk = outdb.insert(resourcename, summary, timeseries)
            
            if insertOk:
                dbwriter.logprocessed( acct, settings['resource_id'], PROCESS_VERSION )
                processtimes['mintime'] = min( processtimes['mintime'], summary["acct"]['end_time'] )
                processtimes['maxtime'] = max( processtimes['maxtime'], summary["acct"]['end_time'] )
                ratecalc.increment()
            else:
                # Mark as negative process version to indicate that it has been processed
                # but no summary was output
                dbwriter.logprocessed( acct, settings['resource_id'], 0 - PROCESS_VERSION )

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
            "records": ratecalc.count
            }

    report = { "proc": proc, "resources": timewindows }

    outdb.logreport(report)

def usage():
    """ print usage """
    print "usage: {0} [OPTS]".format(os.path.basename(__file__))
    print "  -r --resource=RES     process only jobs for the specified resource,"
    print "                        if absent then all resources are processed"
    print "  -l --localjobid=JOBID process only the job with the specified id"
    print "                        this option requires the resource to be specified"
    print "  -c --config=PATH      specify the path to the configuration directory"
    print "  -s --start TIME       process all jobs that ended after the provided start"
    print "                        time (an end time must also be specified)"
    print "  -e --end TIME         process all jobs that ended before the provided end"
    print "                        time (a start time must also be specified)"
    print "  -d --debug            set log level to debug"
    print "  -q --quiet            only log errors"
    print "  -h --help             print this help message"

def getoptions():
    """ process comandline options """

    retdata = {
        "log": logging.INFO,
        "resource": None,
        "localjobid": None,
        "config": None,
        "start": None,
        "end": None
    }

    opts, args = getopt(sys.argv[1:], "r:l:c:s:e:dqh", ["resource=", "localjobid=", "config=", "start=", "end=", "debug", "quiet", "help"])

    for opt in opts:
        if opt[0] in ("-r", "--resource"):
            retdata['resource'] = opt[1]
        elif opt[0] in ("-l", "--localjobid"):
            retdata['localjobid'] = opt[1]
        elif opt[0] in ("-d", "--debug"):
            retdata['log'] = logging.DEBUG
        elif opt[0] in ("-q", "--quiet"):
            retdata['log'] = logging.ERROR
        elif opt[0] in ("-c", "--config"):
            retdata['config'] = opt[1]
        elif opt[0] in ("-s", "--start"):
            retdata['start'] = (parsetime(opt[1]) - datetime.datetime(1970, 1, 1)).total_seconds()
        elif opt[0] in ("-e", "--end"):
            retdata['end'] = (parsetime(opt[1]) - datetime.datetime(1970, 1, 1)).total_seconds()
        elif opt[0] in ("-h", "--help"):
            usage()
            sys.exit(0)

    retdata['nprocs'] = int(args[0]) if len(args) > 0 else 1
    retdata['total_instances'] = int(args[1]) if len(args) > 1 else 1
    retdata['instance_id'] = int(args[2]) if len(args) > 2 else 0

    if retdata['start'] != None and retdata['end'] == None or retdata['start'] == None and retdata['end'] != None:
        usage()
        sys.exit(1)

    return retdata

def setuplogger(consolelevel, filename=None, filelevel=None):
    """ setup the python root logger to log to the console with defined log
        level. Optionally also log to file with the provided level """

    if filelevel == None:
        filelevel = consolelevel

    if sys.version.startswith("2.7"):
        logging.captureWarnings(True)

    rootlogger = logging.getLogger()
    rootlogger.setLevel(min(consolelevel, filelevel))

    formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

    if filename != None:
        filehandler = logging.FileHandler(filename)
        filehandler.setLevel(filelevel)
        filehandler.setFormatter(formatter)
        rootlogger.addHandler(filehandler)

    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(consolelevel)
    consolehandler.setFormatter(formatter)
    rootlogger.addHandler(consolehandler)

def main():

    comm = MPI.COMM_WORLD

    options = getoptions()

    setuplogger(logging.ERROR, "./logs/summary_" + str(comm.Get_rank()) + ".log", options['log'])

    createsummary(options, comm.Get_size(), comm.Get_rank())

if __name__ == '__main__': 
    main()
