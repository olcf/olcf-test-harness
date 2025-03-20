#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 03-20-2025
################################################################################
# Purpose:
#   Locates and archives tests within the OTH directory structure.
################################################################################

from datetime import datetime
import os
import glob
import subprocess
import argparse
import csv

from libraries.subtest_factory import SubtestFactory
from libraries.status_file import StatusFile, get_status_info_from_file
from libraries.config_file import rgt_config_file
from libraries.rgt_loggers import rgt_logger_factory

# define some constants
ALWAYS = 'ALWAYS'
NEVER = 'NEVER'
ON_FAIL = 'ON_FAIL'

def initialize_parser():
    # Initialize argparse ##########################################################
    parser = argparse.ArgumentParser(description="Locates and archives tests, condensing test output into a simplified directory structure.")

    # Required information for operation
    parser.add_argument('--from', required=True, type=str, action='store', help="Path to the application repository directories (ie, Path_to_tests).")
    parser.add_argument('--to', required=True, type=str, action='store', help="Path to the archive location.")

    # Time filtering options:
    parser.add_argument('--age', default='6m', type=str, action='store', help="How old a test must be to be archived (default: 6 months).")
    parser.add_argument('--starttime', type=str, action='store', help="Absolute start time. Format: YYYY-MM-DDTHH:MM:SSZ. Overrides --time")
    parser.add_argument('--endtime', type=str, action='store', help="Absolute end time. Format: YYYY-MM-DDTHH:MM:SSZ. Should only be used with --starttime.")

    # Optional customization of preserving/removal behavior
    parser.add_argument('--keep-workdir', default=ON_FAIL, choices=[ON_FAIL, ALWAYS, NEVER] type=str, action='store', help="Customize when to copy the work directory to archive (default: ON_FAIL).")
    parser.add_argument('--keep-builddir', default=ON_FAIL, choices=[ON_FAIL, ALWAYS, NEVER] type=str, action='store', help="Customize when to copy the build directory to archive (default: ON_FAIL).")
    parser.add_argument('--delete-scratch-dir', action='store_true', help="If set, deletes the build and work directories after archiving.")
    parser.add_argument('--delete-run-dir', action='store_true', help="If set, deletes the Run_Archive and Status directories after archiving.")

    # Optional filters to pick a subset of apps/tests
    parser.add_argument('--user', '-u', type=str, action='store', help="Specifies the UNIX user to archive jobs for (default: all).")
    parser.add_argument('--machine', '-m', type=str, action='store', help="Specifies the machine to archive jobs for (default: all).")
    parser.add_argument('--app', type=str, nargs='+', action='append', help="Specifies one or more apps to archive jobs for (default: all).")
    parser.add_argument('--test', type=str, nargs='+', action='append', help="Specifies one or more tests to archive jobs for (default: all).")
    parser.add_argument('--runtag', type=str, action='store', help="Specifies the runtag to archive jobs for (default: all).")

    # Operational tuning
    parser.add_argument('--no-tqdm', action='store_true', help="If set, disables using TQDM progress bars.")
    parser.add_argument('--compress', action='store_true', help="If set, tar's and gzip's the resulting archive directory.")
    parser.add_argument('--limit', type=int, action='store', help="Maximum number of tests to archive.")
    parser.add_argument('--stop-after', type=int, action='store', help="Specify a number of hours after which to cleanly pause archiving and exit.")
    parser.add_argument('--loglevel', default='INFO', choices=["NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL"], type=str, action='store', help="Specify verbosity")
    parser.add_argument('--logfile', default='archive.log', type=str, action='store', help="Name/location of the log file (default: archive.log). Set to /dev/null to disable log file.")

parser = initialize_parser()
args = parser.parse_args()

# Read in the <machine>.ini configuration file #################################
# uses the getDefaultConfigName, which keys off of OLCF_HARNESS_MACHINE
config = rgt_config_file()
logger = rgt_logger_factory.create_rgt_logger(logger_name='rgt_archive_test_utility',
                fh_filepath=args.logfile, logger_threshold_log_level=args.loglevel,
                fh_threshold_log_level=args.loglevel, ch_threshold_log_level=args.loglevel)

# Checking format of provided times ############################################
def check_time_format(s):
    try:
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        logger.doCriticalLogging(f"Invalid time format: {s}. Aborting")
        raise
    return True

# Check time formatting
if args.starttime:
    # Check format
    if not check_time_format(args.starttime):
        logger.doCriticalLogging("Time validation failed. Exiting.")
        exit(1)

if args.endtime:
    # Check format
    if not check_time_format(args.endtime):
        logger.doCriticalLogging("Time validation failed. Exiting.")
        exit(1)

if not (args.time.endswith('y') or args.time.endswith('m') or args.time.endswith('d')):
    logger.doCriticalLogging(f"Unrecognized time parameter: {args.time[0]}.")
    logger.doCriticalLogging(f"This program allows years (y), months (m), or days (d) to be specified as '1y' or '1m' or '1d' for one year, month, or day, respectively.")
    exit(1)
################################################################################

