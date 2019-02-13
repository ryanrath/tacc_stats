""" Utility functions that are used from more than one place """
import logging

def setuplogger(consolelevel, filename=None, filelevel=None):
    """ setup the python root logger to log to the console with defined log
        level. Optionally also log to file with the provided level """

    if filelevel is None:
        filelevel = consolelevel

    logging.captureWarnings(True)

    rootlogger = logging.getLogger()
    rootlogger.setLevel(min(consolelevel, filelevel))

    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')

    if filename != None:
        filehandler = logging.FileHandler(filename)
        filehandler.setLevel(filelevel)
        filehandler.setFormatter(formatter)
        rootlogger.addHandler(filehandler)

    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(consolelevel)
    consolehandler.setFormatter(formatter)
    rootlogger.addHandler(consolehandler)
