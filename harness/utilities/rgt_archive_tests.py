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
import re

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
    parser.add_argument('--runtags', type=str, nargs='+', action='store', help="Specifies one or more runtags to archive jobs for (default: all). This filter supports regex.")

    # Operational tuning
    parser.add_argument('--no-tqdm', action='store_true', help="If set, disables using TQDM progress bars.")
    parser.add_argument('--print-summary', action='store_true', help="If set, prints a summary of how many test instances are archived for each app-test.")
    parser.add_argument('--compress', action='store_true', help="If set, tar's and gzip's the resulting archive directory.")
    parser.add_argument('--limit', type=int, action='store', help="Maximum number of tests to archive.")
    parser.add_argument('--stop-after', type=int, action='store', help="Specify a number of hours after which to cleanly pause archiving and exit.")
    parser.add_argument('--loglevel', default='ERROR', choices=["NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL"], type=str, action='store', help="Specify verbosity")
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
# Key: apptest name, value: number of tests archived
archive_counts = {}

test_id_regex = re.compile('^[0-9]+\.[0-9]+$')

def should_archive_test(test_path, test_id):
    """ Verifies conditions from --users, --machines, --runtags are met by a specific test id """
    # Read the latest status file for this test to get machine, runtag, and user info
    status_dir = f"{test_path}/{apptest_layout.test_status_dirname}/{test_id}"
    if not os.path.isdir(status_dir):
        logger.doDebugLogging(f"Could not find status directory for test_id {test_id} in {status_dir}. Skipping")
        return False

    # If none of the optional filters are set, short-circuit
    if (not args.users) and (not args.machines) and (not args.runtags):
        return True

    latest_status_file = None
    current_event_num = 0
    status_file_regex = re.compile('^Event_[0-9]+_.*\.txt$')

    for status_file_name in os.listdir(status_dir):
        if not status_file_regex.match(status_file_name):
            continue
        event_number = int(status_file_name.split('_')[1]) # used to sort if this is a newer event than current
        if event_number > current_event_num:
            # Then get the info from the status file & log it to the database
            latest_status_file = status_file_name
            current_event_num = event_number
    
    logger.doDebugLogging(f"Using status file {status_dir/status_file_name}")
    event_info = get_status_info_from_file(os.path.join(status_dir, status_file_name))

    if args.users:
        if not event_info['user'] in args.users:
            logger.doInfoLogging(f"Excluding test_id {test_id} in {test_path} due to --users filter")
            return False
    if args.machines:
        if not event_info['machine'] in args.machines:
            logger.doInfoLogging(f"Excluding test_id {test_id} in {test_path} due to --machines filter")
            return False
    if args.runtags:
        matched = False
        for runtag_regex in args.runtags:
            if re.match(runtag_regex, event_info['rgt_system_log_tag']):
                matched = True
        if not matched:
            logger.doInfoLogging(f"Excluding test_id {test_id} in {test_path} due to --runtags filter")
            return False

    return True

def archive_test(apptest, test_id):
    """ Archives a test_id to the args.path_to_archive argument """
    return True

# Handle --no-tqdm flag
if not args.no_tqdm:
    import tqdm
    my_apptests_for = tqdm.tqdm(my_apptests)
else:
    my_apptests_for = my_apptests

for apptest in my_apptests_for:
    # We assume that Run_Archive and Status hold the same set of test IDs, and that there is at least 1 test_id in there
    for testid in os.listdir(os.path.join(args.path_to_tests, apptest, apptest_layout.test_run_archive_dirname)):
        if not test_id_regex.match(testid):
            logger.doDebugLogging(f"Excluding test ID that does not match regex: {testid}")
        elif should_archive_test(f"{args.path_to_tests}/{apptest}", testid):
            # Then this run passed any other validation checks and we should archive this test
            logger.doInfoLogging(f"Logging {apptest}/{testid}")
            exit_code = archive_test(apptest, testid)
            if not exit_code:
                logger.doErrorLogging(f"Failed to archive {testid} from {args.path_to_tests}/{apptest}.")
            else:
                if apptest in archive_counts.keys():
                    archive_counts[apptest] += 1
                else:
                    archive_counts[apptest] = 1

    # If we archived more than 1 run for this test, make sure the app's Source directory and the test's Scripts/Source directories exist
    #if archive_counts[apptest] > 0:
        #archive_apptest_common_files(apptest)

if args.print_summary:
    logger.doCriticalLogging("Archive Summary Statistics ---------------------------------------------------------------")
    for apptest in archive_counts.keys():
        logger.doCriticalLogging(f"{apptest: <80}:{str(archive_counts[apptest]): >9}")
