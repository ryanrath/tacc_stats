#!/usr/bin/env python
""" job summary output """
import json
import logging
from urllib import quote_plus
from pymongo import MongoClient
from pymongo.errors import InvalidDocument

from memory_profiler import profile


def factory(dbconfig):
    if dbconfig['dbtype'] == 'stdout':
        return StdoutOutput(dbconfig)
    else:
        return MongoOutput(dbconfig)


class StdoutOutput(object):
    def __init__(self, _):
        pass

    def insert(self, resourcename, summary, timeseries):
        print resourcename
        print json.dumps(summary, indent=4, default=str)
        print json.dumps(timeseries, indent=4, default=str)
        return True

    def logreport(self, report):
        print report

class MongoOutput(object):
    @profile
    def __init__(self, dbconfig):
        if 'uri' in dbconfig:
            uri = dbconfig['uri']
        else:
            uri = "mongodb://%s:%s@%s/%s?authSource=%s" % (
                quote_plus(dbconfig['user']),
                quote_plus(dbconfig['password']),
                quote_plus(dbconfig['host']),
                quote_plus(dbconfig['dbname']),
                quote_plus(dbconfig['authSource'])
            )
        self.client = MongoClient(uri)
        self.db = self.client[dbconfig['dbname']]

    @profile
    def insert(self, resourcename, summary, timeseries):
        summaryOk = False
        try:
            self.db[resourcename].update( {"_id": summary["_id"]}, summary, upsert=True )

            if self.db[resourcename].find_one( {"_id": summary["_id"], "summary_version": summary["summary_version"] }, { "_id":1 } ) != None:
                summaryOk = True
        except InvalidDocument as exc:
            logging.error("inserting summary document %s %s. %s",
                          resourcename, summary["_id"], str(exc))
        except Exception as e:
            logging.error("Unhandled Error %s", str(e))

        timeseriesOk = False
        if timeseries != None:
            # If the timeseries data is present then it must got into the db
            try:
                self.db["timeseries-" + resourcename].update( {"_id":timeseries["_id"]}, timeseries, upsert=True )
                if self.db["timeseries-" + resourcename].find_one( {"_id": timeseries["_id"]}, { "_id":1 } ) != None:
                    timeseriesOk = True
            except InvalidDocument as exc:
                logging.error("inserting timeseries document %s %s %s",
                              resourcename, timeseries["_id"], str(exc))
                timeseriesOk = False
        else:
            timeseriesOk = True

        return summaryOk and timeseriesOk

    @profile
    def logreport(self, report):
        try:
            self.db['journal'].insert(report)
        except Exception as exc:
            logging.error("inserting report. Error: %s %s", str(exc), str(report))

