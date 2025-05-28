#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 05-01-2025
################################################################################
# Purpose:
#   Locates and archives tests within the OTH directory structure.
#   This script was developed with the v3.0 release of the OLCF Test Harness
################################################################################

from datetime import datetime
import os
import argparse
import re
import shutil
import tarfile
import sys

# For directory names
from libraries.layout_of_apps_directory import apptest_layout
# For interpreting status files
from libraries.status_file import StatusFile, get_status_info_from_file
# For logging
from libraries.rgt_loggers import rgt_logger_factory

# define some constants
KW_ALWAYS = 'ALWAYS'
KW_NEVER = 'NEVER'
KW_ON_FAIL = 'ON_FAIL'

def initialize_parser():
    # Initialize argparse ##########################################################
    parser = argparse.ArgumentParser(description="Locates and archives tests, condensing test output into a simplified directory structure.")

    # Required information for operation
    parser.add_argument('--path-to-tests', required=True, type=str, action='store', help="Path to the application repository directories (ie, Path_to_tests).")
    parser.add_argument('--path-to-archive', required=True, type=str, action='store', help="Path to the archive location.")

    # Time filtering options:
    parser.add_argument('--starttime', type=str, action='store', help="Absolute start time. Format: YYYY-MM-DDTHH:MM.")
    parser.add_argument('--endtime', type=str, action='store', help="Absolute end time. Format: YYYY-MM-DDTHH:MM.")

    # Optional customization of preserving/removal behavior
    parser.add_argument('--keep-workdir', default=KW_ON_FAIL, choices=[KW_ON_FAIL, KW_ALWAYS, KW_NEVER], type=str, action='store', help=f"Customize when to copy the work directory to archive (default: {KW_ON_FAIL}).")
    parser.add_argument('--keep-builddir', default=KW_ON_FAIL, choices=[KW_ON_FAIL, KW_ALWAYS, KW_NEVER], type=str, action='store', help=f"Customize when to copy the build directory to archive (default: {KW_ON_FAIL}).")
    parser.add_argument('--delete-scratch-dir', action='store_true', help="DANGEROUS. If set, deletes the build and work directories after archiving.")
    parser.add_argument('--delete-run-dir', action='store_true', help="DANGEROUS. If set, deletes the Run_Archive and Status directories after archiving.")

    # Optional filters to pick a subset of apps/tests
    parser.add_argument('--users', type=str, nargs='+', action='store', help="Specifies one or more UNIX users to archive jobs for (default: all).")
    parser.add_argument('--machines', type=str, nargs='+', action='store', help="Specifies one or more machines to archive jobs for (default: all).")
    parser.add_argument('--apps', type=str, nargs='+', action='store', help="Specifies one or more apps to archive jobs for (default: all).")
    parser.add_argument('--tests', type=str, nargs='+', action='store', help="Specifies one or more tests to archive jobs for (default: all).")
    parser.add_argument('--runtags', type=str, nargs='+', action='store', help="Specifies one or more runtags to archive jobs for (default: all). This filter supports regex.")

    # Operational tuning
    parser.add_argument('--no-tqdm', action='store_true', help="If set, disables using TQDM progress bars.")
    parser.add_argument('--print-summary', action='store_true', help="If set, prints a summary of how many test instances are archived for each app-test.")
    parser.add_argument('--force', action='store_true', help="DANGEROUS. If set, will remove the archive of an existing test if found, then re-archive.")
    parser.add_argument('--compress', action='store_true', help="If set, tar's and gzip's the resulting archive directory.")
    parser.add_argument('--limit', type=int, action='store', help="Maximum number of tests to archive.")
    parser.add_argument('--stop-after', type=float, action='store', help="Specify a number of hours after which to cleanly pause archiving and exit.")
    parser.add_argument('--loglevel', default='ERROR', choices=["NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL"], type=str, action='store', help="Specify verbosity")
    parser.add_argument('--logfile', default=os.path.join(os.getcwd(), 'archive.log'), type=str, action='store', help="Name/location of the log file (default: archive.log). Set to /dev/null to disable log file.")

    return parser

def validate_args():
    def check_time_format(s):
        try:
            dt = datetime.strptime(s, "%Y-%m-%dT%H:%M")
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

fh_log_level = 'DEBUG' if args.loglevel == 'DEBUG' else 'INFO'

logger = rgt_logger_factory.create_rgt_logger(logger_name='rgt_archive_test_utility',
                fh_filepath=args.logfile, logger_threshold_log_level=fh_log_level,
                fh_threshold_log_level=fh_log_level, ch_threshold_log_level=args.loglevel)

logger.doCriticalLogging(f"Command-line invocation: {' '.join(sys.argv)}")

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

def should_archive_test(test_path, test_id):
    """ Verifies conditions from --age, --starttime, --endtime, --users, --machines, --runtags are met by a specific test id """
    # Read the latest status file for this test to get time, machine, runtag, and user info
    status_dir = f"{test_path}/{apptest_layout.test_status_dirname}/{test_id}"
    if not os.path.isdir(status_dir):
        logger.doDebugLogging(f"Could not find status directory for test_id {test_id} in {status_dir}. Skipping")
        return False

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
    
    if not latest_status_file:
        logger.doWarningLogging(f"Skipping a test that couldn't find the latest status file for: {status_dir}.")
        return False

    logger.doDebugLogging(f"Using status file {status_dir}/{latest_status_file}")
    event_info = get_status_info_from_file(os.path.join(status_dir, latest_status_file))
    event_time_modified = re.search('([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}):[0-9]{2}\..*', event_info['event_time']).group(1)

    # Verify time conditions are met
    if args.starttime and args.starttime > event_time_modified:
            logger.doDebugLogging(f"Rejecting {test_id} using starttime filter.")
            return False
    if args.endtime and args.endtime < event_time_modified:
        logger.doDebugLogging(f"Rejecting {test_id} using endtime filter.")
        return False

    # If none of the optional filters are set, short-circuit
    if (not args.users) and (not args.machines) and (not args.runtags):
        return True

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

    # Read the latest status file for this test to get machine, runtag, and user info
    test_archive_dir = os.path.join(args.path_to_archive, apptest, 'Archive', test_id)
    test_run_archive = os.path.join(args.path_to_tests, apptest, apptest_layout.test_run_archive_dirname, test_id)
    test_status = os.path.join(args.path_to_tests, apptest, apptest_layout.test_status_dirname, test_id)

    latest_status_file = None
    current_event_num = 0
    status_file_regex = re.compile('^Event_[0-9]+_.*\.txt$')

    for status_file_name in os.listdir(test_status):
        if not status_file_regex.match(status_file_name):
            continue
        event_number = int(status_file_name.split('_')[1]) # used to sort if this is a newer event than current
        if event_number > current_event_num:
            # Then get the info from the status file & log it to the database
            latest_status_file = status_file_name
            current_event_num = event_number

    if not latest_status_file:
        logger.doWarningLogging(f"In archive_test, skipping a test that couldn't find the latest status file for: {status_dir}. This should not be happening.")
        return False

    logger.doDebugLogging(f"Using status file {test_status}/{latest_status_file}")
    # status file used for exit codes and build_directory and workdir paths
    test_info = get_status_info_from_file(os.path.join(test_status, latest_status_file))

    # check for existing archive:
    if os.path.isdir(test_archive_dir):
        if not args.force:
            logger.doWarningLogging(f"Found {apptest}/{test_id} in archive already at {test_archive_dir}. Skipping.")
            return False
        else:
            logger.doWarningLogging(f"Found {apptest}/{test_id} in archive already at {test_archive_dir}. --force is set, so removing this directory.")
            shutil.rmtree(test_archive_dir)
    elif os.path.exists(f'{test_archive_dir}.tar.gz'):
        if not args.force:
            logger.doWarningLogging(f"Found a compressed {apptest}/{test_id} in archive already at {test_archive_dir}.tar.gz. Skipping.")
            return False
        else:
            logger.doWarningLogging(f"Found {apptest}/{test_id} in archive already at {test_archive_dir}.tar.gz. --force is set, so removing this tarball.")
            os.remove(f'{test_archive_dir}.tar.gz')

    # make Archive directory if it doesn't already exist
    if not os.path.isdir(os.path.dirname(test_archive_dir)):
        os.makedirs(os.path.dirname(test_archive_dir))

    # Archive -- use shutil.copytree to copy the current Run_Archive with sym-links for build_directory and workdir
    shutil.copytree(test_run_archive, test_archive_dir, symlinks=True)
    # remove build_directory and workdir sym-links in Archive
    os.unlink(os.path.join(test_archive_dir, apptest_layout.test_run_dirname))
    os.unlink(os.path.join(test_archive_dir, apptest_layout.test_build_dirname))
    # copy the real build_directory and workdir directories if they exist & if flags are right
    test_failed = False
    if (not test_info['event_value'] == '0') and (not test_info['event_name'] == 'job_queued') and (not test_info['event_name'] == 'submit_end'):
        test_failed = True

    # handle build_directory copying
    if (args.keep_builddir == KW_ALWAYS) or (args.keep_builddir == KW_ON_FAIL and test_failed):
        if os.path.isdir(test_info['build_directory']):
            shutil.copytree(test_info['build_directory'], os.path.join(test_archive_dir, apptest_layout.test_build_dirname), symlinks=True)
        else:
            logger.doInfoLogging(f"Build directory for {apptest}/{test_id} does not exist in {test_info['build_directory']}. Skipping copying build_directory.")

    # handle build_directory copying
    if (args.keep_workdir == KW_ALWAYS) or (args.keep_workdir == KW_ON_FAIL and test_failed):
        if os.path.isdir(test_info['workdir']):
            shutil.copytree(test_info['workdir'], os.path.join(test_archive_dir, apptest_layout.test_run_dirname), symlinks=True)
        else:
            logger.doInfoLogging(f"Work directory for {apptest}/{test_id} does not exist in {test_info['workdir']}. Skipping copying workdir.")

    # Compress
    if args.compress:
        with tarfile.open(f'{test_archive_dir}.tar.gz', "w:gz") as test_archive_tar:
            test_archive_tar.add(f'{test_archive_dir}', arcname=f'{test_id}')
        # Remove existing directory once compression is done
        shutil.rmtree(test_archive_dir)

    # Clean-up based off command-line flags --delete-scratch-dir and --delete-run-dir
    if args.delete_scratch_dir and os.path.isdir(test_info['workdir']):
        logger.doDebugLogging(f"Removing scratch directory for test {apptest}/{test_id}.")
        # scratch directory for this test is the parent directory of workdir or build_directory
        shutil.rmtree(os.path.dirname(test_info['workdir']))

    if args.delete_run_dir:
        logger.doDebugLogging(f"Removing Run_Archive and Status directories for test {apptest}/{test_id}.")
        shutil.rmtree(test_run_archive)
        shutil.rmtree(test_status)

    return True

def archive_apptest_common_files(apptest):
    """ Archives app-Source, test-Scripts, and test-Source directories, if they are not already archived """

    test_archive_dir = os.path.join(args.path_to_archive, apptest)
    if os.path.isdir(os.path.join(test_archive_dir, apptest_layout.test_scripts_dirname)) and \
        os.path.isdir(os.path.join(os.path.dirname(test_archive_dir), apptest_layout.app_source_dirname)) \
        and not args.force:
        return False
    elif args.force:
        # then remove any common files, to replace later in this function
        if os.path.isdir(os.path.join(test_archive_dir, apptest_layout.test_scripts_dirname)):
            shutil.rmtree(os.path.join(test_archive_dir, apptest_layout.test_scripts_dirname))
        if os.path.isdir(os.path.join(test_archive_dir, apptest_layout.test_source_dirname)):
            shutil.rmtree(os.path.join(test_archive_dir, apptest_layout.test_source_dirname))
        if os.path.isdir(os.path.join(os.path.dirname(test_archive_dir), apptest_layout.app_source_dirname)):
            shutil.rmtree(os.path.join(os.path.dirname(test_archive_dir), apptest_layout.app_source_dirname))

    apptest_root = os.path.join(args.path_to_tests, apptest)
    test_scripts = os.path.join(apptest_root, apptest_layout.test_scripts_dirname)
    test_source = os.path.join(apptest_root, apptest_layout.test_source_dirname)
    app_source = os.path.join(os.path.dirname(apptest_root), apptest_layout.app_source_dirname)

    # app/Source
    if not os.path.isdir(os.path.join(os.path.dirname(test_archive_dir), apptest_layout.app_source_dirname)):
        shutil.copytree(app_source, os.path.join(os.path.dirname(test_archive_dir), apptest_layout.app_source_dirname), symlinks=True)

    # app/test/Source
    if os.path.isdir(test_source):
        shutil.copytree(test_source, os.path.join(test_archive_dir, apptest_layout.test_source_dirname), symlinks=True)

    # app/test/Scripts
    shutil.copytree(test_scripts, os.path.join(test_archive_dir, apptest_layout.test_scripts_dirname), symlinks=True)

    return True

# Handle --no-tqdm flag
if not args.no_tqdm:
    try:
        import tqdm
    except ModuleNotFoundError:
        logger.doWarningLogging("Python module 'tqdm' not found. Turning off TQDM progress bars.")
        args.no_tqdm = True
        pass

# Key: apptest name, value: number of tests archived
archive_counts = {}
for apptest in my_apptests:
    archive_counts[apptest] = 0

test_id_regex = re.compile('^[0-9]+\.[0-9]+$')

total_logged = 0
limit_reached = False

timestart = datetime.now()

for apptest in my_apptests:
    # this output message may help with the multiple TQDM progress bars
    logger.doErrorLogging(f"Archiving tests for {apptest}.")
    # Handle --no-tqdm flag
    my_tests = os.listdir(os.path.join(args.path_to_tests, apptest, apptest_layout.test_run_archive_dirname))
    if not args.no_tqdm:
        my_tests_for = tqdm.tqdm(my_tests)
    else:
        my_tests_for = my_tests
    # We assume that Run_Archive and Status hold the same set of test IDs, and that there is at least 1 test_id in there
    for testid in my_tests_for:
        if not test_id_regex.match(testid):
            logger.doDebugLogging(f"Excluding test ID that does not match regex: {testid}")
        elif should_archive_test(f"{args.path_to_tests}/{apptest}", testid):
            # Then this run passed any other validation checks and we should archive this test
            logger.doInfoLogging(f"Logging {apptest}/{testid}")
            exit_code = archive_test(apptest, testid)
            # a warning will already be printed by the archive_test function if the test fails to archive
            if exit_code:
                total_logged += 1
                archive_counts[apptest] += 1

        timenow = datetime.now()
        time_elapsed_dt = timenow - timestart
        total_hours = float(time_elapsed_dt.seconds) / float(60 * 60)
        if args.limit and total_logged == args.limit:
            logger.doCriticalLogging("Reached the maximum number of tests to archive set by --limit. Exiting.")
            limit_reached = True
            break
        elif args.stop_after and total_hours > args.stop_after:
            logger.doCriticalLogging("Reached the maximum amount of time set by --stop-after. Exiting.")
            limit_reached = True
            break

    # If we archived more than 1 run for this test, make sure the app's Source directory and the test's Scripts/Source directories exist
    if archive_counts[apptest] > 0:
        archive_apptest_common_files(apptest)

    if limit_reached:
        break


if args.print_summary:
    logger.doCriticalLogging("Archive Summary Statistics ---------------------------------------------------------------")
    for apptest in archive_counts.keys():
        logger.doCriticalLogging(f"{apptest: <80}:{str(archive_counts[apptest]): >9}")
    logger.doCriticalLogging(f"Total: {str(total_logged)}")
