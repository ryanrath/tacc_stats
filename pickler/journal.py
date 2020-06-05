#!/usr/bin/env python
""" Wrapper for logging timing information to the database """

import json
import MySQLdb as mdb

class Journal(object):
    """ Wrapper for logging timing information to the database """

    def __init__(self, config):
        self._config = config

    def logreport(self, report):
        """ Save the report data to the log table. Some parsing is done to break out
            the start and end times. The rest just goes in a json blob.

            The definition of the log table is:

                CREATE TABLE `log` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `dataset` varchar(256) DEFAULT NULL,
                    `start_ts` bigint(20) DEFAULT NULL,
                    `end_ts` bigint(20) DEFAULT NULL,
                    `processed` int(11) DEFAULT NULL,
                    `details` text,
                    PRIMARY KEY (`id`),
                    KEY `end_time` (`end_ts`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """

        end_time_ts = int(report['proc']['end_time'])
        start_time_ts = int(report['proc']['start_time'])

        resources = report['resources'].keys()

        if len(resources) == 1:
            resource = resources[0]
        else:
            resource = 'mixed'

        details = json.dumps(report, default=str)

        acctconf = self._config['archivedatabase']
        con = mdb.connect(db=acctconf['dbname'], read_default_file=acctconf['defaultsfile'])
        mysqlcur = con.cursor()
        mysqlcur.execute('INSERT INTO `log` (dataset, start_ts, end_ts, processed, details) VALUES (%s, %s, %s, %s, %s)',
                         [resource, start_time_ts, end_time_ts, report['proc']['records'], details])
        con.commit()
        mysqlcur.close()
