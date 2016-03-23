#!/usr/bin/env python
""" Script that indexes the pc archives for a given resource.
"""

import logging
import sys
import os
from datetime import datetime, timedelta
from getopt import getopt
import re
import gzip
import MySQLdb as mdb

from config import Config

class DbArchiveCache(object):
    """
    Helper class that adds job accounting records to the database
    """

    def __init__(self, resource_id, config):

        acctconf = config.getsection("archivedatabase")
        self.con = mdb.connect(db=acctconf['dbname'], read_default_file=acctconf['defaultsfile'])
        self.buffered = 0
        self._hostnamecache = {}
        self._versioncache = {}
        self.resource_id = resource_id

        cur = self.con.cursor()
        cur.execute("SELECT hostname FROM hosts WHERE resource_id = %s", resource_id)
        for host in cur:
            self._hostnamecache[host[0]] = 1

    def insert(self, hostname, filename, start, end, tacc_version):
        """
        Insert a job record
        """
        cur = self.con.cursor()
        if hostname not in self._hostnamecache:
            cur.execute("INSERT IGNORE INTO hosts (hostname, resource_id) VALUES (%s, %s)", [hostname, self.resource_id])
            self.con.commit()
            self._hostnamecache[hostname] = 1
        if tacc_version not in self._versioncache:
            cur.execute("INSERT IGNORE INTO version (name) VALUES (%s)", tacc_version)
            self.con.commit()
            self._versioncache[tacc_version] = 1

        query = """INSERT INTO archive (hostid, resource_id, filename, start_time_ts, end_time_ts, version) 
                   VALUES( (SELECT id FROM hosts WHERE hostname = %s AND resource_id = %s),%s,%s,%s,%s,(SELECT id FROM version WHERE name = %s)) 
                   ON DUPLICATE KEY UPDATE start_time_ts=%s, end_time_ts=%s, version=(SELECT id FROM version WHERE name = %s)"""
        cur.execute(query, [hostname, self.resource_id, self.resource_id, filename, start, end, tacc_version, start, end, tacc_version])

        self.buffered += 1
        if self.buffered > 100:
            self.con.commit()
            self.buffered = 0

    def postinsert(self):
        """
        Must be called after insert.
        """
        self.con.commit()


class BasicTaccArchiveParser(object):
    """ Bare bones implementation of tacc_stats archive file parser used to 
        retrieve file metadata. Will not find all possible problems with
        file corruption, but will catch things like empty files and corrupt
        gzip data """
    def __init__(self, filepath):
        self.filepath = filepath
        self.fileline = 0

        self.HEADER_PROPERTY = "$"

        self.hostname = "unknown"
        self.tacc_version = "unknown"
        self.firsttimestamp = None
        self.lasttimestamp = None

    def parsetimestamp(self, line):
        """ parse a timestamp line """
        tokens = line.split(" ")
        self.lasttimestamp = tokens[0]

        if self.firsttimestamp == None:
            self.firsttimestamp = self.lasttimestamp

    def parseheaderproperty(self, line):
        if line.startswith("$tacc_stats"):
            self.tacc_version = line.split(" ")[1].strip()
        elif line.startswith("$hostname"):
            self.hostname = line.split(" ")[1].strip()

    def parseline(self, line):
        """ process a single line from the archive """
        if len(line) < 1:
            return
        ch = line[0]

        if ch.isdigit():
            self.parsetimestamp(line)
        elif ch == self.HEADER_PROPERTY:
            self.parseheaderproperty(line)

    def parse(self):
        """ open and parse the contents of the archive """

        self.fileline = 0

        with gzip.open(self.filepath) as filep:
            for line in filep:
                self.fileline += 1
                self.parseline(line.strip())

class TaccStatsArchiveProcessor(object):
    """ Parses a pcp archive and adds the archive information to the index """

    def __init__(self, config, resconf):
        self.resource_id = resconf['resource_id']
        self.hostnameext = resconf['host_name_ext']
        self.dbac = DbArchiveCache(self.resource_id, config)

    def processarchive(self, archive):
        """ Try to open the tacc_stats archive and extract the timestamps of the first and last
            records and hostname. Store this in the DbArchiveCache
        """
        try:
            data = BasicTaccArchiveParser(archive)
            data.parse()

            hostname = data.hostname
            if self.hostnameext != "" and (not hostname.endswith(self.hostnameext)):
                hostname += "." + self.hostnameext

            self.dbac.insert(hostname, archive, data.firsttimestamp, data.lasttimestamp, data.tacc_version)

            logging.debug("processed archive %s", archive)

        except IOError as ioe:
            logging.error("archive %s. %s", archive, exc.message())

    def close(self):
        """ cleanup and close the connection """
        self.dbac.postinsert()

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


def datetimetoposix(dt):
    if dt.utcoffset() != None:
        utc_naive  = dt.replace(tzinfo=None) - dt.utcoffset()
    else:
        utc_naive = dt
    return (utc_naive - datetime(1970, 1, 1)).total_seconds()

class TaccStatsArchiveFinder(object):
    """ Helper class that finds all tacc_stats archive files in a directory
        mindate is the minimum datestamp of files that should be processed
    """

    def __init__(self, mindate, pathfilter):
        if mindate == None:
            self.mindate_ts = None
        else:
            self.mindate_ts = datetimetoposix(mindate)

        self.fregex = re.compile(r"^(\d*)\.gz$")
        self.pathfilter = pathfilter

    def filenameok(self, filename):
        """ parse filename to get the datestamp and compare with the reference datestamp
        """
        if self.mindate_ts == None:
            return True

        mtch = self.fregex.match(filename)

        if mtch == None:
            return False

        timestamp = int(mtch.group(1))

        return timestamp > self.mindate_ts

    def find(self, topdir):
        """  find all archive files in topdir """
        if topdir == "":
            return

        for (dirpath, subdirs, filenames) in os.walk(topdir):
            for filename in filenames:
                archivefile = os.path.join(dirpath, filename)
                if filename.endswith(".gz") and self.filenameok(filename):
                    yield archivefile

            if self.pathfilter != None:
                # In-place modification of subdirs
                subdirs[:] = [subdir for subdir in subdirs if self.pathfilter.match(subdir) != None]

DAY_DELTA = 3


def usage():
    """ print usage """
    print "usage: {0} [OPTS]".format(os.path.basename(__file__))
    print "  -r --resource=RES    process only archive files for the specified resource,"
    print "                       if absent then all resources are processed"
    print "  -c --config=PATH     specify the path to the configuration directory"
    print "  -m --mindate=DATE    specify the minimum datestamp of archives to process"
    print "                       (default", DAY_DELTA, "days ago)"
    print "  -a --all             process all archives regardless of age"
    print "  -d --debug           set log level to debug"
    print "  -q --quiet           only log errors"
    print "  -h --help            print this help message"


def getoptions():
    """ process comandline options """

    retdata = {
        "log": logging.INFO,
        "resource": None,
        "config": None,
        "mindate": datetime.now() - timedelta(days=3)
    }

    opts, _ = getopt(sys.argv[1:], "r:c:m:adqh", ["resource=", "config=", "mindate=", "all", "debug", "quiet", "help"])

    for opt in opts:
        if opt[0] in ("-r", "--resource"):
            retdata['resource'] = opt[1]
        elif opt[0] in ("-d", "--debug"):
            retdata['log'] = logging.DEBUG
        elif opt[0] in ("-q", "--quiet"):
            retdata['log'] = logging.ERROR
        elif opt[0] in ("-c", "--config"):
            retdata['config'] = opt[1]
        elif opt[0] in ("-m", "--mindate"):
            retdata['mindate'] = parsetime(opt[1])
        elif opt[0] in ("-a", "--all"):
            retdata['mindate'] = None
        elif opt[0] in ("-h", "--help"):
            usage()
            sys.exit(0)

    return retdata


def runindexing():
    """ main script entry point """
    opts = getoptions()

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S', level=opts['log'])
    if sys.version.startswith("2.7"):
        logging.captureWarnings(True)

    config = Config(opts['config'])

    for resourcename, resource in config.resourceconfigs():

        if opts['resource'] in (None, resourcename, str(resource['resource_id'])):

            pathfilter = None
            if 'path_filter' in resource:
                pathfilter = re.compile(resource['path_filter'])

            acache = TaccStatsArchiveProcessor(config, resource)
            afind = TaccStatsArchiveFinder(opts['mindate'], pathfilter)

            for archivefile in afind.find(resource['tacc_stats_home'] + "/archive"):
                acache.processarchive(archivefile)

            acache.close()

if __name__ == "__main__":
    runindexing()
