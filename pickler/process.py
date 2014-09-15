#!/usr/bin/env python
import job_stats
import batch_acct
import account
import summarize
import sys
import time
import datetime
from pymongo import MongoClient
from pymongo.errors import InvalidDocument
from multiprocessing import Process
import socket

PROCESS_VERSION = 4
verbose = False

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
                    sys.stderr.write("{} Instance {} Processed {} records in {} seconds ({} per second)\n".format( 
                        datetime.datetime.utcnow().isoformat(), self.procid, self.count, diff, self.rate ))

        self.count += 1

    def rate(self):
        return self.rate

def createsummary(totalprocs, procid):

    sys.stderr.write("{} Processor {} of {} starting\n".format(datetime.datetime.utcnow().isoformat(), procid, totalprocs))
    referencetime = int(time.time()) - ( 3 * 24 * 3600 ) 

    config = account.getconfig()
    dbconf = config['accountdatabase']
    outdbconf = config['outputdatabase']

    outclient = MongoClient(host=outdbconf['dbhost'])
    outdb = outclient[outdbconf['dbname'] ]

    ratecalc = RateCalculator(procid)
    timewindows = dict()

    for resourcename, settings in config['resources'].iteritems():

        if 'enabled' in settings:
            if settings['enabled'] == False:
                continue

        processtimes = { "mintime": 2**64, "maxtime": 0 }

        dbreader = account.DbAcct( settings['resource_id'], dbconf, PROCESS_VERSION, totalprocs, procid)

        bacct = batch_acct.factory(settings['batch_system'], settings['acct_path'], settings['host_name_ext'] )

        if settings['lariat_path'] != "":
            lariat = summarize.LariatManager(settings['lariat_path'])
        else:
            lariat = None

        dbwriter = account.DbLogger( dbconf["dbname"], dbconf["tablename"], dbconf["defaultsfile"] )

        for acct in dbreader.reader():
            if verbose:
                sys.stderr.write( "{} local_job_id = {}\n".format(datetime.datetime.utcnow().isoformat(), acct['id']) )
            job = job_stats.from_acct( acct, settings['tacc_stats_home'], settings['host_list_dir'], bacct )
            summary,timeseries = summarize.summarize(job, lariat)

            if summary['complete'] == False and summary["acct"]['end_time'] > referencetime:
                # Do not mark incomplete jobs as done unless they are older than the
                # reference time (which defaults to 3 days ago)
                continue

            summaryOk = False
            outdb[resourcename].update( {"_id": summary["_id"]}, summary, upsert=True )

            if outdb[resourcename].find_one( {"_id": summary["_id"], "summary_version": summary["summary_version"] }, { "_id":1 } ) != None:
                summaryOk = True

            timeseriesOk = False
            if timeseries != None:
                # If the timeseries data is present then it must got into the db
                try:
                    outdb["timeseries-" + resourcename].update( {"_id":timeseries["_id"]}, timeseries, upsert=True )
                    if outdb["timeseries-" + resourcename].find_one( {"_id": timeseries["_id"]}, { "_id":1 } ) != None:
                        timeseriesOk = True
                except InvalidDocument as e:
                    sys.stderr.write("Error inserting document {}\n".format(summary["_id"]) )
                    timeseriesOk = False
            else:
                timeseriesOk = True

            if summaryOk and timeseriesOk:
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

    sys.stderr.write("{} Processor {} of {} exiting. Processed {}\n".format(datetime.datetime.utcnow().isoformat(), procid, totalprocs, ratecalc.count))

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

    try:
        outdb["journal"].insert( report )
    except Exception as e:
        sys.stderr.write("Error inserting report. Error: {}\n{}\n".format(e, report) )


def main():

    if len(sys.argv) == 1:
        print "Usage: " + sys.argv[0] + " [N SUBPROCESSES] [TOTAL INSTANCES] [INSTANCE ID]"
        sys.exit(1)

    nprocs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    total_instances = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    instance_id = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    total_procs = nprocs * total_instances

    if nprocs == 1:
        createsummary(None, None)
    else:
        proclist = []
        for procid in xrange(nprocs):
            p = Process( target=createsummary, args=(total_procs, (instance_id*nprocs) + procid) )
            p.start()
            proclist.append(p)

        for proc in proclist:
            p.join()

if __name__ == '__main__': 
    main()
