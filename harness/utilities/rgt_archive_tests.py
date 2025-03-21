#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 03-20-2025
################################################################################
# Purpose:
#   Locates and archives tests within the OTH directory structure.
#   This script was developed with the v3.0 release of the OLCF Test Harness
################################################################################

from datetime import datetime
import os
import argparse

# For directory names
from libraries.layout_of_apps_directory import apptest_layout
# For interpreting status files
from libraries.status_file import StatusFile, get_status_info_from_file
# For logging
from libraries.rgt_loggers import rgt_logger_factory

# define some constants
ALWAYS = 'ALWAYS'
NEVER = 'NEVER'
ON_FAIL = 'ON_FAIL'

def initialize_parser():
    # Initialize argparse ##########################################################
    parser = argparse.ArgumentParser(description="Locates and archives tests, condensing test output into a simplified directory structure.")

    # Required information for operation
    parser.add_argument('--path-to-tests', required=True, type=str, action='store', help="Path to the application repository directories (ie, Path_to_tests).")
    parser.add_argument('--path-to-archive', required=True, type=str, action='store', help="Path to the archive location.")

    # Time filtering options:
    parser.add_argument('--age', default='6m', type=str, action='store', help="How old a test must be to be archived (default: 6 months).")
    parser.add_argument('--starttime', type=str, action='store', help="Absolute start time. Format: YYYY-MM-DDTHH:MM:SSZ. Overrides --time")
    parser.add_argument('--endtime', type=str, action='store', help="Absolute end time. Format: YYYY-MM-DDTHH:MM:SSZ. Should only be used with --starttime.")

    # Optional customization of preserving/removal behavior
    parser.add_argument('--keep-workdir', default=ON_FAIL, choices=[ON_FAIL, ALWAYS, NEVER], type=str, action='store', help="Customize when to copy the work directory to archive (default: ON_FAIL).")
    parser.add_argument('--keep-builddir', default=ON_FAIL, choices=[ON_FAIL, ALWAYS, NEVER], type=str, action='store', help="Customize when to copy the build directory to archive (default: ON_FAIL).")
    parser.add_argument('--delete-scratch-dir', action='store_true', help="If set, deletes the build and work directories after archiving.")
    parser.add_argument('--delete-run-dir', action='store_true', help="If set, deletes the Run_Archive and Status directories after archiving.")

    # Optional filters to pick a subset of apps/tests
    parser.add_argument('--users', type=str, nargs='+', action='store', help="Specifies one or more UNIX users to archive jobs for (default: all).")
    parser.add_argument('--machines', type=str, nargs='+', action='store', help="Specifies one or more machines to archive jobs for (default: all).")
    parser.add_argument('--apps', type=str, nargs='+', action='store', help="Specifies one or more apps to archive jobs for (default: all).")
    parser.add_argument('--tests', type=str, nargs='+', action='store', help="Specifies one or more tests to archive jobs for (default: all).")
    parser.add_argument('--runtags', type=str, nargs='+', action='store', help="Specifies one or more runtags to archive jobs for (default: all).")

    # Operational tuning
    parser.add_argument('--no-tqdm', action='store_true', help="If set, disables using TQDM progress bars.")
    parser.add_argument('--compress', action='store_true', help="If set, tar's and gzip's the resulting archive directory.")
    parser.add_argument('--limit', type=int, action='store', help="Maximum number of tests to archive.")
    parser.add_argument('--stop-after', type=int, action='store', help="Specify a number of hours after which to cleanly pause archiving and exit.")
    parser.add_argument('--loglevel', default='INFO', choices=["NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL"], type=str, action='store', help="Specify verbosity")
    parser.add_argument('--logfile', default=os.path.join(os.getcwd(), 'archive.log'), type=str, action='store', help="Name/location of the log file (default: archive.log). Set to /dev/null to disable log file.")

    return parser

def validate_args():
    def check_time_format(s):
        try:
            dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            logger.doCriticalLogging(f"Invalid time format: {s}.")
            raise
        return True

    errs = 0
    # Check time formatting
    if args.starttime:
        if not check_time_format(args.starttime):
            logger.doCriticalLogging("Start time validation failed. Exiting.")
            errs += 1
    if args.endtime:
        if not check_time_format(args.endtime):
            logger.doCriticalLogging("End time validation failed. Exiting.")
            errs += 1
    if not (args.age.endswith('y') or args.age.endswith('m') or args.age.endswith('d')):
        logger.doCriticalLogging(f"Unrecognized --age format: {args.age}.")
        logger.doCriticalLogging(f"This program allows years (y), months (m), or days (d) to be specified as '1y' or '1m' or '1d' for one year, month, or day, respectively.")
        errs += 1

    # Check if path to tests exists
    if not os.path.exists(args.path_to_tests):
        logger.doCriticalLogging(f"Path to tests provided by --path-to-tests does not exist: {args.path_to_tests}")
        errs += 1
    ################################################################################
    return errs

def build_apptest_list():
    apptests = []
    for d in os.listdir(args.path_to_tests):
        # implement app-level filtering
        if args.apps and not d in args.apps:
            logger.doInfoLogging(f"App {d} not in the --apps command-line selector. Skipping.")
            continue
        app_source = os.path.join(args.path_to_tests, d, apptest_layout.app_source_dirname)
        if not os.path.isdir(app_source):
            logger.doDebugLogging(f"Ignoring potential app directory due to missing Source directory: {app_source}")
            continue
        logger.doDebugLogging(f"Searching for tests in the following application sub-directory: {d}")
        for t in os.listdir(os.path.join(args.path_to_tests, d)):
            if args.tests and not t in args.tests:
                logger.doInfoLogging(f"Test {d}/{t} not in the --tests command-line selector. Skipping.")
                continue
            if t == apptest_layout.app_source_dirname:
                continue
            test_scripts = os.path.join(args.path_to_tests, d, t, apptest_layout.test_scripts_dirname)
            test_status = os.path.join(args.path_to_tests, d, t, apptest_layout.test_status_dirname)
            test_run_archive = os.path.join(args.path_to_tests, d, t, apptest_layout.test_run_archive_dirname)
            if os.path.isdir(test_scripts) and os.path.isdir(test_status) and os.path.isdir(test_run_archive):
                # then we have a valid test directory
                apptests.append(f'{d}/{t}')
            elif os.path.isdir(test_scripts) and not os.path.isdir(test_run_archive):
                logger.doDebugLogging(f"Excluding test {d}/{t} that has a Scripts directory but no Run_Archive directory.")
    return apptests

parser = initialize_parser()
args = parser.parse_args()

logger = rgt_logger_factory.create_rgt_logger(logger_name='rgt_archive_test_utility',
                fh_filepath=args.logfile, logger_threshold_log_level=args.loglevel,
                fh_threshold_log_level=args.loglevel, ch_threshold_log_level=args.loglevel)

exit_code = validate_args()
if exit_code > 0:
    logger.doCriticalLogging(f"Found {exit_code} total errors. Exiting.")
    exit(1)

# Make the output directory, if it doesn't exist
if not os.path.exists(args.path_to_archive):
    logger.doInfoLogging(f"Creating output directory {args.path_to_archive}")
    os.makedirs(args.path_to_archive)

# Locate candidate directories
my_apptests = build_apptest_list()




