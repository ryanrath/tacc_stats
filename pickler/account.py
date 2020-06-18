#!/usr/bin/env python

import getopt
import json
import logging
import sys

import MySQLdb as mdb

import batch_acct
from scripthelpers import setuplogger
from summarize import SUMMARY_VERSION

VERSION_NUMBER = 1

class DbInterface:
    def __init__(self, dbname, tablename, mydefaults):

        self.con = mdb.connect(db=dbname, read_default_file=mydefaults)
        self.tablename = tablename
        self.query = "INSERT INTO " + tablename + " (resource_id,job_array_index,local_job_id,start_time_ts,end_time_ts,record,ingest_version) VALUES(%s,%s,%s,%s,%s,COMPRESS(%s)," + str(VERSION_NUMBER) + ") ON DUPLICATE KEY UPDATE ingest_version = VALUES(ingest_version), record = VALUES(record)"
        self.buffered = 0

    def resettable(self,dropexisting = False):
        cur = self.con.cursor()
        if dropexisting:
            cur.execute("DROP TABLE IF EXISTS " + self.tablename )

        cur.execute("CREATE TABLE IF NOT EXISTS " + self.tablename + "(" + \
                "resource_id INT NOT NULL,"  + \
                "local_job_id INT NOT NULL," + \
                "job_array_index SMALLINT(5) NOT NULL DEFAULT '-1'," + \
                "start_time_ts INT NOT NULL," + \
                "end_time_ts INT NOT NULL," + \
                "process_version INT NOT NULL DEFAULT -1," + \
                "process_timestamp TIMESTAMP," + \
                "ingest_version INT NOT NULL," + \
                "summary_version CHAR(8) NOT NULL DEFAULT 'na'," + \
                "record BLOB," + \
                "UNIQUE (resource_id,local_job_id,job_array_index,end_time_ts)," + \
                "INDEX (end_time_ts,resource_id,process_version)," + \
                "INDEX (resource_id,process_version)" + \
                ") " )

    def insert(self, data):
        cur = self.con.cursor()
        try:
            cur.execute(self.query, data)
        except mdb.IntegrityError as e:
            if e[0] != 1062:
                raise e
            # else:
                # Todo - check that the blobs match on duplicate records

        self.buffered += 1
        if self.buffered > 100:
            self.con.commit()
            self.buffered = 0


    def postinsert(self):
        self.con.commit()

    def getmostrecent(self, resource_id):
        query = "SELECT MAX(end_time_ts) FROM " + self.tablename + " WHERE resource_id = %s"
        data = ( resource_id, )
        
        cur = self.con.cursor()
        cur.execute(query, data)
        return cur.fetchone()[0]

class DbLogger(object):
    def __init__(self, dbname, tablename, mydefaults):
        self.con = mdb.connect(db=dbname, read_default_file=mydefaults)
        self.tablename = tablename

    def logprocessed(self, acct, resource_id, version):

        query = "UPDATE " + self.tablename + " SET process_version = %s, summary_version = %s WHERE resource_id = %s AND local_job_id = %s AND job_array_index = %s AND end_time_ts = %s"
        local_jobid = acct['local_jobid'] if 'local_jobid' in acct else acct['id']
        job_array_index = acct['job_array_index'] if 'job_array_index' in acct else -1
        data = ( version, SUMMARY_VERSION, resource_id, local_jobid, job_array_index, acct['end_time'] )

        cur = self.con.cursor()
        cur.execute(query, data)
        self.con.commit()

class DbAcct(object):
    def __init__(self, resource_id, dbconf, process_version, totalprocs = None, procid = None, local_jobid = None, large_jobs = False, small_jobs = False):
        self.con = mdb.connect(db=dbconf['dbname'], read_default_file=dbconf['defaultsfile'])
        self.tablename = dbconf['tablename']
        self.process_version = process_version
        self.resource_id = resource_id
        self.local_jobid = local_jobid
        self.totalprocs = totalprocs
        self.procid = procid
        self.large_jobs = large_jobs
        self.small_jobs = small_jobs

    def jobidreader(self, local_jobid):
        query = "SELECT UNCOMPRESS(record) FROM " + self.tablename + " WHERE resource_id = %s AND local_job_id = %s"
        data = (self.resource_id, local_jobid)
        if self.totalprocs != None and self.procid != None:
            query += " AND (CRC32(local_job_id) %% %s) = %s"
            data = data + ( self.totalprocs, self.procid )
        query += " ORDER BY end_time_ts ASC"

        cur = self.con.cursor()
        cur.execute(query, data)

        for record in cur:
            r = json.loads(record[0])
            yield r

    def generate_time_query(self, start_time=None, end_time=None):
        """
        Generate a query, data tuple based on whether or not the `large_jobs` argument was provided on the command line.

        :param start_time:
        :param end_time:
        :return:
        """
        if not self.large_jobs and not self.small_jobs:
            query = "SELECT UNCOMPRESS(record) FROM " + self.tablename + " WHERE resource_id = %s AND process_version != %s "
            data = ( self.resource_id, self.process_version )
            if start_time != None:
                query += " AND end_time_ts >= %s "
                data = data + ( start_time, )
            if end_time != None:
                query += " AND end_time_ts < %s "
                data = data + ( end_time, )
            if self.totalprocs != None and self.procid != None:
                query += " AND (CRC32(local_job_id) %% %s) = %s"
                data = data + ( self.totalprocs, self.procid )
            query += " ORDER BY end_time_ts ASC"
            return query, data
        else:
            # We're going to be dealing with [small|large]_jobs, "small_jobs" are defined as jobs that ran < 24 hrs and
            # have less then 200 nodes while large jobs are defined as any job that has run over 24 hours. Since we need 
            # to be able to filter on nodes and wall time the sql is slightly more complicated.

            # This query is used to select the initial set of data from accountfact
            initial_data_query = """
                                       SELECT UNCOMPRESS(af.record)                     AS uncompressed,
                                              TIMEDIFF(FROM_UNIXTIME(af.end_time_ts),
                                                       FROM_UNIXTIME(af.start_time_ts)) AS time_diff,
                                              af.end_time_ts,
                                              af.record
                                       FROM {} AS af
                                       WHERE af.process_version != %s
                                         AND af.resource_id = %s
                """.format(self.tablename)

            data = (self.process_version, self.resource_id)
            if start_time is not None:
                initial_data_query += " \t\t\t\t\t\t AND af.end_time_ts >= %s "
                data = data + (start_time,)
            if end_time is not None:
                initial_data_query += "\n \t\t\t\t\t\t\t\t\t AND af.end_time_ts < %s "
                data = data + (end_time,)
            if self.totalprocs is not None and self.procid is not None:
                initial_data_query += "\n AND (CRC32(af.local_job_id) %% %s) = %s"
                data = data + (self.totalprocs, self.procid)

            # This outer query utilizes the initial_data_query to allow us to calculate / filter jobs based on a job_
            # hour statistic
            query = """
                SELECT
                    l3.uncompressed
                FROM (
                     SELECT CAST(
                                    SUBSTR(
                                            l2.uncompressed,
                                            l2.nodes_loc + l2.nodes_len,
                                            LOCATE('"', l2.uncompressed, l2.nodes_loc + l2.nodes_len) -
                                            (l2.nodes_loc + l2.nodes_len)
                                    )
                            AS INTEGER) AS nodes,
                            l2.hours,
                            l2.end_time_ts,
                            l2.uncompressed
                     FROM (
                              /* intermediate step, gathering data for calculations to be made further up the select chain */
                              SELECT INSTR(data.uncompressed, '"nodes": "') AS nodes_loc,
                                     LENGTH('"nodes": "')                   AS nodes_len,
                                     data.uncompressed,
                                     HOUR(data.time_diff)                   AS hours,
                                     data.end_time_ts
                              FROM (
                                  {}
                              ) AS data
                          ) AS l2
                 ) AS l3
                """.format(initial_data_query)

            # Make sure to filter on the size of jobs we're supposed to be processing.
            if self.small_jobs:
                query += "WHERE l3.hours <= 24 AND l3.nodes < 200 "
            elif self.large_jobs:
                query += "WHERE l3.hours > 24 "

            # Make sure to maintain the original ordering.
            query += "ORDER BY l3.end_time_ts"

            return query, data

    def timereader(self, start_time=None, end_time=None, seek=0):
        (query, data) = self.generate_time_query(start_time, end_time)
        cur = self.con.cursor()
        cur.execute(query, data)

        for record in cur:
            r = json.loads(record[0])
            yield r

    def reader(self,start_time=None, end_time=None, seek=0):
        """ seek parameter is unused. It is present for API compatibilty with file batch acct class """
        if self.local_jobid:
            for record in self.jobidreader(self.local_jobid):
                yield record
        else:
            for record in self.timereader(start_time, end_time, seek):
                yield record


        
def getconfig(configfilename = None):
    
    if configfilename == None:
        configfilename = "config.json"

    with open(configfilename, "rb") as fp:
        config = json.load(fp)

    return config

def ingestall(config):
    ingest(config, 9223372036854775807L, 0) 

def ingest(config, end_time, start_time = None):

    dbconf = config['accountdatabase']
    dbif = DbInterface(dbconf["dbname"], dbconf["tablename"], dbconf["defaultsfile"] )

    for resourcename,resource in config['resources'].iteritems():

        if 'enabled' in resource and resource['enabled'] == False:
            continue

        if resource['batch_system'] == "XDcDB":
            # The resources that use the accounting data directly from the 
            # datawarehouse are not handled by this script
            continue

        if start_time == None:
            start_time = dbif.getmostrecent( resource['resource_id'] )
            if start_time == None:
                start_time = 0
            else:
                start_time = start_time - (2* 24 * 3600)

        acctreader = batch_acct.factory( resource['batch_system'], resource['acct_path'], resource['host_name_ext'], resource, config)

        for acct in acctreader.reader(start_time, end_time):

            record = []
            record.append( resource['resource_id'] )
            if 'job_array_index' in acct:
                record.append(acct['job_array_index'])
            else:
                record.append(-1)

            jobid = acct['local_jobid'] if 'local_jobid' in acct else acct['id']
            record.append( jobid )
            record.append( acct['start_time'] )
            record.append( acct['end_time'] )
            record.append( json.dumps(acct) )

            dbif.insert(record)

        dbif.postinsert()


def usage():
    print '''
Usage: account.py [OPTION] [CONFIG PATH] [END TIME]

Ingest account data into the staging tables for the XSEDE SUPReMM workflow

   -s STARTTIME   Only process account records where the job end time is
                  greater than this value. The time is spcified as a POSIX
                  timestamp.  Default is 2 days before the end time of the most
                  recently ingested job.

   -e ENDTIME     Only process account records where the job end time is
                  less than this value. The time is spcified as a POSIX
                  timestamp. Default is +Inf. To maintain backwards
                  compatibility, the end time may also be specified as the
                  second non-option argument.

   -d             enable debug logging
   -h             Print this help message and exit.
'''

def main():

    optlist, args = getopt.getopt(sys.argv[1:], 'hds:e:')

    loglevel = logging.WARNING

    conffile = None
    start_time = None
    end_time = 9223372036854775807L

    for option, argument in optlist:
        if option == '-h':
            usage()
            sys.exit(1)
        elif option == '-s':
            start_time = int(argument)
        elif option == '-e':
            end_time = int(argument)
        elif option == '-d':
            loglevel = logging.DEBUG

    if len(args) > 0:
        conffile = args[0]

    if len(args) > 1:
        end_time = args[1]

    setuplogger(loglevel)

    ingest(getconfig(conffile), end_time, start_time)

if __name__ == "__main__":
    main()
