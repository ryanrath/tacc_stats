import time

def isodate(s):
    """ Return the unix timestamp for a date represented in the LOCAL timezone """
    """ Note that it is strongly recommended to store dates with their timezone """
    """ information. The absence of the timezone means that some dates are ambigous """
    return int(time.mktime(time.strptime(s,'%Y-%m-%dT%H:%M:%S')))

def isodate_pacific(s):
    """ Return an estimate for the unix timestamp for a date represented in US/Pacific time """
    """ this code will not correctly handle daylight savings transitions """
    return isodate(s) + (3 * 3600)
