import numpy
import tspl_utils
import tspl

class Catastrophe(object):

  # Hash value must be a list
  k1={'amd64' : ['amd64_sock'],
          'intel': ['intel_pmc3'],
      'intel_snb': ['intel_snb']}
  k2={'amd64' : ['DRAM'],
          'intel': ['MEM_LOAD_RETIRED_L1D_HIT'],
      'intel_snb': ['LOAD_L1D_ALL']}
  comp_operator = '<'

  def setup(self, job_data):
    self.aggregate = True
    self.min_time = 3600
    self.min_hosts = 1
    self.waynesses=[x+1 for x in range(32)]
    self.ignore_qs = []
    
    self.metric = float("nan")
    try:
      if self.aggregate:
        self.ts=tspl.TSPLSum("",self.k1,self.k2,job_data=job_data)
      else:
        self.ts=tspl.TSPLBase("",self.k1,self.k2,job_data=job_data)
    except tspl.TSPLException as e:
      return False
    except EOFError as e:
      print('End of file found reading: ' + job_path)
      return False

    if not tspl_utils.checkjob(self.ts,self.min_time,
                               self.waynesses,skip_queues=self.ignore_qs):
      return False
    elif self.ts.numhosts < self.min_hosts:
      return False
    else:
      return True

  def compute_fit_params(self,ind):
    fit=[]
    r1=range(ind)
    r2=[x + ind for x in range(len(self.dt)-ind)]

    for v in self.ts:
      rate=numpy.divide(numpy.diff(v),self.dt)
      # integral before time slice 
      a=numpy.trapz(rate[r1],self.tmid[r1])/(self.tmid[ind]-self.tmid[0])
      # integral after time slice
      b=numpy.trapz(rate[r2],self.tmid[r2])/(self.tmid[-1]-self.tmid[ind])
      # ratio of integral after time over before time
      fit.append(b/a)      
    return fit   

  def compute_metric(self):

    if len(tspl_utils.lost_data(self.ts)) > 0: 
      self.metric = { 'error': "Detected hosts with bad data" }
      return

    self.tmid=(self.ts.t[:-1]+self.ts.t[1:])/2.0
    self.dt = numpy.diff(self.ts.t)

    #skip first and last two time slices
    vals=[]
    for i in [x + 2 for x in range(self.ts.size-4)]:
      vals.append(self.compute_fit_params(i))

    #times  hosts ---->
    #  |
    #  |
    #  |
    #  V

    self.metric = numpy.array(vals).min()
    return
