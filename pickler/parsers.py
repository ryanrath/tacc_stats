import pytz
import datetime

class TimeFixer(object):
    """ Compute the posix timestamp of a timestamp that is assumed to be in a given timezone. """

    def __init__(self, timezoneName, guessEarly):
        """ timezoneName name of target timezone
            guessEarly if the time string is ambigous (due to e.g. DST change) then whether to return the earlier possible time or the later one (true for earlier).
            """
        self.timezone = pytz.timezone(timezoneName)
        self.is_dst = guessEarly

    @staticmethod
    def to_posix(date):
        """ returns a posix timestamp for a non-timezone aware date time """
        return (date - datetime.datetime(1970, 1, 1)).total_seconds()

    def __call__(self, arg):
        """ main impl """
        time = datetime.datetime.strptime(arg, '%Y-%m-%dT%H:%M:%S')

        time_ts = self.to_posix(time)
        try:
            time_ts -= self.timezone.utcoffset(time).total_seconds()
        except pytz.exceptions.AmbiguousTimeError:
            time_ts -= self.timezone.utcoffset(time, self.is_dst).total_seconds()

        return int(round(time_ts))
