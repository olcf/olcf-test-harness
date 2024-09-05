#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 09-05-2024
################################################################################
# Purpose:
#   Send metrics from outside of the harness to the InfluxDB database.
#   For example, MTBF.
################################################################################

from datetime import datetime
import os
import argparse
import re

from libraries.rgt_database_loggers.rgt_database_logger_factory import create_rgt_db_logger
from libraries.rgt_database_loggers.db_backends.rgt_influxdb import InfluxDBLogger
from libraries.subtest_factory import SubtestFactory
from libraries.status_file import StatusFile, get_status_info_from_file
from libraries.config_file import rgt_config_file
from libraries.rgt_loggers import rgt_logger_factory

# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Post a custom metric to Databases")
parser.add_argument('--time', '-t', type=str, action='store', help="Timestamp to post record as. Format: YYYY-MM-DDTHH:MM:SS[.MS][Z]")
parser.add_argument('--keys', '-k', required=True, type=str, action='store', help="A set of comma-separated keys to identify your metric by. Ex: machine=frontier")
parser.add_argument('--values', '-v', required=True, type=str, action='store', help="A set of comma-separated values to post. Ex: value_a=1,value_b=2. These may or may not be quoted")
parser.add_argument('--loglevel', default='INFO', choices=["NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL"], type=str, action='store', help="Specify verbosity")
parser.add_argument('--table_name', default='non_harness_metrics', type=str, action='store', help="Specifies the name of the table (measurement) to post to.")
parser.add_argument('--dry-run', action='store_true', help="When set, print the message to the databases, but do not send.")

# Parse command-line arguments #################################################
args = parser.parse_args()

# Read in the <machine>.ini configuration file #################################
# uses the getDefaultConfigName, which keys off of OLCF_HARNESS_MACHINE
config = rgt_config_file()
logger = rgt_logger_factory.create_rgt_logger(logger_name='report_to_db',
                fh_filepath='/dev/null', logger_threshold_log_level=args.loglevel,
                fh_threshold_log_level=args.loglevel, ch_threshold_log_level=args.loglevel)

db_logger = create_rgt_db_logger(logger=logger)

# db_logger is ready

logger.doInfoLogging(f"Enabled {len(db_logger.enabled_backends)} database backends")

if args.dry_run:
    for db in db_logger.enabled_backends:
        os.environ[db.disable_envvar_name] = "1"

skipped = 0
sent = 0

# Format check for keys & values ###############################################
def format_check(line):
    """ Format check for keys & values """
    # Expecting value_1=x,value_2=y
    splt_by_comma = line.split(',')
    for entry in splt_by_comma:
        splt_by_equal = entry.split('=')
        if not len(splt_by_equal) == 2:
            return [False, f'Invalid entry has more or less than 1 equal sign: {entry}']
        # Single quotes are not permitted in general
        if "'" in entry:
            return [False, f'Single quotes are not permitted in any keys/values: {entry}']
        # Check for unbalanced/ill-placed quotes
        if splt_by_equal[1].startswith('"') and not splt_by_equal[1].endswith('"'):
            return [False, f'Unbalanced quotes found in: {entry}']
        elif not splt_by_equal[1].startswith('"') and splt_by_equal[1].endswith('"'):
            return [False, f'Unbalanced quotes found in: {entry}']
        elif '"' in splt_by_equal[1][1:-1]:
            # If there's a quote in the middle of the string
            return [False, f'Quote found in the middle of a value: {entry}']
        # Check to make sure there's no quotes in the label
        if '"' in splt_by_equal[0]:
            return [False, f'Quotes not allowed in labels: {entry}']
    return [True, '']

ret = format_check(args.values)
if not ret[0]:
    logger.doErrorLogging(f"Format check of values failed: {ret[1]}")
    exit(1)
ret = format_check(args.keys)
if not ret[0]:
    logger.doErrorLogging(f"Format check of values failed: {ret[1]}")
    exit(1)

################################################################################

# Format check for fields ######################################################
log_time = args.time if args.time else datetime.now().isoformat()
keys_formatted = {}
for val in args.keys.split(','):
    val_splt = val.split('=')
    # Keys cannot use quotes, so remove them if they are used
    if val_splt[1].startswith('"'):
        val_splt[1] = val_splt[1][1:-1]
    # Save as a string
    keys_formatted[val_splt[0]] = str(val_splt[1])

number_regex = re.compile('^([0-9]*\.)?[0-9]+(e[+-]?[0-9]+)?$')
values_formatted = {}
for val in args.values.split(','):
    # We know it's properly formatted already
    val_splt = val.split('=')
    # We know quotes are balanced - if the starting quote is there, so is end
    if not val_splt[1].startswith('"'):
        if not number_regex.match(val_splt[1]):
            val_splt[1] = '"' + val_splt[1] + '"'
        # else, it's a valid decimal number
    elif val_splt[1].startswith('"') and number_regex.match(val_splt[1][1:-1]):
        # If it's a number, un-quote it (otherwise InfluxDB thinks it's a str)
        val_splt[1] = val_splt[1][1:-1]
    # Save as a string
    values_formatted[val_splt[0]] = f'{val_splt[1]}'

################################################################################

# Send #########################################################################
db_logger.log_external_metrics(args.table_name, keys_formatted, values_formatted, log_time)
################################################################################
