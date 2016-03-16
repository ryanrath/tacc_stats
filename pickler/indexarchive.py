#!/usr/bin/python
""" helper functions to clean up tacc_stats data """
import gzip
import re
import os
import json

from account import DbInterface
import MySQLdb as mdb
import MySQLdb.cursors

class DataSqlStore:
    def __init__(self, dbname, mydefaults, resource_id):

        self.con = mdb.connect(db=dbname, read_default_file=mydefaults)
        self.buffered = 0
        self.resource_id = resource_id
        self._hostlistcache = {}

    def __str__(self):
        return "Processed " + str(len(self._hostlistcache))

    def record(self, jobid, hostname, timestamp, startend):
        """
        Insert a job record
        """
        cur = self.con.cursor()
        try:
            if hostname not in self._hostlistcache:
                cur.execute("INSERT IGNORE INTO supermichost (resource_id, hostname) VALUES (%s,%s)", [self.resource_id, hostname])
                self.con.commit()
                self._hostlistcache[hostname] = 1

            cur.execute("INSERT INTO supermicjobhosts (resource_id, jobid, hostid, timestamp, type) VALUES(%s, %s, (SELECT id FROM supermichost WHERE resource_id = %s AND hostname = %s), %s, %s )",
                        [self.resource_id, jobid, self.resource_id, hostname, timestamp, startend])

        except mdb.IntegrityError as e:
            if e[0] != 1062:
                raise e
            else:
                print "Sadness"
                # Todo - check that the blobs match on duplicate records

        self.buffered += 1
        if self.buffered > 10:
            self.con.commit()
            self.buffered = 0


    def postinsert(self):
        """ 
        Must be called after insert.
        """
        self.con.commit()

    def getmaxhosttimestamps(self):
        query = """
            SELECT 
                h.`hostname`, MAX(timestamp)
            FROM
                supermicjobhosts jh,
                supermichost h
            WHERE
                h.id = jh.hostid
                AND jh.resource_id = %s
            GROUP BY hostid;
            """
        cur = self.con.cursor()
        cur.execute(query, (self.resource_id, ))
        res = {}
        for r in cur:
            res[r[0]] = r[1]

        return res

    def recordstart(self, jobid, hostname, timestamp):
        self.record(jobid, hostname, timestamp, "start")

    def recordend(self, jobid, hostname, timestamp):
        self.record(jobid, hostname, timestamp, "end")

class JobAccountFaker(object):
    """ Retrieve job account data directly from the datawarehouse """
    def __init__(self, dbname, mydefaults, resconf):
        self.con = mdb.connect(db=dbname, read_default_file=mydefaults, cursorclass=MySQLdb.cursors.DictCursor)
        self.resource_id = resconf['resource_id']
        self.dbname = dbname

    def getjob(self):
        """ iterator to get a job account data object """

        query = """
SELECT 
    jf.resource_id AS resource_id,
    jf.local_jobid AS id,
    jf.queue_id AS `queue`,
    a.charge_number AS project,
    s.username AS uid,
    jf.submit_time_ts  AS queue_time,
    jf.start_time_ts AS start_time,
    jf.end_time_ts  AS end_time,
    jf.nodecount AS nodes,
    jf.processors AS cores,
    jf.`name` AS job_name
FROM
    modw.jobfact jf
        LEFT JOIN
    {0}.accountfact af ON jf.resource_id = af.resource_id
        AND jf.local_jobid = af.local_job_id
        INNER JOIN modw.account a ON a.id = jf.account_id
        INNER JOIN modw.systemaccount s ON s.id = jf.systemaccount_id
WHERE
    af.resource_id IS NULL
        AND jf.resource_id = %s 
        """.format(self.dbname)

        cur = self.con.cursor()
        cur.execute(query, (self.resource_id, ))
        for rec in cur:

            record = []
            record.append(rec['resource_id'])
            record.append("") # placeholder for cluster
            record.append(rec['id'])
            record.append(rec['start_time'])
            record.append(rec['end_time'])
            record.append(json.dumps(rec))

            yield record

class SuperMicJobAccountFaker(object):
    def __init__(self, dbname, mydefaults):
        self.con = mdb.connect(db=dbname, read_default_file=mydefaults, cursorclass=MySQLdb.cursors.DictCursor)

    def getjob(self):

        # This query _should_ return the list of accounts that have tacc_stats data and are not in the
        # AccountFact table

        # The 18,000 time offset is the fiddle factor for the discrpency between jobfact times
        # and tacc stats times (which probably varies with time of year :-(
        fiddlefactor = "18000"

        # The second fixup is that the jobids for PBS systems are strings. On SuperMIC the 
        # jobid is a number followed by ".smic3", but the string part is stripped off befroe 
        # it makes it into the modw.jobfact table.

        query = """
SELECT 
    jf.resource_id AS resource_id,
    jf.local_jobid AS local_jobid,
    CONCAT(jf.local_jobid,'.smic3') as id,
    jf.queue_id AS `partition`,
    a.charge_number AS account,
    s.username AS user,
    (jf.submit_time_ts + {}) AS submit,
    (jf.start_time_ts + {}) AS start_time,
    (jf.end_time_ts + {}) AS end_time,
    COUNT(jh.hostid) AS hostcount,
    jf.nodecount AS nodes,
    jf.processors AS ncpus,
    GROUP_CONCAT(hh.hostname) AS node_list,
    jf.`name` AS jobname
FROM
    ts_analysis.supermicjobhosts jh,
    modw.jobfact jf,
    modw.account a,
    modw.systemaccount s,
    ts_analysis.supermichost hh,
    (SELECT DISTINCT
        jh.resource_id, jh.jobid AS local_jobid
    FROM
        ts_analysis.supermicjobhosts jh
    INNER JOIN modw.jobfact jf ON jf.local_jobid = jh.jobid
        AND jf.resource_id = jh.resource_id
    LEFT JOIN ts_analysis.accountfact af ON af.resource_id = jh.resource_id
        AND af.local_job_id = jh.jobid
    WHERE
        af.local_job_id IS NULL) pending
WHERE
    jh.`type` = 'end'
        AND jf.local_jobid = jh.jobid
        AND jh.hostid = hh.id
        AND jf.resource_id = jh.resource_id
        AND jf.start_time_ts + {} < jh.`timestamp`
        AND a.id = jf.account_id
        AND s.id = jf.systemaccount_id
        AND pending.local_jobid = jh.jobid
        AND pending.resource_id = jh.resource_id
GROUP BY 1 , 2
        """.format(fiddlefactor, fiddlefactor, fiddlefactor, fiddlefactor)

        cur = self.con.cursor()
        cur.execute(query)
        for r in cur:

            record = []
            record.append( r['resource_id'] )
            record.append("") # placeholder for cluster
            record.append( r['local_jobid'] )
            record.append( r['start_time'] )
            record.append( r['end_time'] )
            r['host_list'] = r['node_list'].split(',')
            record.append( json.dumps(r) )

            yield record
    

class DataProxy:
    def __init__(self):
        self.data = {}

    def __str__(self):
        s = ""
        for jobid, hosts in self.data.iteritems():
            s += str(jobid) + " " + str(len(hosts)) + "\n"
        return s

    def recordstart(self, jobid, hostname, timestamp):
        self.record(jobid, hostname, timestamp, "start")

    def recordend(self, jobid, hostname, timestamp):
        self.record(jobid, hostname, timestamp, "end")

    def record(self, jobid, hostname, timestamp, startend):

        if jobid not in self.data:
            self.data[jobid] = {}

        if hostname not in self.data[jobid]:
            self.data[jobid][hostname] = {}

        if startend not in self.data[jobid][hostname]:
            self.data[jobid][hostname][startend] = timestamp

class ArchiveIndexer:
    def __init__(self, accountconfig, resconf):
        self.jobs = DataSqlStore( accountconfig['dbname'], accountconfig['defaultsfile'], resconf['resource_id'])
        
    def __str__(self):
        return str(self.jobs)

    def getjobid(self, line):
        jobstr = line.strip().split()[-1]
        m = re.search('^([0-9]*).*', jobstr)
        if m:
            return int(m.group(1))
        else:
            raise Exception("Invalid jobid" + jobstr)

    def process(self, basepath):

        ar = re.compile('^([0-9]*)\.gz$')

        hostsdone = self.jobs.getmaxhosttimestamps()

        for root, dirname, files in os.walk(basepath):
            for fname in files:
                m = ar.match(fname)
                if m:
                    hostname = os.path.basename(root)
                    timestamp = int(m.group(1))
                    if hostname in hostsdone and hostsdone[hostname] > timestamp:
                        # Skip this file
                        continue
                    self.parsearchive(os.path.join(root, fname))

        self.jobs.postinsert()

    def parsearchive(self, filename):
    
        lineNum = 0
        time = None
        hostname = None
        try:
            with gzip.open(filename) as f:
                for line in f:
                    # store line number
                    lineNum += 1
                    if line.startswith("$hostname"):
                        hostname = line.strip().split()[1]
                    # test if its already running
                    if line[0].isdigit():
                        tok = line.strip().split()
                        time = tok[0]
                    # test if it is starting
                    if re.match("% *begin", line) != None:
                        jobid = self.getjobid(line)
                        self.jobs.recordstart(jobid, hostname, time)
                    # test if it is ending
                    if re.match("% *end", line) != None:
                        jobid = self.getjobid(line)
                        self.jobs.recordend(jobid, hostname, time)
        except TypeError as e:
            print e
            pass
        
def getconfig(configfilename = "config.json"):
    
    with open(configfilename, "rb") as fp:
        config = json.load(fp)

    return config

def main():

    config = getconfig()

    #mode = "indexarchive"
    #mode = "createaccount"
    mode = "both"

    for resourcename,resource in config['resources'].iteritems():

        if 'enabled' in resource and resource['enabled'] == False:
            continue

        if resource['batch_system'] != "XDcDB":
            continue
    
        if mode == "indexarchive" or mode == "both":
            a = ArchiveIndexer(config['accountdatabase'], resource)
            a.process(resource['tacc_stats_home'])
            print resourcename, str(a)

        if mode == "createaccount" or mode == "both":
            dbconf = config['accountdatabase']
            if resourcename == "supermic":
                f = SuperMicJobAccountFaker(dbconf['dbname'], dbconf['defaultsfile'])
            else:
                f = JobAccountFaker(dbconf['dbname'], dbconf['defaultsfile'], resource)
            dbif = DbInterface(dbconf["dbname"], dbconf["tablename"], dbconf["defaultsfile"] )
            for job in f.getjob():
                dbif.insert(job)
            dbif.postinsert()


if __name__ == '__main__':
    main()

