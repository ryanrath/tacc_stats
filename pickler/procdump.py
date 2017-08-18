#!/usr/bin/python
import gzip
import sys
import base64
import StringIO
import re
import operator
from linuxhelpers import parsecpusallowed

class ProcFilter:
    def __init__(self):
        self.knownprocesses = set(['wnck-applet',
            'ibrun', 'mpispawn', 'mpirun_rsh',
            'munged', 'nscd', 'orterun', 'perl',
            'wc', 'which', 'vncserver', 'vncconfig', 'vim', 'vi', 'usleep', 'uname',
            'uniq', 'tr', 'top', 'time', 'tee', 'tail', 'sync-to-pcp1',
            'sync-pcp-logs', 'sshd:', 'sshd', 'sort', 'ssh', 'srun', 'sh', 'squeue',
            'slurmstepd:', 'slurmstepd', 'slurm_script', 'sleep', 'sinfo', 'sed',
            'screen', 'scontrol', 'sbcast', 'rsync', 'pulseaudio',
            'pulse/gconf-helper', 'ps', 'pmi_proxy', 'nrpe', 'nedit',
            'notification-area-applet', 'nautilus', 'mv', 'more', 'mktemp', 'mkdir',
            'ln', 'ldd', 'lsof', 'hostname', 'gzip', 'gvfsd-trash', 'gvfsd-metadata',
            'gvfsd-http', 'gvfsd-computer', 'gvfsd', 'gvfs-gdu-volume-monitor', 'grep',
            'gnome-terminal', 'gnome-settings-daemon', 'gnome-session',
            'gnome-pty-helper', 'gnome-panel', 'gnome-keyring-daemon', 'gedit',
            'gdm-user-switch-applet', 'gconfd-2', 'gawk', 'fgrep', 'emacs', 'echo',
            'dmtcp_restart_s', 'dmtcp_restart', 'dmtcp_checkpoint',
            'dmtcp_coordinator', 'dmtcp_coordinat', 'dmtcp_command', 'dmesg', 'df',
            'dbus-launch', 'dbus-daemon', 'cut', 'crond', 'cp', 'csh', 'cd',
            'clock-applet', 'cat', 'bash', 'bonobo-activation-server', 'awk', 'SCREEN',
            'hald-addon-acpi', 'hald',
            'CROND', '/usr/lib64/nagios/plugins/check_procs', '/etc/vnc/Xvnc-core'])
        
        self.procfilter = re.compile('^/user/[a-z0-9]+/\.vnc/xstartup|^/var\/spool\/slurmd.+|.*pmi_proxy$')

    def filter(self, command):
        """ returns true if the command should be filtered (ie it is a known non-HPC application) """
        if command in self.knownprocesses:
            return True
        if self.procfilter.search(command):
            return True
    
        return False

    def allow(self, command):
        return not self.filter(command)

class TaccProcDump:
    """ Process the proc information from tacc_stats version >= 2.1 """
    def __init__(self):
        self.procfilter = ProcFilter()
        self.commandre_v1 = re.compile("(.*)/([0-9]*)$")
        self.commandre_v2 = re.compile("(.*)/([0-9]+)/([0-9,-]+)/([0-9,-]+)$")

    def getproclist(self, job, uid=None):
        if job.get_schema('proc') == None:
            return dict()

        if 'Cpus_allowed_list' in job.get_schema('proc'):
            return self.getproc_v1(job, uid)
        else:
            return self.getproc_v2(job, uid)

    def getproc_v2(self, job, uid):
        outprocs = dict()

        for host in job.hosts.itervalues():
            if "proc" in host.stats.keys():
                for procstr, data in host.stats['proc'].iteritems():

                    m = self.commandre_v2.search(procstr)
                    if m == None:
                        continue
                    command = m.group(1)

                    if self.procfilter.allow(command):
                        procuid = data[0, job.get_schema('proc')['Uid'].index]
                        if uid == None or uid == procuid:
                            outprocs[command] = parsecpusallowed(m.group(3))

            if len(outprocs) > 0:
                break

        # sort results by the cpus allowed value. This will
        # prefer commands that were pinned to the fewest cpus (ie are most likely to be parallel codes)
        return [x[0] for x in sorted(outprocs.items(), key=lambda x: len(x[1]))]

    def getproc_v1(self, job, uid):
        outprocs = dict()

        for host in job.hosts.itervalues():
            if "proc" in host.stats.keys():
                for command, data in host.stats['proc'].iteritems():

                    m = self.commandre.search(command)
                    if m != None:
                        command = m.group(1)

                    if self.procfilter.allow(command):
                        procuid = data[0, job.get_schema('proc')['Uid'].index]
                        mincpuallowed = min(data[:,job.get_schema('proc')['Cpus_allowed_list'].index])

                        if uid == None or uid == procuid:
                            outprocs[command] = mincpuallowed

            if len(outprocs) > 0:
                break

        # sort results by the cpus allowed value. This will
        # prefer commands that were pinned to the fewest cpus (ie are most likely to be parallel codes)
        return [x[0] for x in sorted(outprocs.items(), key=operator.itemgetter(1))]

class ProcDump:
    """ This class parses the output of the procdump information from the (deprecated) CCR branch 
        of tacc_stats. This data is base64 encoded dump of various contents of files under /proc
    """
    def __init__(self):
        self.uidprocs= dict()
        self.procfilter = ProcFilter()

    def __str__(self):
        return str(self.getproclist())

    def getproclist(self, uid=None):
        allprocs = set()

        if uid != None:
            uid = str(uid)
            if uid in self.uidprocs:
                for proc in self.uidprocs[uid]:
                    allprocs.add( self.getcommand(proc) )
                return list(allprocs)

        for procs in self.uidprocs.itervalues():
            for proc in procs:
                allprocs.add( self.getcommand(proc) )

        return list(allprocs)

    def strippath(self, command):
        paths = ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/', '/usr/libexec/', '/usr/local/bin/', '-' ]
        for path in paths:
            if command.startswith(path):
                return command[len(path):].strip('";')
        return command
    
    def getcommand(self, procname):
        shells = ["sh", "csh", "tcsh", "bash", "perl", "python"]
    
        cmdline = procname.split(" ")
        command = self.strippath(cmdline[0])
    
        if command in shells:
            command = None
            for s in cmdline[1:]:
                if not s.startswith("-"):
                    command = self.strippath(s)
                    break
        return command
    
    def blacklisted(self, commandline):
        command = self.getcommand(commandline)
        if command == None:
            return True
        return self.procfilter.filter(command)

    def parse(self,indata):

        if len(indata) < 40:
            return

        if indata.startswith("% procdump "):
            slicestart = 11
        else:
            slicestart = 10

        decoded = StringIO.StringIO(base64.b64decode(indata[slicestart:]))
        gzo = gzip.GzipFile(mode="rb",fileobj=decoded)

        (START, STATUS_LEN, STATUS_NAME, UIDSEARCH, CMDLINE_LEN, CMDLINE_NAME) = range(6)

        state = START
        pid = -1
        uidpids = dict()
        processes = dict()

        for line in gzo:
            if state == START:
                if "/status" in line:
                    m = re.search("^/proc/([0-9]+)/status", line)
                    if m:
                        pid = m.group(1)
                        state = STATUS_LEN
                        continue
                if "/cmdline" in line:
                    m = re.search("^/proc/([0-9]+)/cmdline", line)
                    if m:
                        pid = m.group(1)
                        state = CMDLINE_LEN
                continue
            if state == STATUS_LEN:
                state = STATUS_NAME
                continue
            if state == STATUS_NAME:
                if pid not in processes:
                    processes[pid] = line.split()[1]
                state = UIDSEARCH
                continue
            if state == UIDSEARCH:
                if line.startswith("Uid:"):
                    m = re.search("^Uid:\t+([0-9]+).*", line)
                    if m:
                        uid = m.group(1)
                        if uid not in uidpids:
                            uidpids[uid] = set()
                        uidpids[uid].add(pid)
                    state = START
                continue
            if state == CMDLINE_LEN:
                state = CMDLINE_NAME
                continue
            if state == CMDLINE_NAME:
                try:
                    processes[pid] = unicode(line.replace("\0", " ").rstrip())
                except:
                    # If the cmdline is not unicode, then don't replace the proc/status Name: field
                    pass
                state = START
                continue

        # post process
        for uid,pids in uidpids.iteritems():
            tmp = set()
            for pid in pids:
                procname = processes[pid]
                if not self.blacklisted(procname):
                    tmp.add(procname)

            if len(tmp) > 0:
                self.uidprocs[uid] = tmp

""" This helper function is a bare-bones parser to easily extract the """
""" procDump information from a raw taccstats output file. """

def getProcdumpData( filename, jid ):

    procParser = ProcDump()
    lineNum = 0
    cmd = ""
    procDumpData = []
    running = False
    ending = False
    procDumpLines = []
    try:
        with gzip.open(filename) as f:
            for line in f:
                # store line number
                lineNum += 1
                # test if its already running
                if line[0].isdigit():
                    jobs=line.strip().split()[1].split(',')
                    if jid in jobs:
                        running = True
                # test if it is starting
                if re.match("% *begin", line) != None:
                    if line.strip().split()[-1] == jid:
                        running = True
                # test if it is ending
                if re.match("% *end", line) != None:
                    if line.strip().split()[-1] == jid:
                        ending = True
                # test if its a procdump line and job is running
                if re.match("% *procdump", line) != None and (running or ending):
                    procParser.parse(line)
                    if ending:
                        break
    except TypeError as e:
        print e
        pass
    
    return procParser

if __name__ == '__main__':
    print getProcdumpData( sys.argv[1], sys.argv[2] )

