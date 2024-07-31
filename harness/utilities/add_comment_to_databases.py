#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 07-30-2024
################################################################################
# Purpose:
#   This script currently only has support for Slurm systems and InfluxDB.
#
#   Queries each enabled backend to find the runs without the complete list of
#   events, then attempts to re-send each event not found, using the event files.
#   If event files aren't found, queries SLURM to find out if the job crashed.
#   POSTs the update back to each backend under 'check_end' status.
################################################################################

from datetime import datetime
import os
import glob
import subprocess
import argparse
import csv
import socket

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
    if not db.name == "influxdb":
        self.doErrorLogging(f"Unsupported db backend: {db.name}")
        exit(1)

# Checking format of provided times ############################################
if not (args.time.endswith('d') or args.time.endswith('h')):
    logger.doErrorLogging(f"Unrecognized time parameter: {args.time}.")
    logger.doErrorLogging(f"This program allows hours or days to be specified as '1h' or '1d' for one hour or day, respectively.")
    exit(1)

# Helper functions, one per database type ######################################
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

def check_job_status(slurm_jobid_lst):
    """
        Checks if a Slurm job is running by querying sacct
        Returns [False] (list length=1) or
            [JobID, Elapsed, Start, End, State, ExitCode, Reason, Comment]
    """
    result = {}  # a dictionary of dictionaries
    low_limit = 0
    high_limit = 0
    batch_size = 100
    node_failed_jobids = []
    # Batched into batches of 100
    while low_limit < len(slurm_jobid_lst):
        high_limit = min(low_limit + batch_size, len(slurm_jobid_lst))
        sacct_format = 'JobID,Elapsed,Start,End,State%40,ExitCode,Reason%100,Comment%100'
        cmd=f"sacct -j {','.join(slurm_jobid_lst[low_limit:high_limit])} --format {sacct_format} -X"
        os.system(f'{cmd} 2>&1 > slurm.jobs.tmp.txt')
        with open(f'slurm.jobs.tmp.txt', 'r') as f:
            line = f.readline()
            labels = line.split()
            comment_line = f.readline()   # line of dashes
            # use the spaces in the comment line to split the next line properly
            for line in f:
                fields = {}
                search_pos = -1
                for i in range(0, len(labels)):
                    next_space = comment_line.find(' ', search_pos + 1)
                    # No more spaces found, and it's the last label
                    if next_space < 0 and i == len(labels) - 1:
                        next_space = len(line)
                    elif next_space < 0:
                        logger.doErrorLogging(f"Sacct parse error: Couldn't find enough spaces to correctly parse the columns to fit the labels {','.join(labels)}")
                    cur_field = line[search_pos+1:next_space].strip()
                    search_pos = next_space
                    fields[labels[i].lower()] = cur_field
                if not 'jobid' in fields:
                    logger.doErrorLogging(f"Couldn't find JobID in sacct record. Skipping")
                    continue
                elif fields['state'] == 'RESIZING':
                    logger.doInfoLogging(f"Detected RESIZING for job {fields['jobid']}. RESIZING is from node failure + SLURM '--no-kill'. There should be another record in sacct for this job. Skipping")
                    # Add a field to this job that shows it had/survived a node failure
                    node_failed_jobids.append(fields['jobid'])
                    continue
                elif fields['jobid'] in node_failed_jobids:
                    # Check if a previous step had come in with RESIZING
                    logger.doDebugLogging(f"Found jobid in node failure list: {fields['jobid']}")
                    fields['node-failed'] = True
                result[fields['jobid']] = fields
        os.remove(f"slurm.jobs.tmp.txt")
        low_limit = high_limit  # prepare for next iteration
    return result

def get_user_from_id(user_id):
    """ Given a user ID, return the username """
    # replace parenthesis with commas to make splitting easier
    os.system(f"id {user_id} 2>&1 | tr '()' '??' | cut -d'?' -f2 > tmp.user.txt")
    with open(f'tmp.user.txt', 'r') as f:
        user_name = f.readline().strip()
    if len(user_name) == 0:
        logger.doErrorLogging(f"Couldn't find user name for {user_id}. Returning 'unknown'")
        user_name = 'unknown'
    os.remove(f"tmp.user.txt")
    return user_name

def slurm_time_to_harness_time(timecode):
    """
    Converts the time format from Slurm into the time format for the harness (YYYY-MM-DDTHH:MM:SS.6f)
    """
    return f'{timecode}.000000'


skipped = 0
sent = 0

for db in db_logger.enabled_backends:
    results = []
    if db.name == "influxdb":
        results.extend(influxdb_get_results(db))

    if not len(results) == 1:
        logger.doInfoLogging("No results returned from database query.")
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
        db.send_event(entry)

