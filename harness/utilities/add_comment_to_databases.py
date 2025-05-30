#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 2025-05-30
################################################################################
# Purpose:
#   This script currently only has support for Slurm systems and InfluxDB and
#   Kafka with the Druid database backend.
#
#   Adds a comment field to an existing test in the database.
################################################################################

from datetime import datetime, timedelta
import os
import glob
import subprocess
import argparse
import csv
import socket
import re

from libraries.rgt_database_loggers.rgt_database_logger_factory import create_rgt_db_logger
from libraries.rgt_database_loggers.db_backends.rgt_influxdb import InfluxDBLogger
from libraries.subtest_factory import SubtestFactory
from libraries.status_file import StatusFile, get_status_info_from_file
from libraries.config_file import rgt_config_file
from libraries.rgt_loggers import rgt_logger_factory

# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Updates harness runs in database backends using event and Slurm data")
parser.add_argument('--time', default='90d', type=str, action='store', help="How far back to look for jobs relative to now (ex: 1h, 2d).")
parser.add_argument('--testid', type=str, action='store', required=True, help="Specifies the harness test id to update jobs for.")
parser.add_argument('--loglevel', default='INFO', choices=["NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL"], type=str, action='store', help="Specify verbosity")
parser.add_argument('--dry-run', action='store_true', help="When set, prints messages to send to databases, but does not send them.")
parser.add_argument('--message', type=str, action='store', required=True, help="Comment to add to the record.")
parser.add_argument('--event', type=str, action='store', choices=['logging_start', 'build_start', 'build_end', 'submit_start', \
                        'submit_end', 'job_queued', 'binary_execute_start', 'binary_execute_end', 'check_start', 'check_end'], \
                        help="Specifies the harness event to add the comment to. Defaults to most recent event.")

# Parse command-line arguments #################################################
args = parser.parse_args()

# Read in the <machine>.ini configuration file #################################
# uses the getDefaultConfigName, which keys off of OLCF_HARNESS_MACHINE
config = rgt_config_file()
logger = rgt_logger_factory.create_rgt_logger(logger_name='add_comment_db',
                fh_filepath='/dev/null', logger_threshold_log_level=args.loglevel,
                fh_threshold_log_level=args.loglevel, ch_threshold_log_level=args.loglevel)

db_logger = create_rgt_db_logger(logger=logger)

# db_logger is ready

logger.doInfoLogging(f"Enabled {len(db_logger.enabled_backends)} database backends")

for db in db_logger.enabled_backends:
    if db.name == "influxdb":
        continue
    elif db.name == "kafka":
        continue
    else:
        self.doErrorLogging(f"Unsupported db backend for add_comment_to_databases.py: {db.name}")
        exit(1)

if args.dry_run:
    for db in db_logger.enabled_backends:
        os.environ[db.disable_envvar_name] = "1"

# Checking format of provided times ############################################
if not (args.time.endswith('d') or args.time.endswith('h')):
    logger.doErrorLogging(f"Unrecognized time parameter: {args.time}.")
    logger.doErrorLogging(f"This program allows hours or days to be specified as '1h' or '1d' for one hour or day, respectively.")
    exit(1)

# Helper functions, one per database type ######################################
def event_time_to_timestamp(event_time : str, precision : str = 's'):
    """ Converts a time string to Unix timestamp in EST """

    # Check for different time formats
    if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}$", event_time):
        # YYYY-MM-DDTHH:MM:SS.UUUUUU -- this is the default harness output
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%f")
    elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$", event_time):
        # YYYY-MM-DDTHH:MM:SS.UUUUUUZ
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$", event_time):
        # YYYY-MM-DDTHH:MM:SS
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")
    elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", event_time):
        # YYYY-MM-DDTHH:MM:SSZ
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ")
    elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$", event_time):
        # YYYY-MM-DDTHH:MM:SS.mmmZ
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        raise Exception(f"Unrecognized time format in string {event_time}.")

    # Kafka wants timestamps in seconds, for indexing only (not unique identifiers)
    if precision == 's':
        return int(datetime.timestamp(log_time))
    elif precision == 'ms':
        return int(datetime.timestamp(log_time) * 1000)
    elif precision == 'us':
        return int(datetime.timestamp(log_time) * 1000 * 1000)
    elif precision == 'ns':
        return round(datetime.timestamp(log_time) * 1000 * 1000) * 1000

def influxdb_get_results(db):
    """
    Helper function to return a list of dictionary objects from InfluxDB

    Inherits logger and db_logger from the parent scope
    Parameters:
        db : an instantiation of base_db class (ie, RgtInfluxdbLogger)
    """

    def build_query():
        """
        Helper function to build the query for InfluxDB

        Returns: an InfluxDB Flux v2 query string
        """

        flux_time_str = ''
        # Build range() line for flux query
        flux_time_str = f'|> range(start: -{args.time})'

        # Excludes the output_txt field, since that's not important to this query
        # r.user is an InfluxDB intrinsic variable, so we can't query based on that
        if not args.event:
            running_query = f'from(bucket: "{db.bucket}") {flux_time_str} \
            |> filter(fn: (r) => r._measurement == "events" and r.test_id == "{args.testid}") |> last() \
            |> pivot(rowKey: ["test_id", "machine", "_time"], columnKey: ["_field"], valueColumn: "_value") \
            |> group()'
        else:
            running_query = f'from(bucket: "{db.bucket}") {flux_time_str} \
            |> filter(fn: (r) => r._measurement == "events" and r.test_id == "{args.testid}") \
            |> pivot(rowKey: ["test_id", "machine", "_time"], columnKey: ["_field"], valueColumn: "_value") \
            |> filter(fn: (r) => r.event_name == "{args.event}") |> group()'

        return running_query

    results = db.query(build_query())
    ret = []
    # filter out unwanted/incomplete/irrelevant results
    for r in results:
        missing_entries = []
        for e in InfluxDBLogger.INFLUX_TAGS:
            if not e in r.keys():
                missing_entries.append(e)
        if len(missing_entries) > 0:
            logger.doDebugLogging(f"Discarding event {r['event_id']} from test id {r['test_id']} with missing entries: {','.join(missing_entries)}")
        else:
            ret.append(r)
    return ret

def kafka_get_results(db):
    """
    Helper function to return a list of dictionary objects from Kafka

    Inherits logger and db_logger from the parent scope
    Parameters:
        db : an instantiation of base_db class (ie, RgtKafkaLogger)
    """

    def build_query():
        """
        Helper function to build the query for Kafka

        Returns: a SQL query string
        """

        # build a SQL conditional to check the timestamp
        filters = []
        if args.time.endswith('d'):
            # then subtract some number of days from current day
            dt = datetime.today() - timedelta(days=int(args.time.replace('d', '')))
        else:
            # then subtract some number of hours
            dt = datetime.today() - timedelta(hours=int(args.time.replace('h', '')))
        filters.append(f'__time > MILLIS_TO_TIMESTAMP({event_time_to_timestamp(dt.strftime("%Y-%m-%dT%H:%M:%SZ"), precision="ms")})')
        filters.append(f'test_id = \'{args.testid}\'')

        if args.event:
            filters.append(f'event_name = \'{args.event}\'')

        groupby_fields = ['test_id']
        # user is a SQL keyword, and event_time is swallowed up by Druid as a timestamp
        fields_sql_kw = ['user', 'event_time']
        field_selector = f'{",".join(groupby_fields)},{",".join([f"LATEST({e}) as {e}" for e in KafkaLogger.KAFKA_EVENT_FIELDS if not (e in groupby_fields or e in fields_sql_kw)])}'
        field_selector += f',LATEST("user") as "user",MAX(__time) as event_time'

        query = f'SELECT {field_selector} FROM "{os.environ["RGT_KAFKA_EVENTS_TOPIC"]}" WHERE {" AND ".join(filters)} GROUP BY test_id'
        logger.doDebugLogging(f"SQL query: {query}")
        return query

    results = db.query(build_query())
    ret = []
    # filter out unwanted/incomplete/irrelevant results
    for r in results:
        missing_entries = []
        for e in KafkaLogger.KAFKA_EVENT_FIELDS:
            if not e in r.keys():
                missing_entries.append(e)
        if len(missing_entries) > 0:
            logger.doDebugLogging(f"Discarding test id {r['test_id']} with missing entries: {','.join(missing_entries)}")
        else:
            ret.append(r)
    return ret

for db in db_logger.enabled_backends:
    single_db_logger = create_rgt_db_logger(logger=logger, only=db.url)
    results = []
    if db.name == "influxdb":
        results.extend(influxdb_get_results(db))
    elif db.name == "kafka":
        results.extend(kafka_get_results(db))

    if not len(results) == 1:
        logger.doErrorLogging(f"{len(results)} results returned from database query, expected 1. Skipping adding a comment.")
    else:
        entry = results[0]
        logger.doDebugLogging(f"Setting comment for test_id = {entry['test_id']}, event_name = {entry['event_name']}.")
        timestamp = datetime.now().isoformat()
        user = os.environ['USER']
        if 'comment' in entry.keys() and entry['comment'] == db.NO_VALUE:
            entry['comment'] = f"{timestamp} - {user}: {args.message}"
        elif 'comment' in entry.keys():
            # otherwise, append to the comments
            entry['comment'] += f"\n{timestamp} - {user}: {args.message}"
        elif not 'comment' in entry.keys():
            entry['comment'] = f"{timestamp} - {user}: {args.message}"
        single_db_logger.log_event(entry)

