#!/usr/bin/env python
import datetime, numpy, os, sys, gzip
import amd64_pmc, intel_process
import phys_cores_process
import re
import procdump
import string
import math

import logging

if sys.version.startswith("3"):
    import io
    io_method = io.BytesIO
else:
    import cStringIO
    io_method = cStringIO.StringIO
    #import io
    #io.BufferedIOBase
if sys.version.startswith("2.6"):
    from backport_collections import OrderedDict
else:
    from collections import OrderedDict

verbose = os.getenv('TACC_STATS_VERBOSE')

if not verbose:
    numpy.seterr(over='ignore')
else:
    logging.basicConfig(level=logging.DEBUG)

prog = os.path.basename(sys.argv[0])
if prog == "":
    prog = "***"

def trace(fmt, *args):
    if verbose:
        msg = fmt % args
        logging.debug(prog + ": " + msg)

def error(fmt, *args):
    # Job-level errors are summarization process level wanrings since an error
    # with one job does not prevent others from being processed
    msg = fmt % args
    logging.warning(prog + ": " + msg)

RAW_STATS_TIME_MAX = 86400 + 2 * 3600
RAW_STATS_TIME_PAD = 1200

SF_SCHEMA_CHAR = '!'
SF_DEVICES_CHAR = '@'
SF_COMMENT_CHAR = '#'
SF_PROPERTY_CHAR = '$'
SF_MARK_CHAR = '%'

KEEP_EDITS = False

def schema_fixup(type_name, desc):
    """ This function implements a workaround for a known issue with incorrect schema """
    """ definitions for irq, block and sched tacc_stats metrics. """

    if type_name == "irq":
        # All of the irq metrics are 32 bits wide
        res = ""
        for token in desc.split():
            res += token.strip() + ",W=32 "
        return res

    elif type_name == "sched":
        # Most sched counters are 32 bits wide with 3 exceptions
        res = ""
        sixtyfourbitcounters = [ "running_time,E,U=ms", "waiting_time,E,U=ms", "pcount,E" ]
        for token in desc.split():
            if token in sixtyfourbitcounters:
                res += token.strip() + " "
            else:
                res += token.strip() + ",W=32 "
        return res
    elif type_name == "block":
        # Most block counters are 64bits wide with a few exceptions
        res = ""
        thirtytwobitcounters = [ "rd_ticks,E,U=ms", "wr_ticks,E,U=ms", "in_flight", "io_ticks,E,U=ms", "time_in_queue,E,U=ms" ]
        for token in desc.split():
            if token in thirtytwobitcounters:
                res += token.strip() + ",W=32 "
            else:
                res += token.strip() + " "
        return res
    elif type_name == "panfs":
        # The syscall_*_(n+)s stats are not events
        res = ""
        for token in desc.split():
            token = token.strip()
            if token.startswith("syscall_") and ( token.endswith("_s,E,U=s") or token.endswith("_ns,E,U=ns")):
                res += string.replace(token, "E,", "") + " "
            else:
                res += token + " "
        return res
    elif type_name == "ib":
        res = ""
        for token in desc.split():
            token = token.strip()
            if not token.endswith(",W=32"):
                res += token.strip() + ",W=32 "
            else:
                res += token.strip() + " "
        return res

    return desc

class SchemaEntry(object):
    __slots__ = ('key', 'index', 'is_control', 'is_event', 'width', 'mult', 'unit')

    def __init__(self, i, s):
        opt_lis = s.split(',')
        self.key = opt_lis[0]
        self.index = i
        self.is_control = False
        self.is_event = False
        self.width = None
        self.mult = None
        self.unit = None
        for opt in opt_lis[1:]:
            if len(opt) == 0:
                continue
            elif opt[0] == 'C':
                self.is_control = True
            elif opt[0] == 'E':
                self.is_event = True
            elif opt[0:2] == 'W=':
                self.width = int(opt[2:])
            elif opt[0:2] == 'U=':
                j = 2
                while j < len(opt) and opt[j].isdigit():
                    j += 1
                if j > 2:
                    self.mult = numpy.uint64(opt[2:j])
                if j < len(opt):
                    self.unit = opt[j:]
                if self.unit == "KB":
                    self.mult = numpy.uint64(1024)
                    self.unit = "B"
            else:
                # XXX
                raise ValueError("unrecognized option `%s' in schema entry spec `%s'\n", opt, s)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               all(self.__getattribute__(attr) == other.__getattribute__(attr) \
                   for attr in self.__slots__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        lis = [] # 'index=%d' % self.index
        if self.is_event:
            lis.append('is_event=True')
        elif self.is_control:
            lis.append('is_control=True')
        if self.width:
            lis.append('width=%d' % int(self.width))
        if self.mult:
            lis.append('mult=%d' % int(self.mult))
        if self.unit:
            lis.append('unit=%s' % self.unit)
        return '(' + ', '.join(lis) + ')'


class Schema(dict):
    def __init__(self, desc):
        dict.__init__(self)
        self.desc = desc
        self._key_list = []
        self._value_list = []
        for i, s in enumerate(desc.split()):
            e = SchemaEntry(i, s)
            dict.__setitem__(self, e.key, e)
            self._key_list.append(e.key)
            self._value_list.append(e)

    def __iter__(self):
        return self._key_list.__iter__()

    def __repr__(self):
        return '{' + ', '.join(("'%s': %s" % (k, repr(self[k]))) \
                               for k in self._key_list) + '}'

    def _notsup(self, s):
        raise TypeError("'Schema' object does not support %s" % s)

    def __delitem__(self, k, v):
        self._notsup('item deletion')

    def pop(self, k, d=None):
        self._notsup('removal')

    def popitem(self):
        self._notsup('removal')

    def setdefault(self, k, d=None):
        self._notsup("item assignment")

    def update(self, **args):
        self._notsup("update")

    def items(self):
        return zip(self._key_list, self._value_list)

    def iteritems(self):
        for k in self._key_list:
            yield (k, dict.__getitem__(self, k))

    def iterkeys(self):
        return self._key_list.__iter__()

    def itervalues(self):
        return self._value_list.__iter__()

    def keys(self):
        return self._key_list

    def values(self):
        return self._value_list


#def get_host_list_path(acct, host_list_dir):
#    """Return the path of the host list written during the prolog."""
#    # Example: /share/sge6.2/default/tacc/hostfile_logs/2011/05/19/prolog_hostfile.1957000.IV32627
#    start_date = datetime.date.fromtimestamp(acct['start_time'])
#    base_glob = 'prolog_hostfile.' + acct['id'] + '.*'
#    for days in (0, -1, 1):
#        yyyy_mm_dd = (start_date + datetime.timedelta(days)).strftime("%Y/%m/%d")
#        full_glob = os.path.join(host_list_dir, yyyy_mm_dd, base_glob)
#        for path in glob.iglob(full_glob):
#            return path
#    return None


def stats_file_discard_record(file):
    for line in file:
        if line.isspace():
            return


# ------------------------------------------------------------------

(PENDING_FIRST_RECORD, ACTIVE, ACTIVE_IGNORE, LAST_RECORD, DONE ) = range(0,5)
statenames = { PENDING_FIRST_RECORD: "PENDING_FIRST_RECORD", ACTIVE: "ACTIVE", ACTIVE_IGNORE: "ACTIVE_IGNORE", LAST_RECORD: "LAST_RECORD", DONE: "DONE" }

class Host(object):
    def __init__(self, job, name, raw_stats_dir, name_ext, genproc = False):
        self.job = job
        self.name = name
        self.name_ext = name_ext
        self.raw_stats_dir=raw_stats_dir
        if genproc:
            self.procdump = procdump.ProcDump()
        else:
            self.procdump = None

        self.times = []
        self.raw_stats = {}
        self.marks = {}
        self.rotatetimes = []

        self.state = PENDING_FIRST_RECORD
        self.timestamp = None
        self.filename = None
        self.fileline = None
        self.tacc_version = "Unknown"

        self.mismatch_schemas = {}

    def trace(self, fmt, *args):
        logging.debug( fmt % args )

    def error(self, fmt, *args):
        self.job.error('%s: ' + fmt, self.name, *args)

    def get_stats_paths(self):
        raw_host_stats_dir = os.path.join(self.raw_stats_dir, self.name+self.name_ext)
        job_start = self.job.start_time - RAW_STATS_TIME_PAD
        job_end = self.job.end_time + RAW_STATS_TIME_PAD
        path_list = []
        try:
            for ent in os.listdir(raw_host_stats_dir):
                base, dot, ext = ent.partition(".")
                if not base.isdigit():
                    continue
                if ext != "gz":
                    continue
                # Support for filenames of the form %Y%m%d
                if re.match('^[0-9]{4}[0-1][0-9][0-3][0-9]$', base):
                    base = (datetime.datetime.strptime(base,"%Y%m%d") - datetime.datetime(1970,1,1)).total_seconds()
                # Prune to files that might overlap with job.
                ent_start = long(base)
                ent_end = ent_start + 2*RAW_STATS_TIME_MAX
                if ((ent_start <= job_start) and (job_start <= ent_end)) or ((ent_start <= job_end) and (job_end <= ent_end)) or (max(job_start, ent_start) <= min(job_end, ent_end)) :
                    full_path = os.path.join(raw_host_stats_dir, ent)
                    path_list.append((full_path, ent_start))
                    self.trace("path `%s', start %d", full_path, ent_start)
        except Exception as exc:
            logging.error("get_stats_paths job %s. %s", self.job.id, exc)

        path_list.sort(key=lambda tup: tup[1])
        return path_list

    def read_stats_file_header(self, fp):
        file_schemas = {}
        for line in fp:
            self.fileline += 1
            try:
                c = line[0]
                if c == SF_SCHEMA_CHAR:
                    type_name, schema_desc = line[1:].split(None, 1)
                    schema = self.job.get_schema(type_name, schema_desc)
                    if schema:
                        file_schemas[type_name] = schema
                    else:
                        self.mismatch_schemas[type_name] = 1
                        self.error("file `%s', type `%s', schema mismatch desc `%s'",
                                   fp.name, type_name, schema_desc)
                elif c == SF_PROPERTY_CHAR:
                    if line.startswith("$tacc_stats"):
                        self.tacc_version = line.split(" ")[1].strip()
                    pass
                elif c == SF_COMMENT_CHAR:
                    pass
                else:
                    break
            except Exception as exc:
                self.error("file `%s', caught `%s' discarding line `%s'",
                           fp.name, exc, line)
                break
        return file_schemas


    def read_stats_file(self, fp):

        if self.state == DONE:
            return

        self.filename = fp.name
        self.fileline = 0

        self.file_schemas = self.read_stats_file_header(fp)
        if not self.file_schemas:
            self.error("file `%s' bad header on line %s", self.filename, self.fileline)
            return

        try:
            for line in fp:
                self.fileline += 1
                self.parse(line.strip())
                if self.state == DONE:
                    break
        except Exception as e:
            self.error("file `%s' exception %s on line %s", self.filename, str(e), self.fileline)


    def parse(self, line):
        if len(line) < 1:
            return

        ch = line[0]

        if ch.isdigit():
            self.processtimestamp(line)
        elif ch.isalpha():
            self.processdata(line)
        elif ch == SF_SCHEMA_CHAR:
            self.processschema(line)
        elif ch == SF_COMMENT_CHAR:
            pass
        elif ch == SF_PROPERTY_CHAR:
            self.processproperty(line)
        elif ch == SF_MARK_CHAR or ch == '^':
            try:
                self.processmark(line)
            except TypeError as e:
                self.error("TypeError %s in %s line %s", str(e), self.filename, self.fileline)
        else:
            logging.warning("Unregognised character \"%s\" in %s on line %s ",
                            ch, self.filename, self.fileline)
            pass

    def setstate(self, newstate, reason = None):
        self.trace("TRANS {} -> {} ({})".format( statenames[self.state], statenames[newstate], reason ) )
        self.state = newstate

    def processtimestamp(self,line):
        recs = line.strip().split(" ")
        try:
            self.timestamp = float(recs[0])
            jobs = recs[1].strip().split(",")
        except IndexError as e:
            self.error("syntax error timestamp in file '%s' line %s", self.filename, self.fileline)
            return

        if self.state == PENDING_FIRST_RECORD:
            if self.job.id in jobs:
                self.setstate(ACTIVE, "job in timestamp list")
            elif math.floor(self.timestamp) >= self.job.start_time:
                self.setstate(ACTIVE, "timestamp in job window")
        elif self.state == ACTIVE:
            if math.floor(self.timestamp - 600) > self.job.end_time:
                self.setstate(DONE, "timestamp out of job window")
        elif self.state == ACTIVE_IGNORE:
            self.setstate(ACTIVE)
        elif self.state == LAST_RECORD:
            self.setstate(DONE, "processed last record")

        if self.state == ACTIVE:
            self.times.append( self.timestamp )

    @staticmethod
    def processproc(schema, devname, rest):
        """ Process names may contain arbitrary data including the tacc_stats record delimiter character
            Attempt to handle the case where the process name contains one of more record delimiters """

        tokens = rest.split()

        while len(tokens) > len(schema):
            devname = devname + " " + tokens[0]
            tokens.pop(0)

        vals = numpy.asarray(tokens, dtype=numpy.uint64)

        return devname, vals

    def processdata(self,line):
        if self.state == ACTIVE or self.state == LAST_RECORD:

            try:
                type_name, dev_name, rest = line.split(None, 2)
            except ValueError as e:
                self.error("syntax error on file '%s' line %s", self.filename, self.fileline)
                return

            schema = self.file_schemas.get(type_name)
            if not schema:
                if not type_name in self.mismatch_schemas:
                    self.error("file `%s', unknown type `%s', discarding line `%s'",
                        self.filename, type_name, self.fileline)
                return

            if type_name == 'proc':
                dev_name, vals = self.processproc(schema, dev_name, rest)
            else:
                vals = numpy.fromstring(rest, dtype=numpy.uint64, sep=' ')

            if vals.shape[0] != len(schema):
                self.error("file `%s', type `%s', expected %d values, read %d, discarding line `%s'",
                       self.filename, type_name, len(schema), vals.shape[0], self.fileline)
                return

            type_stats = self.raw_stats.setdefault(type_name, {})
            dev_stats = type_stats.setdefault(dev_name, [])
            dev_stats.append((self.timestamp, vals))

    def processschema(self,line):
        print "processschema"
        pass

    def processproperty(self,line):
        print "processproperty"
        pass

    def processmark(self,line):
        mark = line[1:].strip()
        actions = mark.split()
        if not actions:
            self.error("syntax error processmark file `%s' line `%s'", self.filename, self.fileline)
            return
        if actions[0] == "end":
            if actions[1] == self.job.id:
                if self.state == ACTIVE:
                    # This is the end for the sought after job
                    self.setstate(LAST_RECORD, "seen end marker")
                    self.marks['end'] = True
                else:
                    self.error("end marker in {} line {} before job started".format(self.filename, self.fileline) )
                    # Stay in non-active
            else:
                # this is an end marker for another job.
                if self.state == ACTIVE:
                    self.times = self.times[:-1]
                    self.setstate(ACTIVE_IGNORE, "end for another job")

        if actions[0] == "begin":
            self.trace( "Seen begin at %s for \"%s\"", self.timestamp, actions[1] )
            if actions[1] == self.job.id:
                if self.state == ACTIVE:
                    # Need to discard any earlier timerecords since the begin resets the counters.
                    if len(self.times) > 1:
                        self.trace("BEGIN_IN_MIDDLE {} {} line {} @ {} discard {} previous".format(self.name, self.filename, self.fileline, self.timestamp, len(self.times)-1 ) )
                        self.raw_stats = {}
                        self.times = [ self.timestamp ]
                        self.rotatetimes = []
                else:
                    self.setstate(ACTIVE, "seen begin marker")
                    self.marks['begin'] = True
            else:
                # this is a begin marker for another job.
                if self.state == ACTIVE:
                    self.times = self.times[:-1]
                    self.setstate(ACTIVE_IGNORE, "begin for another job")

        if actions[0] == "rotate":
            if self.state == ACTIVE or self.state == ACTIVE_IGNORE:
                self.rotatetimes.append(self.timestamp)

        if actions[0] == "procdump":
            # procdump information is valid even when in active ignore
            if (self.state == ACTIVE or self.state == ACTIVE_IGNORE) and self.procdump != None:
                self.procdump.parse(line)
        pass

    def gather_stats(self):
        path_list = self.get_stats_paths()
        if len(path_list) == 0:
            self.error("no stats files overlapping job")
            return False

        # read_stats_file() and parse_stats() append stats records
        # into lists of tuples in self.raw_stats.  The lists will be
        # converted into numpy arrays below.
        for path, start_time in path_list:
            try:
                with gzip.open(path) as file:
                    self.read_stats_file(file)
            except IOError as ioe:
                self.error("read error for file %s", path)

        return self.raw_stats

    def get_stats(self, type_name, dev_name, key_name):
        """Host.get_stats(type_name, dev_name, key_name)
        Return the vector of stats for the given type, dev, and key.
        """
        schema = self.job.get_schema(type_name)
        index = schema[key_name].index
        return self.stats[type_name][dev_name][:, index]



class Job(object):
    # TODO errors/comments
    __slots__ = ('id', 'start_time', 'end_time', 'acct', 'schemas', 'hosts',
    'times','stats_home', 'host_list_dir', 'batch_acct', 'edit_flags', 'errors', 'overflows')

    def __init__(self, acct, stats_home, host_list_dir, batch_acct):
        self.id = acct['id']
        self.start_time = acct['start_time']
        self.end_time = acct['end_time']
        self.acct = acct
        self.schemas = {}
        self.hosts = OrderedDict()
        self.times = []
        self.stats_home=stats_home
        self.host_list_dir=host_list_dir
        self.batch_acct=batch_acct
        self.edit_flags = []
        self.errors = set()
        self.overflows = dict()

    def trace(self, fmt, *args):
        trace('%s: ' + fmt, self.id, *args)

    def error(self, fmt, *args):
        self.errors.add( fmt % args )
        error('%s: ' + fmt, str(self.id), *args)

    def get_schema(self, type_name, desc=None):
        schema = self.schemas.get(type_name)
        if schema:
            if desc and schema.desc != schema_fixup(type_name,desc):
                # ...
                return None
        elif desc:
            desc = schema_fixup(type_name, desc)
            schema = self.schemas[type_name] = Schema(desc)
        return schema

    def gather_stats(self):
        if "host_list" in self.acct:
            host_list = self.acct['host_list']
            if host_list == ["None assigned"]:
                host_list = []
        else:
            path = self.batch_acct.get_host_list_path(self.acct, self.host_list_dir)
            if not path:
                if self.end_time - self.start_time > 0:
                    # Only care about missing hosts if the job actually ran!
                    self.error("no host list found in dir " + self.host_list_dir)
                return False
            try:
                with open(path) as file:
                    host_list = [host for line in file for host in line.split() if line != "None assigned"]
            except IOError as (err, str):
                self.error("cannot open host list `%s': %s", path, str)
                return False
        if len(host_list) == 0 and self.end_time - self.start_time > 0:
            self.error("empty host list")
            return False
        for hidx, host_name in enumerate(host_list):
            # TODO Keep bad_hosts.
            try: host_name = host_name.split('.')[0]
            except: pass
            
            host = Host(self, host_name, self.stats_home + '/archive',self.batch_acct.name_ext, hidx == 0 )
            if host.gather_stats():
                self.hosts[host_name] = host
        if not self.hosts:
            self.error("no good hosts")
            return False
        return True

    def munge_times(self):
        times_lis = []
        for host in self.hosts.itervalues():
            times_lis.append(host.times)

            # the data for a host is considered complete if there is at least one
            # measurement for every 12 minutes of job walltime.
            if len(host.times) == 0:
                host.complete = False
            else:
                host.complete = ((self.end_time - self.start_time) / len(host.times)) < 720

            del host.times

        times_lis.sort(key=lambda lis: len(lis))
        # Choose times to have median length.
        times = list(times_lis[len(times_lis) / 2])
        if not times:
            return False
        times.sort()
        # Ensure that times is sane and monotonically increasing.
        t_min = 0
        for i in range(0, len(times)): 
            t = max(times[i], t_min)
            times[i] = t
            t_min = t + 1
        self.trace("nr times min %d, mid %d, max %d\n",
                   len(times_lis[0]), len(times), len(times_lis[-1]))
        self.trace("job start to first collect %d\n", times[0] - self.start_time)
        self.trace("last collect to job end %d\n", self.end_time - times[-1])
        self.times = numpy.array(times, dtype=numpy.float64)
        if len(times_lis[0]) != len(times_lis[-1]):
            self.errors.add( "Number of records differs between hosts (min {}, max {})".format(len(times_lis[0]), len(times_lis[-1]) ) )
        return True
    
    def process_dev_stats(self, host, type_name, schema, dev_name, raw):
        def trace(fmt, *args):
            return self.trace("host `%s', type `%s', dev `%s': " + fmt,
                              host.name, type_name, dev_name, *args)
        def error(fmt, *args):
            return self.error("host `%s', type `%s', dev `%s': " + fmt,
                              host.name, type_name, dev_name, *args)
        # raw is a list of pairs with car the timestamp and cdr a 1d
        # numpy array of values.
        m = len(self.times)
        n = len(schema)
        A = numpy.zeros((m, n), dtype=numpy.uint64) # Output.

        k = 0
        # len(raw) may not be equal to m, so we fill out A by choosing values
        # with the closest timestamps.
        # TODO sort out host times
        host.times = []
        rmsjitter = 0.0
        logrotates = []
        for i in xrange(0, m):
            t = self.times[i]
            while k + 1 < len(raw) and abs(raw[k + 1][0] - t) <= abs(raw[k][0] - t):
                k += 1
            rmsjitter += (raw[k][0] - t)**2
            A[i] = raw[k][1]
            if raw[k][0] in host.rotatetimes:
                logrotates.append(i)
            host.times.append(raw[k][0])

        if m > 0:
            rmsjitter = math.sqrt(rmsjitter) / m
            if rmsjitter > 60:
                self.errors.add("HRJ {} {}".format(host.name, type_name))

        # OK, we fit the raw values into A.  Now fixup rollover and
        # convert units.
        for e in schema.itervalues():
            j = e.index
            if e.is_event:
                p = r = A[0, j] # Previous raw, rollover/baseline.
                # Rebase, check for rollover.
                for i in range(0, m):
                    v = A[i, j]

                    if i in logrotates and host.tacc_version == "2.2.1" and type_name.startswith('intel_') and i > 0:
                        r = numpy.uint64(v) - A[i-1,j] 
                        if i > 1:
                            linear_interp = numpy.uint64(numpy.uint64(A[i-1, j] - A[i-2,j]) * numpy.uint64(host.times[i] - host.times[i-1]) ) / numpy.uint64(host.times[i-1] - host.times[i-2])
                            r -= linear_interp
                        fudged = True
                    elif v < p:
                        fudged = False
                        # Looks like rollover.
                        if e.width and e.width < 64:
                            trace("time %d, counter `%s', rollover prev %d, curr %d\n",
                                  self.times[i], e.key, p, v)
                            r -= numpy.uint64(1L << e.width)
                        elif v == 0:
                            # Spurious reset
                            # This happens with the IB counters.
                            # Ignore this value, use previous instead.
                            # TODO Interpolate or something.
                            trace("time %d, counter `%s', suspicious zero, prev %d\n",
                                  self.times[i], e.key, p)
                            v = p # Ugh.
                        elif (type_name == 'ib_ext' or type_name == 'ib_sw') or (type_name == 'cpu' and e.key == 'iowait'):
                            # We will assume a spurious reset, 
                            # and the reset happened at the start of the counting period.
                            # This happens with IB ext counters.
                            #   A[i,j] = v + A[i-1,j] 
                            # and
                            #   A[i,j] = v - r
                            # Therefore
                            #   A[i-1,j] = -r 
                            # or
                            #          r = - A[i-1,j]
                            r = numpy.uint64(0) - A[i-1,j] 
                            if KEEP_EDITS:
                                self.edit_flags.append("(time %d, host `%s', type `%s', dev `%s', key `%s')" %
                                                   (self.times[i],host.name,type_name,dev_name,e.key))
                            fudged = True
                        elif type_name == 'net' and (dev_name == 'mic0' or dev_name == 'mic1') and i == (len(self.times)-1):
                            # mic counters are reset at the end of a job ignore the last datapoint
                            v = p
                            fudged = True

                        if type_name not in ['ib', 'ib_ext'] and (fudged == False):
                            width = e.width if e.width else 64
                            if ( v - p ) % (2**width) > 2**(width-1):
                                # This counter rolled more than half of its range
                                self.logoverflow(host.name, type_name, dev_name, e.key)

                    A[i, j] = v - r
                    p = v
            if e.mult:
                for i in range(0, m):
                    A[i, j] *= e.mult
        return A

    def logoverflow(self, host_name, type_name, dev_name, key_name):
        if type_name not in self.overflows:
            self.overflows[type_name] = dict()
        if dev_name not in self.overflows[type_name]:
            self.overflows[type_name][dev_name] = dict()
        if key_name not in self.overflows[type_name][dev_name]:
            self.overflows[type_name][dev_name][key_name] = set()

        self.overflows[type_name][dev_name][key_name].add(host_name)

    def process_stats(self):
        for host in self.hosts.itervalues():
            host.stats = {}
            for type_name, raw_type_stats in host.raw_stats.iteritems():
                stats = host.stats[type_name] = {}
                schema = self.schemas[type_name]
                for dev_name, raw_dev_stats in raw_type_stats.iteritems():
                    stats[dev_name] = self.process_dev_stats(host, type_name, schema,
                                                             dev_name, raw_dev_stats)
            del host.raw_stats
        amd64_pmc.process_job(self)
        intel_process.process_job(self)
        phys_cores_process.process_job(self)
        # Clear mult, width from schemas. XXX
        for schema in self.schemas.itervalues():
            for e in schema.itervalues():
                e.width = None
                e.mult = None
        return True
    
    def aggregate_stats(self, type_name, host_names=None, dev_names=None):
        """Job.aggregate_stats(type_name, host_names=None, dev_names=None)
        """
        # TODO Handle control registers.
        schema = self.schemas[type_name]
        m = len(self.times)
        n = len(schema)
        A = numpy.zeros((m, n), dtype=numpy.uint64) # Output.       
        nr_hosts = 0
        nr_devs = 0
        if host_names:
            host_list = [self.hosts[name] for name in host_names]
        else:
            host_list = self.hosts.itervalues()
        for host in host_list:
            type_stats = host.stats.get(type_name)
            if not type_stats:
                continue
            nr_hosts += 1
            if dev_names:
                dev_list = [type_stats[name] for name in dev_names]
            else:
                dev_list = type_stats.itervalues()
            for dev_stats in dev_list:
                A += dev_stats
                nr_devs += 1
        return (A, nr_hosts, nr_devs)

    def get_stats(self, type_name, dev_name, key_name):
        """Job.get_stats(type_name, dev_name, key_name)
        Return a dictionary with keys host names and values the vector
        of stats for the given type, dev, and key.
        """
        schema = self.get_schema(type_name)
        index = schema[key_name].index
        host_stats = {}
        for host_name, host in self.hosts.iteritems():
            host_stats[host_name] = host.stats[type_name][dev_name][:, index]
        return host_stats


def from_acct(acct, stats_home, host_list_dir, batch_acct, open_xdmod=False):
    """from_acct(acct, stats_home)
    Return a Job object constructed from the appropriate accounting data acct using
    stats_home as the base directory, running all required processing.
    """
    if open_xdmod:
        job = OpenXDMoDJob(acct, stats_home, host_list_dir, batch_acct)
    else:
        job = Job(acct, stats_home, host_list_dir, batch_acct)
    job.gather_stats() and job.munge_times() and job.process_stats()
    return job


def from_id(id, **kwargs):
    """from_id(id, acct_file=None, acct_path=sge_acct_path, use_awk=True)
    Return Job object for the job with SGE id ID, or None if no such job was found.
    """
    acct = sge_acct.from_id(id, **kwargs)
    if acct:
        return from_acct(acct)
    else:
        return None


class OpenXDMoDJob(Job):
    """

    """

    def get_stats_paths(self):
        raw_host_stats_dir = os.path.join(self.raw_stats_dir, self.name+self.name_ext)
        job_start = self.job.start_time - RAW_STATS_TIME_PAD
        job_end = self.job.end_time + RAW_STATS_TIME_PAD
        path_list = []
        try:
            for ent in os.listdir(raw_host_stats_dir):
                base, dot, ext = ent.partition(".") if '.' in ent else (ent, '.', 'gz')
                if not base.isdigit():
                    continue
                if ext != "gz":
                    continue
                # Support for filenames of the form %Y%m%d
                if re.match('^[0-9]{4}[0-1][0-9][0-3][0-9]$', base):
                    base = (datetime.datetime.strptime(base,"%Y%m%d") - datetime.datetime(1970,1,1)).total_seconds()
                # Prune to files that might overlap with job.
                ent_start = long(base)
                ent_end = ent_start + 2*RAW_STATS_TIME_MAX
                if ((ent_start <= job_start) and (job_start <= ent_end)) or ((ent_start <= job_end) and (job_end <= ent_end)) or (max(job_start, ent_start) <= min(job_end, ent_end)) :
                    full_path = os.path.join(raw_host_stats_dir, ent)
                    path_list.append((full_path, ent_start))
                    self.trace("path `%s', start %d", full_path, ent_start)
        except Exception as exc:
            logging.error("get_stats_paths job %s. %s", self.job.id, exc)

        path_list.sort(key=lambda tup: tup[1])
        return path_list

    def gather_stats(self):
        host_list = []

        if "host_list" in self.acct:
            host_list = self.acct['host_list']
            if host_list == ["None assigned"]:
                host_list = []

        if len(host_list) == 0 and self.end_time - self.start_time > 0:
            self.error("empty host list")
            return False

        for hidx, host_name in enumerate(host_list):
            # TODO Keep bad_hosts.
            try:
                host_name = host_name.split('.')[0]
            except:
                pass

            host = OpenXDMoDHost(self, host_name, self.stats_home + '/archive', self.batch_acct.name_ext, hidx == 0)

            if host.gather_stats():
                self.hosts[host_name] = host

        if not self.hosts:
            self.error("no good hosts")
            return False
        return True


class OpenXDMoDHost(Host):

    def gather_stats(self):
        path_list = self.get_stats_paths()
        if len(path_list) == 0:
            self.error("no stats files overlapping job")
            return False

        # read_stats_file() and parse_stats() append stats records
        # into lists of tuples in self.raw_stats.  The lists will be
        # converted into numpy arrays below.
        for path, start_time in path_list:
            try:
                with open(path) as file:
                    self.read_stats_file(file)
            except IOError as ioe:
                self.error("read error for file %s", path)

        return self.raw_stats
