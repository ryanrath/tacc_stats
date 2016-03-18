#!/usr/bin/env python

import os
import codecs

class TorqueAcct(object):
    """ Process accounting files from torque """

    def __init__(self, acct_file, host_name_ext):

        self.ncpus = 0
        self.nodes = 0
        self.fieldmapping = {
                "account": ["account", str],
                "queue": ["partition", str],
                "session": ["session", str],
                "owner": ["username", str],
                "group": ["group", str],
                "exec_host": ["host_list", self.parsehostlist],
                "jobname": ["jobname", str],
                "user": ["user", str],
                "Exit_status": ["status", int],
                "Error_Path": ["error_path", str],
                "Output_Path": ["output_path", str],
                "ctime": ["submit", int],
                "etime": ["eligible_time", int],
                "qtime": ["queue_time", int],
                "start": ["start_time", int],
                "end":   ["end_time", int],
                "Resource_List.ncpus": ["requested_cpus", int], 
                "Resource_List.walltime": ["requested_walltime", str],
                "Resource_List.nodect": ["requested_node", int],
                "Resource_List.nodes": ["requested_nodelist", str],
                "Resource_List.host": ["requested_host", str],
                "Resource_List.neednodes": ["requested_neednodes", str],
                "Resource_List.mem": ["requested_memory", str],
                "resources_used.cput": ["cpu_time", str],
                "resources_used.mem": ["mem_used", str],
                "resources_used.vmem": ["vmem_used", str],
                "resources_used.walltime": ["wall_time", str]
        }

        self.batch_kind = 'TORQUE'
        self.acct_file = acct_file
        if len(host_name_ext) > 0:
            self.name_ext = '.'+host_name_ext
        else:
            self.name_ext = ""

    def get_host_list_path(self,acct,host_list_dir):
        return None

    def reader(self,start_time=0, end_time=9223372036854775807L, seek=0):
        """ The file format of the Torque logs is sufficently different from the
            others to warrant its own reader implmentation
        """
        filelist = []
        if os.path.isdir(self.acct_file):
            for dir_name, subdir_list, file_list in os.walk(self.acct_file):
                for fname in file_list:
                    filelist.append( os.path.join(self.acct_file,dir_name,fname) )
        else:
            filelist = [ self.acct_file ]
    
        for fname in filelist:
            filep = codecs.open(fname, "r", "utf-8", errors="replace")
            if seek:
                filep.seek(seek, os.SEEK_SET)
    
            for line in filep:
                 acct = self.parseline(line)
                 if acct != None and start_time <= acct['end_time'] and acct['end_time'] < end_time:
                     yield acct

    def parseline(self, line):
        tokens = line.split(";")
        if len(tokens) < 4:
            return None

        timestamp = tokens[0]
        recordtype = tokens[1]
        jobid = tokens[2]
        record = ";".join(tokens[3:]).strip()

        if recordtype != "E":
            return None

        parts = jobid.split(".") 
        acct = {"local_job_id": int(parts[0]), "id": jobid}

        jobrecs = record.split(" ")
        for jobrec in jobrecs:
            items = jobrec.split("=")
            if len(items) == 2:
                try:
                    mapping = self.fieldmapping[items[0]]
                    acct[mapping[0]] = mapping[1](items[1])
                except KeyError as e:
                    print line
                    raise e
                except ValueError as e:
                    print line
                    raise e

        acct['ncpus'] = self.ncpus
        acct['nodes'] = self.nodes

        return acct

    def parsehostlist(self, hostlist):

        self.ncpus = 0
        hosts = {}
        for item in hostlist.split("+"):
            tokens = item.split("/")
            if len(tokens) == 2:
                hosts[tokens[0]] = 1
                self.ncpus += 1

        self.nodes = len(hosts)
        return hosts.keys()

