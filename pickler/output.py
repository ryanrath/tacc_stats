#!/usr/bin/env python
""" job summary output """
from pymongo import MongoClient
from pymongo.errors import InvalidDocument
import json

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
        print json.dumps(summary, indent=4)
        print json.dumps(timeseries, indent=4)
        return True

    def logreport(self, report):
        print report

class MongoOutput(object):
    def __init__(self, dbconfig):
        self.client = MongoClient(dbconfig['uri'])
        self.db = self.client[dbconfig['dbname']]

    def insert(self, resourcename, summary, timeseries):
        summaryOk = False
        try:
            self.db[resourcename].update( {"_id": summary["_id"]}, summary, upsert=True )

            if self.db[resourcename].find_one( {"_id": summary["_id"], "summary_version": summary["summary_version"] }, { "_id":1 } ) != None:
                summaryOk = True
        except InvalidDocument as exc:
            logging.error("inserting summary document %s %s. %s",
                          resourcename, summary["_id"], str(exc))

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

    def logreport(self, report):
        try:
            self.db['journal'].insert(report)
        except Exception as exc:
            logging.error("inserting report. Error: %s %s", str(exc), str(report))

