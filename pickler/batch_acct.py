import csv, os, datetime, glob, re
import codecs
import logging
import MySQLdb as mdb
from torque_acct import TorqueAcct
from parsers import TimeFixer

def factory(kind, acct_file, host_name_ext='', resource_id=None, config=None):
  if kind == 'SGE':
    return SGEAcct(acct_file,host_name_ext)
  elif kind == 'SLURM':
    return SLURMAcct(acct_file,host_name_ext)
  elif kind == 'SLURMNative':
    return SLURMNativeAcct(acct_file,host_name_ext)
  elif kind == 'SLURMNative2':
    return SLURMNative2Acct(acct_file,host_name_ext, resource_id, config)
  elif kind == 'XDcDB':
    return XDcDBAcct(acct_file,host_name_ext)
  elif kind == 'TORQUE':
    return TorqueAcct(acct_file, host_name_ext)

def special_char_stripper(fp):
   for line in fp:
      yield line.replace('\r', '').encode('utf-8')

class BatchAcct(object):

  def __init__(self,batch_kind,acct_file,host_name_ext,delimiter=":"):
    self.batch_kind=batch_kind
    self.acct_file=acct_file
    self.field_names = [tup[0] for tup in self.fields]
    if len(host_name_ext) > 0:
        self.name_ext = '.'+host_name_ext
    else:
        self.name_ext = ""
    self.delimiter = delimiter 

  def fixuprecord(self, d):
    pass

  def postprocessrecord(self, d):
      return True

  def reader(self,start_time=0, end_time=9223372036854775807L, seek=0):
    """reader(start_time=0, end_time=9223372036854775807L, seek=0)
    Return an iterator for all jobs that finished between start_time and end_time.
    """
    datere = re.compile('^([0-9]{4})-([0-9]{2})-([0-9]{2})\.[a-z]+')

    filelist = []
    if os.path.isdir(self.acct_file):
        for dir_name, subdir_list, file_list in os.walk(self.acct_file):
            for fname in file_list:
                mtch = datere.match(fname)
                if mtch:
                    # date stamped filename
                    filets = (datetime.datetime(year=int(mtch.group(1)), month=int(mtch.group(2)), day=int(mtch.group(3))) - datetime.datetime(1970, 1, 1)).total_seconds() + 24*3600
                    if filets < start_time:
                        continue

                filelist.append( os.path.join(self.acct_file,dir_name,fname) )
    else:
        filelist = [ self.acct_file ]

    filelist.sort()

    for fname in filelist:
        record_count = 0
        skip_count = 0
        file = codecs.open(fname, "r", "utf-8", errors="replace")
        if seek:
            file.seek(seek, os.SEEK_SET)

        for d in csv.DictReader(special_char_stripper(file), delimiter=self.delimiter, fieldnames=self.field_names):
          try:
            for n, t, x in self.fields:
              d[n] = t(d[n])
          except Exception as e:
            #print e
            pass

          ## Clean up when colons exist in job name
          if None in d:
            self.fixuprecord(d)

          if self.postprocessrecord(d) == False:
              skip_count += 1
              continue

          if d['end_time'] == 0:
              # Skip jobs that have no defined end time (occurs when certain schedulers do not allocate resources for job)
              skip_count += 1
              continue

          # Accounting records with pe_taskid != NONE are generated for
          # sub_tasks of a tightly integrated job and should be ignored.
          if start_time <= d['end_time'] and d['end_time'] < end_time:
            if self.batch_kind=='SGE' and d['pe_taskid'] == 'NONE':
              record_count += 1
              yield d
            elif self.batch_kind=='SLURM':
              record_count += 1
              yield d

        logging.debug('Processed %s records, %s skipped for %s', record_count, skip_count, fname)
        file.close()


  def from_id_with_file_1(self, id, seek=0):
    for acct in self.reader(seek=seek):
      if acct['id'] == id:
        return acct
    return None

class SGEAcct(BatchAcct):

  def __init__(self, acct_file, host_name_ext):
    self.fields = (
      ('queue',           str, 'Name of the cluster queue in which the job has run.'), # sge 'qname'
      ('hostname',        str, 'Name of the execution host.'),
      ('group',           str, 'The effective group id of the job owner when executing the job.'),
      ('owner',           str, 'Owner of the Sun Grid Engine job.'),
      ('name',            str, 'Job name.'), # sge 'job_name'
      ('id',              str, 'Job identifier.'), # sge 'job_number'
      ('account',         str, 'An account string as specified by the qsub(1) or qalter(1) -A option.'),
      ('priority',        int, 'Priority value assigned to the job corresponding to the priority parameter in the queue configuration (see queue_conf(5)).'),
      ('submission_time', int, 'Submission time (GMT unix time stamp).'),
      ('start_time',      int, 'Start time (GMT unix time stamp).'),
      ('end_time',        int, 'End time (GMT unix time stamp).'),
      ('failed',          int, 'Indicates the problem which occurred in case a job could not be started on the execution host (e.g. because the owner of the job did not have a valid account on that machine). If Sun Grid Engine tries to start a job multiple times, this may lead to multiple entries in the accounting file corresponding to the same job ID.'),
      ('exit_status',     int, 'Exit status of the job script (or Sun Grid Engine specific status in case of certain error conditions). The exit status is determined by following the normal shell conventions. If the command terminates normally the value of the command is its exit status. However, in the case that the command exits abnormally, a value of 0200 (octal), 128 (decimal) is added to the value of the command to make up the exit status. For example: If a job dies through signal 9 (SIGKILL) then the exit status becomes 128 + 9 = 137.'),
      ('ru_wallclock',    int, 'Difference between end_time and start_time.'),
      ('ru_utime',      float, ''), # Bogus.
      ('ru_stime',      float, ''), # Bogus.
      ('ru_maxrss',     float, ''), # Bogus.
      ('ru_ixrss',        int, ''), # Bogus.
      ('ru_ismrss',       int, ''), # Bogus.
      ('ru_idrss',        int, ''), # Bogus.
      ('ru_isrss',        int, ''), # Bogus.
      ('ru_minflt',       int, ''), # Bogus.
      ('ru_majflt',       int, ''), # Bogus.
      ('ru_nswap',      float, ''), # Bogus.
      ('ru_inblock',    float, ''), # Bogus.
      ('ru_oublock',      int, ''), # Bogus.
      ('ru_msgsnd',       int, ''), # Bogus.
      ('ru_msgrcv',       int, ''), # Bogus.
      ('ru_nsignals',     int, ''), # Bogus.
      ('ru_nvcsw',        int, ''), # Bogus.
      ('ru_nivcsw',       int, ''), # Bogus.
      ('project',         str, 'The project which was assigned to the job.'),
      ('department',      str, 'The department which was assigned to the job.'),
      ('granted_pe',      str, 'The parallel environment which was selected for that job.'), # '16way'
      ('slots',           int, 'The number of slots which were dispatched to the job by the scheduler.'),
      ('task_number',     int, 'Array job task index number.'),
      ('cpu',           float, 'The cpu time usage in seconds.'), # Bogus.
      ('mem',           float, 'The integral memory usage in Gbytes cpu seconds.'), # Bogus.
      ('io',            float, 'The amount of data transferred in input/output operations.'), # Bogus
                                                            ('category',        str, 'A string specifying the job category.'),
      ('iow',           float, 'The io wait time in seconds.'), # Bogus.
      ('pe_taskid',       str, 'If this identifier is set the task was part of a parallel job and was passed to Sun Grid Engine via the qrsh -inherit interface.'),
      ('maxvmem',       float, 'The maximum vmem size in bytes.'), # Bogus.
      ('arid',            int, 'Advance reservation identifier. If the job used resources of an advance reservation then this field contains a positive integer identifier otherwise the value is 0.'),
      ('ar_submission_time', int, 'If the job used resources of an advance reservation then this field contains the submission time (GMT unix time stamp) of the advance reservation, otherwise the value is 0.'),
      )
    
    BatchAcct.__init__(self,'SGE',acct_file,host_name_ext)

  def keymap(key): # Batch account keywords are based on SGE names for
                   # historical reasons
    return key

  def get_host_list_path(self,acct,host_list_dir):
    """Return the path of the host list written during the prolog."""
    # Example: /share/sge6.2/default/tacc/hostfile_logs/2011/05/19/prolog_hostfile.1957000.IV32627
    start_date = datetime.date.fromtimestamp(acct['start_time'])
    base_glob = 'prolog_hostfile.' + acct['id'] + '.*'
    for days in (0, -1, 1):
      yyyy_mm_dd = (start_date + datetime.timedelta(days)).strftime("%Y/%m/%d")
      full_glob = os.path.join(host_list_dir, yyyy_mm_dd, base_glob)
      for path in glob.iglob(full_glob):
        return path
    return None




class SLURMAcct(BatchAcct):

  def __init__(self,acct_file,host_name_ext):
    
    self.fields = (
      ('id', str, 'Job ID'),
      ('uid', str, 'User UNIX ID'),
      ('project', str, 'SLURM account string'),
      ('yesno', str, 'Not sure yet, need to ask Karl'),
      ('start_time', int, 'Epoch time job started'),
      ('end_time', int, 'Epoch time job ended'),
      ('queue_time', int, 'Epoch time job entered queue'),
      ('queue', str, 'Name of the SLURM partition'),
      ('unknown', int, 'minutes requested?'),
      ('name', str, 'Name given to job by user'),
      ('status', str, 'SLURM job finish state: COMPLETED, FAILED, etc.'),
      ('nodes', int, 'Nodes requested'),
      ('cores', int, 'CPU cores requested')
      )
    
    BatchAcct.__init__(self,'SLURM',acct_file,host_name_ext)

  def get_host_list_path(self,acct,host_list_dir):
    """Return the path of the host list written during the prolog."""
    start_date = datetime.date.fromtimestamp(acct['start_time'])
    base_glob = 'hostlist.' + str(acct['id'])
    for days in (0, -1, 1):
      yyyy_mm_dd = (start_date + datetime.timedelta(days)).strftime("%Y/%m/%d")
      full_glob = os.path.join(host_list_dir, yyyy_mm_dd, base_glob)
      for path in glob.iglob(full_glob):
        return path
    return None

  def fixuprecord(self, d):
    """ Try to handle case where the name field contains the delimiter character """
    num_cols = len(d[None])
    for cols in range(num_cols):
      d['name'] = d['name']+':'+d['status']        
      d['status'] = str(d['nodes'])
      d['nodes'] = d['cores']
      d['cores'] = d[None][0]
      del d[None][0]
    d['nodes'] = int(d['nodes'])
    d['cores'] = int(d['cores'])
    del d[None]

class SLURMNativeAcct(BatchAcct):
  """ Process accounting data produced by the sacct command with the following """
  """ flags. """
  """ SLURM_TIME_FORMAT=%s """
  """ sacct --allusers --parsable2 --noheader --allocations --allclusters      """
  """     --format jobid,cluster,partition,account,group,gid,user,uid,submit,eligible,start,end,exitcode,State,nnodes,ncpus,reqcpus,nodelist,jobname,timelimit """
  """     --state CA,CD,F,NF,TO """

  def __init__(self,acct_file,host_name_ext):

    self.fields = (
      ('id',                          str, 'Job identifier'),
      ('cluster',                     str, 'Job cluster'),
      ('partition',                   str, 'Job partition'),
      ('account',                     str, 'Job account'),
      ('group',                       str, 'Group name of the job owner'),
      ('gid',                         int, 'GID of the job owner'),
      ('user',                        str, 'User that is running the job'),
      ('uid',                         int, 'UID of the job owner'),
      ('submit',                      int, 'Time the job was submitted'),
      ('eligible',                    int, 'Time job was eligible to run (unix time stamp)'),
      ('start_time',                  int, 'Time job started to run (unix time stamp)'),
      ('end_time',                    int, 'Time job ended (unix time stamp)'),
      ('exit_code',                   str, 'Exit code of job'),
      ('exit_status',                 str, 'Exit status of the job'),
      ('nodes',                       int, 'Number of nodes'),
      ('ncpus',                       int, 'Number of cpus'),
      ('reqcpus',                     int, 'Number of cores requested'),
      ('node_list',                   str, 'Nodes used in job'),
      ('jobname',                     str, 'Job name'),
      ('timelimit',                   str, 'Assigned time limit')
      )

    BatchAcct.__init__(self,'SLURM',acct_file,host_name_ext,"|")

  def get_host_list_path(self,acct,host_list_dir):
    """Return the path of the host list written during the prolog."""
    start_date = datetime.date.fromtimestamp(acct['start_time'])
    base_glob = 'hostlist.' + str(acct['id'])
    for days in (0, -1, 1):
      yyyy_mm_dd = (start_date + datetime.timedelta(days)).strftime("%Y/%m/%d")
      full_glob = os.path.join(host_list_dir, yyyy_mm_dd, base_glob)
      for path in glob.iglob(full_glob):
        return path
    return None

  def fixuprecord(self, d):
    """ Try to handle case where the name field contains the delimiter character """
    num_cols = len(d[None])
    for cols in range(num_cols):
      d['jobname'] = d['jobname']+'|'+d['timelimit']        
      d['timelimit'] = d[None][0]
      del d[None][0]
    del d[None]

  def get_host_list(self, nodelist):
    
    if nodelist is None:
        return []

    open_brace_flag = False
    close_brace_flag = False
    host_list = []
    tmp_host = ""
    # get a list of all the nodes and store them in host_host
    for c in nodelist:
        if c == '[':
            open_brace_flag = True
        elif c == ']':
            close_brace_flag = True
        if ( c == ',' and not close_brace_flag and not open_brace_flag ) or (c == ',' and close_brace_flag):
            host_list.append(tmp_host)
            tmp_host = ""
            close_brace_flag = False
            open_brace_flag = False
        else:
            tmp_host += c
    if tmp_host:
        host_list.append(tmp_host)

    # parse through host_list and expand the hostnames
    host_list_expanded = []
    for h in host_list:
        if '[' in h:
            node_head = h.split('[')[0]
            node_tail = h.split('[')[1][:-1].split(',')
            for n in node_tail:
                if '-' in n:
                    num = n.split('-')
                    for x in range(int(num[0]), int(num[1])+1):
                        host_list_expanded.append(node_head + str("%02d" % x))
                else:
                    host_list_expanded.append(node_head + n)
        else:
            host_list_expanded.append(h)

    return host_list_expanded

  def reader(self,start_time=0, end_time=9223372036854775807L, seek=0):
      for a in super(SLURMNativeAcct,self).reader(start_time, end_time, seek):
          a['host_list'] = self.get_host_list(a['node_list'])
          if len(a['host_list']) > 0:
            a['hostname'] = a['host_list'][0]
          yield a

class SLURMNative2Acct(SLURMNativeAcct):
  """ Process accounting data produced by the sacct command used by tacc_stats """

  def __init__(self, acct_file, host_name_ext, resource_id, config):

    self.starttimeconverter = TimeFixer('America/Los_Angeles', True)
    self.endtimeconverter = TimeFixer('America/Los_Angeles', False)

    self.fields = (
      ('id',                          str, 'Job identifier'),
      ('user',                        str, 'User that is running the job'),
      ('project',                     str, 'Job account'),
      ('start_time',                  self.starttimeconverter, 'Time job started to run'),
      ('end_time',                    self.endtimeconverter, 'Time job ended'),
      ('queue_time',                  self.starttimeconverter, 'Time the job was submitted'),
      ('queue',                       str, 'Job partition'),
      ('timelimit',                   str, 'Assigned time limit'),
      ('name',                        str, 'Job name'),
      ('status',                      str, 'Exit status of the job'),
      ('nodes',                       int, 'Number of nodes'),
      ('cores',                       int, 'Number of cores requested'),
      ('node_list',                   str, 'Nodes used in job'),
      )

    # The job array regular expression should match:
    #   1) normal job 2342323
    #   2) job array  344354_32
    #   3) job array range 23423_[1-2,5]
    #
    # mtch.group(2) is None if there is no job array index otherwise
    # it is the job array index (or the first job array index for a range).
    self.jobarraydetect = re.compile(r"(\d+)(?:_\[?(\d+)[\d,-]*\]?)?")

    if config:
        dbconfig = config['accountdatabase']
        self.xdmod_db = mdb.connect(db=dbconfig['dbname'], read_default_file=dbconfig["defaultsfile"])
    self.uidcache = {}

    self.resource_id = resource_id

    BatchAcct.__init__(self,'SLURM',acct_file,host_name_ext,"|")

  def fixuprecord(self, d):
      pass

  def postprocessrecord(self, d):
    mtch = self.jobarraydetect.match(d['id'])

    if mtch == None:
        print "Invalid job id ", d
        return False

    d['local_jobid'] = mtch.group(1)

    if mtch.group(2) != None:
        d['job_array_index'] = mtch.group(2)

    if 'user' in d:
        if d['user'] in self.uidcache:
            d['uid'] = self.uidcache[d['user']]
        else:
            cur = self.xdmod_db.cursor()
            cur.execute("""
SELECT
    sa.uid
FROM
    modw.systemaccount sa,
    modw.resourcefact rf,
    modw.resourcefact rr
WHERE
    rr.id = %s
    AND rf.organization_id = rr.organization_id
    AND sa.username = %s
    AND sa.resource_id = rf.id
    AND sa.uid IS NOT NULL""", (self.resource_id, d['user']))

            result = cur.fetchone()
            if result:
                d['uid'] = result[0]
                self.uidcache[d['user']] = result[0]

    return True

class XDcDBAcct(BatchAcct):
  """ Process accounting data produced by grabbing it from the modw.jobfact 
      table (which in turn comes from the XDcDB).
  """

  def __init__(self,acct_file,host_name_ext):

    self.fields = (
      ('id',                          str, 'Job identifier'),
      ('partition',                   str, 'Job partition'),
      ('account',                     str, 'Job account'),
      ('user',                        str, 'User that is running the job'),
      ('submit',                      int, 'Time the job was submitted'),
      ('start_time',                  int, 'Time job started to run (unix time stamp)'),
      ('end_time',                    int, 'Time job ended (unix time stamp)'),
      ('nodes',                       int, 'Number of nodes'),
      ('ncpus',                       int, 'Number of cpus'),
      ('node_list',                   str, 'Nodes used in job'),
      ('jobname',                     str, 'Job name')
      )

    BatchAcct.__init__(self,'XDcDB',acct_file,host_name_ext,"|")

  def get_host_list_path(self,acct,host_list_dir):
    """Return the path of the host list written during the prolog."""
    start_date = datetime.date.fromtimestamp(acct['start_time'])
    base_glob = 'hostlist.' + str(acct['id'])
    for days in (0, -1, 1):
      yyyy_mm_dd = (start_date + datetime.timedelta(days)).strftime("%Y/%m/%d")
      full_glob = os.path.join(host_list_dir, yyyy_mm_dd, base_glob)
      for path in glob.iglob(full_glob):
        return path
    return None

  def get_host_list(self, nodelist):
    return nodelist.split(",")

  def reader(self,start_time=0, end_time=9223372036854775807L, seek=0):
      for a in super(XDcDBAcct,self).reader(start_time, end_time, seek):
          a['host_list'] = self.get_host_list(a['node_list'])
          a['hostname'] = a['host_list'][0]
          yield a
