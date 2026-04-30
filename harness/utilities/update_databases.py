#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 2025-08-12
################################################################################
# Purpose:
#   This script currently only has support for Slurm systems and InfluxDB and
#   Kafka with the Druid database backend.
#
#   Queries each enabled backend to find the runs without the complete list of
#   events, then attempts to re-send each event not found, using the event files.
#   If event files aren't found, queries SLURM to find out if the job crashed.
#   POSTs the update back to each backend under 'check_end' status.
################################################################################

from datetime import datetime, timedelta
import os
import glob
import subprocess
import argparse
import csv
import socket
import re

prefix = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
)
sys.path = [prefix] + sys.path

from libraries.rgt_database_loggers.rgt_database_logger_factory import create_rgt_db_logger

# Silently wrapped in try/except so errors are handled by rgt_db_logger class
try:
    from libraries.rgt_database_loggers.db_backends.rgt_influxdb import InfluxDBLogger
except ImportError as e:
    pass

try:
    from libraries.rgt_database_loggers.db_backends.rgt_kafka import KafkaLogger
except ImportError as e:
    pass

from libraries.subtest_factory import SubtestFactory
from libraries.status_file import StatusFile, get_status_info_from_file
from libraries.config_file import rgt_config_file
from libraries.rgt_loggers import rgt_logger_factory

# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Updates harness runs in database backends using event and Slurm data")
parser.add_argument('--time', '-t', default='7d', type=str, action='store', help="How far back to look for jobs relative to now (ex: 1h, 2d).")
parser.add_argument('--starttime', type=str, action='store', help="Absolute start time. Format: YYYY-MM-DDTHH:MM:SSZ. Overrides --time")
parser.add_argument('--endtime', type=str, action='store', help="Absolute end time. Format: YYYY-MM-DDTHH:MM:SSZ. Should only be used with --starttime.")
parser.add_argument('--user', '-u', default=f"{os.environ['USER']}", type=str, action='store', help="Specifies the UNIX user to update jobs for.")
parser.add_argument('--machine', '-m', required=True, type=str, action='store', help="Specifies the machine to look for jobs for. Setting a wrong machine may lead to SLURM job IDs not being found.")
parser.add_argument('--app', type=str, action='store', help="Specifies the app to update jobs for.")
parser.add_argument('--test', type=str, action='store', help="Specifies the test to update jobs for.")
parser.add_argument('--runtag', type=str, action='store', help="Specifies the runtag to update jobs for.")
parser.add_argument('--loglevel', default='INFO', choices=["NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL"], type=str, action='store', help="Specify verbosity")
parser.add_argument('--dry-run', action='store_true', help="When set, prints messages to send to databases, but does not send them.")
parser.add_argument('--build-timeout', type=float, default=6.0, action='store', help="Number of hours after a build_start event before logging a failed build_end event.")
parser.add_argument('--kafka-grace-period', type=int, default=1800, action='store', help="Number of seconds that Druid can be out-of-sync with local files due to Kafka buffering before re-logging existing events. Only applies to Kafka")

# Parse command-line arguments #################################################
args = parser.parse_args()

# Create rgt_logger
logger = rgt_logger_factory.create_rgt_logger(logger_name='update_db',
                fh_filepath='/dev/null', logger_threshold_log_level=args.loglevel,
                fh_threshold_log_level=args.loglevel, ch_threshold_log_level=args.loglevel)

# Read in the <machine>.ini configuration file #################################
# uses the getDefaultConfigName, which keys off of OLCF_HARNESS_MACHINE
config = rgt_config_file(logger=logger)

db_logger = create_rgt_db_logger(logger=logger)

# db_logger is ready

logger.doInfoLogging(f"Enabled {len(db_logger.enabled_backends)} database backends")

for db in db_logger.enabled_backends:
    if db.name == "influxdb":
        continue
    elif db.name == "kafka":
        if not 'RGT_KAFKA_EVENTS_TOPIC' in os.environ:
            self.doErrorLogging(f"The Kafka backend requires RGT_KAFKA_EVENTS_TOPIC to be set in the environment.")
            exit(1)
        continue
    else:
        self.doErrorLogging(f"Unsupported db backend: {db.name}")
        exit(1)

# Dictionaries with key-value pairs for global use #############################
state_to_value = {
    'fail': 21,
    'timeout': 23,
    'node_fail': 9,
    'success': 0
}
slurm_job_state_codes = {
    'fail': ['DEADLINE', 'FAILED', 'OUT_OF_MEMORY', 'REVOKED'],
    'timeout': ['TIMEOUT'],
    'node_fail': ['NODE_FAIL', 'BOOT_FAIL', 'RESIZING'],
    'success': ['COMPLETED'],
    'pending': ['PENDING', 'RUNNING']
}

# Checking format of provided times ############################################
def check_time_format(s):
    try:
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        logger.doErrorLogging(f"Invalid time format: {s}. Aborting")
        raise
    return True

# Check time formatting
if args.starttime:
    # Check format
    check_time_format(args.starttime)
if args.endtime:
    # Check format
    check_time_format(args.endtime)
if not (args.time.endswith('d') or args.time.endswith('h')):
    logger.doErrorLogging(f"Unrecognized time parameter: {args.time[0]}.")
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
    elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$", event_time):
        # YYYY-MM-DDTHH:MM:SS.UUUZ
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$", event_time):
        # YYYY-MM-DDTHH:MM:SS
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")
    elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", event_time):
        # YYYY-MM-DDTHH:MM:SSZ
        log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ")
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
        if args.starttime:
            # Then we use 'from: <timestamp>'
            flux_time_str = f'|> range(start: {args.starttime}'
            if args.endtime:
                flux_time_str += f', stop: {args.endtime}'
            flux_time_str += ')'
        else:
            # Then we use --time
            flux_time_str = f'|> range(start: -{args.time})'
        machine_app_test_filter = f'r.machine == "{args.machine}"'
        if args.app:
            machine_app_test_filter += f' and r.app == "{args.app}"'
        if args.test:
            machine_app_test_filter += f' and r["test"] == "{args.test}"'
        if args.runtag:
            machine_app_test_filter += f' and r.runtag == "{args.runtag}"'

        # Excludes the output_txt field, since that's not important to this query
        # r.user is an InfluxDB intrinsic variable, so we can't query based on that
        running_query = f'from(bucket: "{db.bucket}") {flux_time_str} \
        |> filter(fn: (r) => r._measurement == "events" and {machine_app_test_filter} and r._field != "output_txt") \
        |> last() \
        |> pivot(rowKey: ["test_id", "machine", "_time"], columnKey: ["_field"], valueColumn: "_value") \
        |> filter(fn: (r) => r.event_name == "job_queued" or (r.event_name != "check_end" and (r.event_value == "0" or r.event_value == "[NO_VALUE]"))) \
        |> group()'

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
            logger.doDebugLogging(f"Discarding test id {r['test_id']} with missing entries: {','.join(missing_entries)}")
        elif not r['user'] == args.user:
            logger.doDebugLogging(f"Discarding test id {r['test_id']} from user {r['user']}")
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
        # Build range() line for flux query
        if args.starttime:
            # Then we use 'from: <timestamp>'
            filters.append(f'__time > MILLIS_TO_TIMESTAMP({event_time_to_timestamp(args.starttime, precision="ms")})')
            if args.endtime:
                filters.append(f'__time < MILLIS_TO_TIMESTAMP({event_time_to_timestamp(args.endtime, precision="ms")})')
        else:
            # Then we use --time
            if args.time.endswith('d'):
                # then subtract some number of days from current day
                dt = datetime.today() - timedelta(days=int(args.time.replace('d', '')))
            else:
                # then subtract some number of hours
                dt = datetime.today() - timedelta(hours=int(args.time.replace('h', '')))
            filters.append(f'__time > MILLIS_TO_TIMESTAMP({event_time_to_timestamp(dt.strftime("%Y-%m-%dT%H:%M:%SZ"), precision="ms")})')
        if args.app:
            filters.append(f'app = \'{args.app}\'')
        if args.test:
            filters.append(f'test = \'{args.test}\'')
        if args.runtag:
            filters.append(f'runtag = \'{args.runtag}\'')
        filters.append(f'machine = \'{args.machine}\'')

        groupby_fields = ['test_id', 'machine', 'app', 'test']
        # user is a SQL keyword, and event_time is swallowed up by Druid as a timestamp
        fields_sql_kw = ['user', 'event_time']
        field_selector = f'{",".join(groupby_fields)},{",".join([f"LATEST({e}) as {e}" for e in KafkaLogger.KAFKA_EVENT_FIELDS if not (e in groupby_fields or e in fields_sql_kw)])}'
        field_selector += f',LATEST("user") as "user",MAX(__time) as event_time'
        unfinished_conditional = 'event_name = \'job_queued\' or (event_name != \'check_end\' and (event_value = \'0\' or event_value = \'[NO_VALUE]\'))'

        #query = f'SELECT * FROM {os.environ["RGT_KAFKA_EVENTS_TOPIC"]} WHERE timestamp = (SELECT MAX(timestamp) FROM {os.environ["RGT_KAFKA_EVENTS_TOPIC"]} AS subq WHERE subq.test_id = test_id) AND {" AND ".join(filters)} GROUP BY test_id,machine,app,test HAVING event_name = "job_queued" or (event_name != "check_end" and (event_value = "0" or event_value = "[NO_VALUE]"))'
        query = f'SELECT * FROM (SELECT {field_selector} FROM "{os.environ["RGT_KAFKA_EVENTS_TOPIC"]}" WHERE {" AND ".join(filters)} GROUP BY test_id,machine,app,test) WHERE {unfinished_conditional}'
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
        elif not r['user'] == args.user:
            logger.doDebugLogging(f"Discarding test id {r['test_id']} from user {r['user']}")
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
                    logger.doWarningLogging(f"Couldn't find JobID in sacct record. Skipping")
                    continue
                elif fields['state'] == 'RESIZING':
                    logger.doDebugLogging(f"Detected RESIZING for job {fields['jobid']}. RESIZING is from node failure + SLURM '--no-kill'. There should be another record in sacct for this job. Skipping")
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

def get_latest_time(t_new, t_ref):
    """
    Helper method to compare 2 time strings (via event_time_to_timestamp) and return the latest
    """
    if event_time_to_timestamp(t_new, precision='us') > event_time_to_timestamp(t_ref, precision='us'):
        return t_new
    else:
        new_timestamp = event_time_to_timestamp(t_ref, precision='us')
        # normalize to be in seconds
        new_timestamp /= (1000 * 1000)
        # add 1 second
        new_timestamp += 1.0
        # return in standard harness time format
        new_dt = datetime.fromtimestamp(new_timestamp)
        return datetime.strftime(new_dt, "%Y-%m-%dT%H:%M:%S.%f")

skipped = 0
sent = 0

if args.dry_run:
    for db in db_logger.enabled_backends:
        os.environ[db.disable_envvar_name] = "1"

# The calls to db_logger.log_event are for ALL enabled backends, so
# the subsequent iterations in this loop will have fewer un-logged
# results
for db in db_logger.enabled_backends:
    # Create a local db_logger with ONLY the current database
    single_db_logger = create_rgt_db_logger(logger=logger, only=db.url)
    results = []
    if db.name == "influxdb":
        results.extend(influxdb_get_results(db))
    elif db.name == "kafka":
        results.extend(kafka_get_results(db))
    # now process results
    # Get all Slurm job IDs
    slurm_job_ids = [ e['job_id'] for e in results if not e['job_id'] == '[NO_VALUE]' ]
    # A job ID will have a field named `node-failed` = True if it survived a node failure via --no-kill
    slurm_data = check_job_status(slurm_job_ids)

    for entry in results:
        # check to see if this entry should be parsed
        logger.doDebugLogging(f"Processing {entry['test_id']}, SLURM id {entry['job_id']} ========================")

        if entry['job_id'] == '[NO_VALUE]':
            # Then this test never made it to the scheduler. Ignore it
            logger.doDebugLogging(f"Test {entry['test_id']} has not made it to a scheduler.")
            # if it's a build_start status that is older than args.build_timeout, then log a build_end status
            if not entry['event_name'] == f"{StatusFile.EVENT_DICT[StatusFile.EVENT_BUILD_START][1]}_{StatusFile.EVENT_DICT[StatusFile.EVENT_BUILD_START][2]}":
                skipped += 1
                continue
            # InfluxDB & Kafka report event_time in different formats
            if db.name == "kafka":
                timediff_dt = datetime.now() - datetime.strptime(entry['event_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                timediff_dt = datetime.now() - datetime.strptime(entry['event_time'], "%Y-%m-%dT%H:%M:%S.%f")
            timediff_hours = timediff_dt.total_seconds() / (60.0 * 60.0)
            if timediff_hours < args.build_timeout:
                skipped += 1
                continue
            # Update fields in entry
            entry['event_time'] = datetime.now().isoformat()
            entry['event_type'] = StatusFile.EVENT_DICT[StatusFile.EVENT_BUILD_END][1]
            entry['event_subtype'] = StatusFile.EVENT_DICT[StatusFile.EVENT_BUILD_END][2]
            entry['event_name'] = entry['event_type'] + '_' + entry['event_subtype']
            entry['event_filename'] = StatusFile.EVENT_DICT[StatusFile.EVENT_BUILD_END][0]
            entry['event_value'] = state_to_value['timeout']
            entry['hostname'] = socket.gethostname()
            entry['user'] = os.environ['USER']
            sent += 1
            entry['output_txt'] = f"Build timed out after {timediff_hours:.1f} hours."
            logger.doErrorLogging(f"Logging build timeout for app={entry['app']}, test={entry['test']}, test_id={entry['test_id']} to {db.url}.")
            single_db_logger.log_event(entry)
        elif not entry['job_id'] in slurm_data.keys():
            logger.doWarningLogging(f"Couldn't find job id {entry['job_id']} in Slurm data. It's possible the job has not finished yet.")
        elif slurm_data[entry['job_id']]['state'] in slurm_job_state_codes['pending']:
            # Then this job is still running/waiting in queue, we can skip
            logger.doDebugLogging(f"Job {entry['job_id']} is in state {slurm_data[entry['job_id']]['state']}. Skipping.")
            skipped += 1
            continue
        elif slurm_data[entry['job_id']]['state'].startswith('CANCELLED'):
            logger.doDebugLogging(f"Found cancelled job {entry['job_id']}. Sending status updates.")
            sent += 1
            if 'node-failed' in slurm_data[entry['job_id']] and slurm_data[entry['job_id']]['node-failed']:
                # Then we possibly had a user-cancelled job following a node failure
                entry['output_txt'] = 'NODE_FAIL detected. Job canceled'
                entry['event_value'] = state_to_value['node_fail']
            else:
                entry['output_txt'] = 'Job canceled'
                entry['event_value'] = state_to_value['fail']
            # Update fields in entry
            entry['event_time'] = get_latest_time(slurm_time_to_harness_time(slurm_data[entry['job_id']]['end']), entry['event_time'])
            entry['event_type'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][1]
            entry['event_subtype'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][2]
            entry['event_name'] = entry['event_type'] + '_' + entry['event_subtype']
            entry['event_filename'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][0]
            entry['hostname'] = socket.gethostname()
            entry['user'] = os.environ['USER']
            # Check if CANCELLED BY ...
            job_status_long = slurm_data[entry['job_id']]['state'].split(' ')
            if len(job_status_long) > 1:
                cancel_user = get_user_from_id(job_status_long[2])
                entry['output_txt'] += f" at {slurm_data[entry['job_id']]['end']} by {cancel_user}"
            else:
                entry['output_txt'] += f" at {slurm_data[entry['job_id']]['end']}"
            entry['output_txt'] += f", after running for {slurm_data[entry['job_id']]['elapsed']}."
            entry['output_txt'] += f" Exit code: {slurm_data[entry['job_id']]['exitcode']}, reason: {slurm_data[entry['job_id']]['reason']}."
            logger.doErrorLogging(f"Logging cancelled job, app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}.")
            single_db_logger.log_event(entry)
        elif slurm_data[entry['job_id']]['state'] in slurm_job_state_codes['node_fail']:
            logger.doDebugLogging(f"Found node failure from: {entry['job_id']}")
            sent += 1
            entry['event_time'] = get_latest_time(slurm_time_to_harness_time(slurm_data[entry['job_id']]['end']), entry['event_time'])
            entry['event_type'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][1]
            entry['event_subtype'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][2]
            entry['event_name'] = entry['event_type'] + '_' + entry['event_subtype']
            entry['event_filename'] = StatusFile.NO_VALUE
            entry['event_value'] = state_to_value['node_fail']
            entry['hostname'] = socket.gethostname()
            entry['user'] = os.environ['USER']
            entry['output_txt'] = f"Node failure detected. Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
            logger.doErrorLogging(f"Logging NODE_FAIL'd job, app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}.")
            single_db_logger.log_event(entry)
        elif slurm_data[entry['job_id']]['state'] in slurm_job_state_codes['timeout']:
            sent += 1
            if 'node-failed' in slurm_data[entry['job_id']] and slurm_data[entry['job_id']]['node-failed']:
                logger.doDebugLogging(f"Found node_fail + timed out job: {entry['job_id']}")
                entry['output_txt'] = f"NODE_FAIL followed by TIMEOUT detected. Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
                entry['event_value'] = state_to_value['node_fail']
            else:
                logger.doDebugLogging(f"Found timed out job: {entry['job_id']}")
                entry['output_txt'] = f"TIMEOUT detected. Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
                entry['event_value'] = state_to_value['timeout']
            entry['event_time'] = get_latest_time(slurm_time_to_harness_time(slurm_data[entry['job_id']]['end']), entry['event_time'])
            entry['event_type'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][1]
            entry['event_subtype'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][2]
            entry['event_name'] = entry['event_type'] + '_' + entry['event_subtype']
            entry['event_filename'] = StatusFile.NO_VALUE
            entry['hostname'] = socket.gethostname()
            entry['user'] = os.environ['USER']
            logger.doErrorLogging(f"Logging timed-out job, app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}.")
            single_db_logger.log_event(entry)
        elif slurm_data[entry['job_id']]['state'] in slurm_job_state_codes['success'] or \
             slurm_data[entry['job_id']]['state'] in slurm_job_state_codes['fail']:
            # Then the job completed, but did not successfully log results (perhaps the compute node can't reach the db?)
            # So we search for status files of events more recent than the one we have
            logger.doDebugLogging(f"Found job {entry['job_id']} in state {slurm_data[entry['job_id']]['state']}. Newest event state was {entry['event_name']}.")
            # Annoyingly, status_dir is not stored in the status file, so we have to use Run_Archive
            status_file_path = os.path.join(entry['run_archive'], '..', '..', 'Status', entry['test_id'])
            current_event_num = int(entry['event_filename'].split('_')[1])
            cur_dir = os.getcwd()
            if not (os.path.exists(status_file_path) and os.path.exists(entry['run_archive'])):
                logger.doDebugLogging(f"Status file and Run_Archive paths for test {entry['test_id']} do not exist ({entry['run_archive']}). Skipping.")
                continue
            logger.doErrorLogging(f"Logging test that completed the Slurm job but did not log to the database, app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}.")
            sent += 1
            os.chdir(status_file_path)
            found_checkend = False
            kafka_grace_period_invoked = False
            for status_file_name in glob.glob("Event_*.txt"):
                event_number = int(status_file_name.split('_')[1]) # used to sort if this is a newer event than current
                if event_number > current_event_num:
                    # Then get the info from the status file & log it to the database
                    event_info = get_status_info_from_file(status_file_name)

                    if db.name == "kafka":
                        # get time between this event and now, check kafka_grace_period
                        diff_s = int(datetime.now().timestamp()) - event_time_to_timestamp(event_info['event_time'], precision='s')
                        if diff_s < args.kafka_grace_period:
                            logger.doWarningLogging(f"Skipping event {status_file_name} for app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}, since kafka_grace_period has not passed: {diff_s} (actual) < {args.kafka_grace_period} (threshold).")
                            kafka_grace_period_invoked = True
                            continue


                    # This is a global call for all enabled databases -- re-posting an event to InfluxDB doesn't hurt
                    logger.doErrorLogging(f"Logging event {status_file_name} for app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}.")
                    single_db_logger.log_event(event_info)
                    if status_file_name == StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][0]:
                        found_checkend = True
                        # Then we initialize a subtest object to go look for metrics & node health results
                        subtest = SubtestFactory.make_subtest(name_of_application=entry['app'],
                                                              name_of_subtest=entry['test'],
                                                              local_path_to_tests=os.path.join(entry['run_archive'], '../../../..'),
                                                              logger=logger,
                                                              tag=entry['test_id'],
                                                              db_logger=single_db_logger)
                        logger.doDebugLogging(f"Attempting to log metric and node health information {status_file_name} for test {entry['test_id']} to {db.url}.")
                        if not subtest.run_db_extensions():
                            logger.doErrorLogging(f"Logging metric & node health data to databases failed for app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}.")
            if (not found_checkend) and (not kafka_grace_period_invoked):
                # If the test didn't log a check_end event, we simulate one here
                logger.doDebugLogging(f"Job {entry['job_id']} in state {slurm_data[entry['job_id']]['state']} did not complete a check_end event. Logging check_end with fail check code.")
                entry['output_txt'] = f"Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
                entry['event_time'] = get_latest_time(slurm_time_to_harness_time(slurm_data[entry['job_id']]['end']), entry['event_time'])
                entry['event_type'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][1]
                entry['event_subtype'] = StatusFile.EVENT_DICT[StatusFile.EVENT_CHECK_END][2]
                entry['event_name'] = entry['event_type'] + '_' + entry['event_subtype']
                entry['event_filename'] = StatusFile.NO_VALUE
                entry['event_value'] = state_to_value['fail']
                entry['hostname'] = socket.gethostname()
                entry['user'] = os.environ['USER']
                logger.doErrorLogging(f"Logging failure exit code for job that exited without logging the check_end event, app={entry['app']}, test={entry['test']}, test_id={entry['test_id']}, jobid={entry['job_id']} to {db.url}.")
                single_db_logger.log_event(entry)
            os.chdir(cur_dir)
        else:
            logger.doWarningLogging(f"Unrecognized job state: {slurm_data[entry['job_id']]['state']}. No action is being taken for job {entry['job_id']}.")
            skipped += 1

if sent > 0:
    # Log at critical level if sent > 0, else at error level
    logger.doCriticalLogging(f"Attempted to log {sent} jobs to databases. Skipped {skipped}.")
else:
    logger.doWarningLogging(f"Attempted to log {sent} jobs to databases. Skipped {skipped}.")
