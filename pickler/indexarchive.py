#!/usr/bin/python
import gzip
import sys
import base64
import StringIO
import re
import os

import MySQLdb as mdb

class DataSqlStore:
    def __init__(self, dbname, mydefaults):

        self.con = mdb.connect(db=dbname, read_default_file=mydefaults)
        self.buffered = 0
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
                cur.execute("INSERT IGNORE INTO supermichost (resource_id, hostname) VALUES (%s,%s)", [2812, hostname])
                self.con.commit()
                self._hostlistcache[hostname] = 1

            cur.execute("INSERT INTO supermicjobhosts (resource_id, jobid, hostid, timestamp, type) VALUES(%s, %s, (SELECT id FROM supermichost WHERE resource_id = %s AND hostname = %s), %s, %s )",
                        [2812, jobid, 2812, hostname, timestamp, startend])

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
            GROUP BY hostid;
            """
        cur = self.con.cursor()
        cur.execute(query)
        res = {}
        for r in cur:
            res[r[0]] = r[1]

        return res

    def recordstart(self, jobid, hostname, timestamp):
        self.record(jobid, hostname, timestamp, "start")

    def recordend(self, jobid, hostname, timestamp):
        self.record(jobid, hostname, timestamp, "end")

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
    def __init__(self):
        #self.jobs = DataProxy()
        self.jobs = DataSqlStore("ts_analysis", "~/.my.cnf")
        
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

                #a.parsearchive(os.path.join(root, fname))

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

def main():
    
    a = ArchiveIndexer()
    a.process("/data/scratch/SuperMIC/archive")
    print a

if __name__ == '__main__':
    main()

