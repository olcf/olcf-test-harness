#! /usr/bin/env python3

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# Scientific Computing Group.
#
# Modified by: Veronica G. Vergara Larrea (vergaravg@ornl.gov)
# User Assistance Group.
#
# National Center for Computational Sciences
# Oak Ridge National Laboratory
#

# Python imports
import argparse
import datetime
import getpass
import logging
import os
import shutil
import stat
import string
import subprocess
import sys

from shlex import split

# Harness imports
from libraries.subtest_factory import SubtestFactory
from libraries.layout_of_apps_directory import apptest_layout as layout
from libraries.layout_of_apps_directory import get_layout_from_scriptdir
from libraries.layout_of_apps_directory import get_path_to_logfile_from_scriptdir
from libraries import rgt_utilities
from libraries.config_file import rgt_config_file
from libraries.status_file_factory import StatusFileFactory
from libraries import status_file
from libraries.rgt_loggers import rgt_logger_factory
from machine_types.machine_factory import MachineFactory
from machine_types.base_machine import SetBuildRTEError

DEFAULT_CONFIGURE_FILE = rgt_config_file.getDefaultConfigFile()
"""
The default configuration filename.

The configuration file contains the machine settings, number of CPUs
per node, etc., for the machine the harness is being run on. Each machine
has a default configuration file that will be used unless another
configuration is specified by the command line or input file.

"""

MODULE_THRESHOLD_LOG_LEVEL = "DEBUG"
"""str : The logging level for this module. """

MODULE_LOGGER_NAME = __name__
"""The logger name for this module."""

def get_log_level():
    """Returns the test harness driver threshold log level.

    Returns
    -------
    int
    """
    return MODULE_THRESHOLD_LOG_LEVEL

def get_logger_name():
    """Returns the logger name for this module."""
    return MODULE_LOGGER_NAME

def create_parser():
    my_parser = argparse.ArgumentParser(description="Application Test Driver",
                                        allow_abbrev=False)
    my_parser.add_argument('-b', '--build',
                           help='Build the application test',
                           action='store_true')
    my_parser.add_argument('-sb', '--separate-build-stdio',
                           help='Separate the stdout and stderr of a build',
                           action='store_true')
    my_parser.add_argument('-c', '--check',
                           help='Check the application test results',
                           action='store_true')
    my_parser.add_argument('-C', '--configfile',
                           required=False,
                           default=DEFAULT_CONFIGURE_FILE,
                           type=str,
                           help="Configuration file name (default: %(default)s)")
    my_parser.add_argument('-d', '--scriptsdir',
                           default=os.getcwd(),
                           help='Provide full path to app/test/Scripts directory (default: current working directory)')
    my_parser.add_argument('-i', '--uniqueid',
                           help='Use previously generated unique id')
    my_parser.add_argument('-l', '--launchid',
                           required=False,
                           type=str,
                           help='Annotate test status with given harness launch id')
    my_parser.add_argument('--loglevel',
                           default='WARNING',
                           choices=['NOTSET', 'notset', 'DEBUG', 'debug', 'INFO', 'info', 'WARNING', 'warning', 'ERROR', 'error', 'CRITICAL', 'critical'],
                           help='Control the level of information printed to stdout.')
    my_parser.add_argument('-r', '--resubmit',
                           help='Have the application test batch script resubmit itself, optionally for a total submission count of N. Leave off N for infinite submissions.',
                           action='store', nargs='?', type=int, const=-1, default=False)
    my_parser.add_argument('-R', '--run',
                           help='Run the application test batch script (NOTE: for use within a job)',
                           action='store_true')
    my_parser.add_argument('-s', '--submit',
                           help='Submit the application test batch script',
                           action='store_true')
    return my_parser


def backup_status_file(test_status_dir):
    """ Make a backup copy of master status file """
    #
    # Set the name of the source file (i.e., the status file to backup).
    # status_dir = test_status_dir/.. (i.e., app/test/Status)
    #
    status_dir = os.path.dirname(test_status_dir)
    fname = status_file.StatusFile.FILENAME
    src = os.path.join(status_dir, fname)

    #
    # Set the name of the destination file (i.e., the backup file)
    #
    currenttime = datetime.datetime.now().isoformat()
    backup_filename = ".backup." + fname + "." + currenttime
    dest = os.path.join(status_dir, backup_filename)

    #
    # Now copy the status file to the backup file.
    #
    if os.path.exists(src):
        shutil.copyfile(src, dest)

def read_job_file(test_status_dir):
    """ Read test_status_dir/job_id.txt to get job id """
    job_id = "0"
    fpath = os.path.join(test_status_dir, layout.job_id_filename)
    if os.path.exists(fpath):
        jfile = open(fpath, "r")
        job_line = jfile.readline()
        jfile.close()
        job_id = str.strip(job_line)
    return job_id


def auto_generated_scripts(harness_config,
                           apptest,
                           jstatus,
                           launch_id,
                           actions,
                           a_logger,
                           separate_build_stdio=False):
    """
    Generates and executes scripts to build, run, and check a test.

    This function uses the machine_types library.

    """

    messloc = "In function {functionname}:".format(functionname="auto_generated_scripts")

    status_dir = apptest.get_path_to_status()
    ra_dir = apptest.get_path_to_runarchive()

    # Instantiate the machine for this computer.
    mymachine = MachineFactory.create_machine(harness_config, apptest, separate_build_stdio=separate_build_stdio)

    #-----------------------------------------------------
    # In this section we build the binary.               -
    #                                                    -
    #-----------------------------------------------------
    build_exit_value = 0
    if actions['build']:
        # Build the executable for this test on the specified machine
        jstatus.log_event(status_file.StatusFile.EVENT_BUILD_START)
        try:
            build_exit_value = mymachine.build_executable()
        except SetBuildRTEError as error:
            message = f"{messloc} Unable to set the build runtime environnment."
            message += error.message
            a_logger.doCriticalLogging(message)
        finally:
            jstatus.log_event(status_file.StatusFile.EVENT_BUILD_END, build_exit_value)

    #-----------------------------------------------------
    # In this section we run the the binary.             -
    #                                                    -
    #-----------------------------------------------------

    # set launch id
    mymachine.test_config.set_launch_id(launch_id)

    job_id = "0"
    submit_exit_value = 0
    if actions['submit'] and (build_exit_value != 0):
        submit_exit_value = 1
        message = f"{messloc} No submit action due to prior failed build."
        a_logger.doCriticalLogging(message)
    elif actions['submit'] and (build_exit_value == 0):

        # determine run count and max
        run_count = 1
        max_count = 1
        max_subs_cfg = mymachine.test_config.get_max_submissions()
        if not max_subs_cfg:
            # Ensure we have a valid string so the template variable can resolve
            mymachine.test_config.set_max_submissions("-1")
        else:
            # If test.ini specified a finite amount of submissions (max_submissions):
            #   on 1st iteration, use the value from test.ini file
            #   on further iterations, get the resubmit count from `test_harness_driver.py -r N` invocation, passed through actions['resubmit']
            max_subs_count = int(max_subs_cfg)

            resub_count = actions['resubmit']
            if resub_count == -1: # 1st iteration
                resub_count = max_subs_count

            # decrement the value to set the resubmission count for the next test_harness_driver run
            resub_count -= 1

            run_count = max_subs_count - resub_count
            max_count = max_subs_count

            # update test config parameter for substitution in batch script we're about to create
            mymachine.test_config.set_max_submissions(str(resub_count))

        run_count_str = f'{run_count}/{max_count}'


        # Create the batch script
        make_batch_script_status = mymachine.make_batch_script()

        # Submit the batch script
        if make_batch_script_status:
            # Submit the batch script
            jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_START, run_count_str)
            try:
                submit_exit_value = mymachine.submit_batch_script()
            finally:
                jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_END, submit_exit_value)

            if submit_exit_value == 0:
                # Log the job id.
                job_id = read_job_file(status_dir)
                if job_id != "0":
                    jstatus.log_event(status_file.StatusFile.EVENT_JOB_QUEUED, job_id)
                else:
                    message = f"{messloc} Submit error, failed to retrieve the job id."
                    a_logger.doCriticalLogging(message)
                    submit_exit_value = 1

    run_exit_value = 0
    if actions['run']:
        # The 'run' action should be executed within a job

        # Create the batch script
        jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_START, str('1/1'))
        make_batch_script_status = mymachine.make_batch_script()
        jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_END, 0)

        # Find the current job id and write it to the associated status file
        mymachine.write_jobid_to_status()
        job_id = read_job_file(status_dir)
        if make_batch_script_status and job_id != "0":
            jstatus.log_event(status_file.StatusFile.EVENT_JOB_QUEUED, job_id)

            # now run the batch script as a subprocess
            batch_script = os.path.join(ra_dir, mymachine.test_config.get_batch_file())
            os.chmod(batch_script, (stat.S_IREAD|stat.S_IWRITE|stat.S_IEXEC))
            args = [batch_script]
            run_outfile = os.path.join(ra_dir, "output_run.txt")
            run_stdout = open(run_outfile, "w")
            p = subprocess.Popen(args, stdout=run_stdout, stderr=subprocess.STDOUT)
            p.wait()
            run_exit_value = p.returncode
            run_stdout.close()
        else:
            message = f"{messloc} Run error, failed to retrieve the job id."
            a_logger.doCriticalLogging(message)
            run_exit_value = 1

    #-----------------------------------------------------
    # In this section we check the the results.          -
    #                                                    -
    #-----------------------------------------------------
    check_exit_value = 0
    if actions['check']:
        if not actions['submit']:
            job_id = read_job_file(status_dir)
        if job_id != "0":
            jstatus.log_event(status_file.StatusFile.EVENT_CHECK_START)
            check_exit_value = mymachine.check_executable()
            mymachine.start_report_executable()
            mymachine.log_to_db()
        else:
            message = f"{messloc} check error, failed to retrieve the job id."
            a_logger.doCriticalLogging(message)
            check_exit_value = 1

    exit_values = {
        'build'  : build_exit_value,
        'check'  : check_exit_value,
        'run'    : run_exit_value,
        'submit' : submit_exit_value
    }
    return exit_values


# This program coordinates the scripts build_executable.x and submit_executable.x
# and is designed such that it will be called from the Scripts directory.
#
def test_harness_driver(argv=None):
    import time

    #
    # Parse arguments
    #
    my_parser = create_parser()
    Vargs = None
    if argv == None:
        Vargs = my_parser.parse_args()
    else:
        Vargs = my_parser.parse_args(argv)

    do_build = Vargs.build
    do_check = Vargs.check
    do_submit = Vargs.submit
    do_run = Vargs.run

    #
    # If none of the individual actions were specified, act
    # like the previous version and do 'build + submit'
    #
    if not (do_build or do_submit or do_check or do_run):
        do_build  = True
        do_submit = True

    resubmit_count = -1 # -1 means resubmit forever until stopped
    if do_submit:
        if Vargs.resubmit:
            resubmit_count = int(Vargs.resubmit)
            if resubmit_count == 0:
                # end of max_submissions
                message = 'Resubmit count is 0. Stopping test cycle.\n'
                print(message)
                return 0

    actions = {
        'build'    : do_build,
        'check'    : do_check,
        'run'      : do_run,
        'submit'   : do_submit,
        'resubmit' : resubmit_count
    }

    # Create a harness config (which sets harness env vars)
    harness_cfg = rgt_config_file(configfilename=Vargs.configfile)

    # Get the launch id for this test instance.
    launch_id = Vargs.launchid
    if launch_id == None:
        now_str = datetime.datetime.now().isoformat()
        if len(now_str) == 26: # now_str includes microseconds
            time_str = now_str[0:-4] # strip off last four characters
        else:
            time_str = now_str
        user_str = getpass.getuser()
        testshot_key = 'system_log_tag'
        testshot_str = 'notag'
        testshot_cfg = harness_cfg.get_testshot_config()
        if testshot_key in testshot_cfg.keys():
            testshot_str = testshot_cfg[testshot_key]
        launch_id = f'{testshot_str}/{user_str}@{time_str}'
        print(f'Generated launch id: {launch_id}')
    else:
        print(f'Using launch id: {launch_id}')

    # Get the unique id for this test instance.
    unique_id = Vargs.uniqueid
    if unique_id == None:
        unique_id = rgt_utilities.unique_harness_id()
        print(f'Generated test unique id: {unique_id}')

    # Make sure we are executing in app/test/Scripts
    testscripts = Vargs.scriptsdir
    (apps_root, app, test) = get_layout_from_scriptdir(testscripts)
    if os.getcwd() != testscripts:
        os.chdir(testscripts)

    # Prepend path to Scripts directory to my PYTHONPATH
    sys.path.insert(0, testscripts)

    # Instantiate application subtest
    logger_name = get_logger_name()
    fh_filepath = get_path_to_logfile_from_scriptdir(testscripts,unique_id)
    # Logger threshold screens ALL traffic before it gets to file/console handlers. Set to lowest level
    logger_threshold = MODULE_THRESHOLD_LOG_LEVEL
    # Always set file handler level to MODULE_THRESHOLD_LOG_LEVEL
    fh_threshold_log_level = MODULE_THRESHOLD_LOG_LEVEL
    # loglevel arg controls the console level
    ch_threshold_log_level = Vargs.loglevel
    #print(f"In test_harness_driver, creating logger with name={logger_name}, filepath={fh_filepath}")
    a_logger = rgt_logger_factory.create_rgt_logger(
                                         logger_name=logger_name,
                                         fh_filepath=fh_filepath,
                                         logger_threshold_log_level=logger_threshold,
                                         fh_threshold_log_level=fh_threshold_log_level,
                                         ch_threshold_log_level=ch_threshold_log_level)

    apptest = SubtestFactory.make_subtest(name_of_application=app,
                                          name_of_subtest=test,
                                          local_path_to_tests=apps_root,
                                          logger=a_logger,
                                          tag=unique_id)
    message = "The length of sys.path is " + str(len(sys.path))
    apptest.doInfoLogging(message)

    #
    # Check for the existence of the file "kill_test".
    # If the file exists then the program will return
    # without building and submitting scripts.
    #
    if do_submit:
        kill_file = apptest.get_path_to_kill_file()
        if os.path.exists(kill_file):
            import shutil
            message = f'The kill file {kill_file} exists. It must be removed to run this test.\n'
            message += "Stopping test cycle."
            apptest.doCriticalLogging(message)
            runarchive_dir = apptest.get_path_to_runarchive()
            logging.shutdown()
            shutil.rmtree(runarchive_dir,ignore_errors=True)
            return


    # Create the status and run archive directories for this test instance
    status_dir = apptest.create_test_status()
    ra_dir = apptest.create_test_runarchive()

    # Create the temporary workspace path for this test instance
    workspace = rgt_utilities.harness_work_space()
    apptest.create_test_workspace(workspace)

    # Update environment with the paths to test directories
    apptest_env_vars = {
        'APP_SOURCE_DIR'      : apptest.get_path_to_source(),
        'TEST_SCRIPTS_DIR'    : testscripts,
        'TEST_BUILD_DIR'      : apptest.get_path_to_workspace_build(),
        'TEST_WORK_DIR'       : apptest.get_path_to_workspace_run(),
        'TEST_SOURCE_DIR'     : apptest.get_path_to_test_source(),
        'TEST_STATUS_DIR'     : status_dir,
        'TEST_RUNARCHIVE_DIR' : ra_dir
    }
    rgt_utilities.set_harness_environment(apptest_env_vars, override=True)

    # Make backup of master status file
    backup_status_file(status_dir)

    # We now create the status file if it doesn't already exist.
    logger_name = "status_file."+ app + "__" + test
    fh_filepath = apptest.path_to_status_logfile
    # Logger threshold screens ALL traffic before it gets to file/console handlers. Set to lowest level
    logger_threshold = MODULE_THRESHOLD_LOG_LEVEL
    # Always set file handler level to MODULE_THRESHOLD_LOG_LEVEL
    fh_threshold_log_level = MODULE_THRESHOLD_LOG_LEVEL
    # loglevel arg controls the console level
    ch_threshold_log_level = Vargs.loglevel
    #print(f"In test_harness_driver, creating logger with name={logger_name}, filepath={fh_filepath}")
    sfile_logger = rgt_logger_factory.create_rgt_logger(
                                         logger_name=logger_name,
                                         fh_filepath=fh_filepath,
                                         logger_threshold_log_level=logger_threshold,
                                         fh_threshold_log_level=fh_threshold_log_level,
                                         ch_threshold_log_level=ch_threshold_log_level)
    path_to_status_file = apptest.get_path_to_status_file()
    jstatus = StatusFileFactory.create(path_to_status_file=path_to_status_file,
                                       logger=sfile_logger)

    # Initialize subtest entry 'unique_id' to status file.
    jstatus.initialize_subtest(launch_id, unique_id)

    #
    # Determine whether we are using auto-generated or user-generated
    # scripts based on existence of rgt_test_input file
    #
    input_txt = os.path.join(testscripts, layout.test_input_txt_filename)
    input_ini = os.path.join(testscripts, layout.test_input_ini_filename)
    if (os.path.isfile(input_txt) or os.path.isfile(input_ini)):
        exit_values = auto_generated_scripts(harness_cfg,
                                             apptest,
                                             jstatus,
                                             launch_id,
                                             actions,
                                             a_logger,
                                             Vargs.separate_build_stdio)
    else:
        error_message = "The user generated scripts functionality is no longer supported"
        a_logger.doCriticalLogging(error_message)
        sys.exit(error_message)

    build_exit_value = 0
    if actions['build']:
        build_exit_value = exit_values['build']
        apptest.doInfoLogging(f'build exit value = {build_exit_value}')

    submit_exit_value = 0
    if actions['submit']:
        submit_exit_value = exit_values['submit']
        apptest.doInfoLogging(f'submit exit value = {submit_exit_value}')

    run_exit_value = 0
    if actions['run']:
        run_exit_value = exit_values['run']
        apptest.doInfoLogging(f'run exit value = {run_exit_value}')

    check_exit_value = 0
    if actions['check']:
        check_exit_value = exit_values['check']
        apptest.doInfoLogging(f'check exit value = {check_exit_value}')

        # Now read the result from the job_status.txt file.
        jspath = os.path.join(status_dir, layout.job_status_filename)
        jsfile = open(jspath, "r")
        job_correctness = jsfile.readline()
        jsfile.close()
        job_correctness = str.strip(job_correctness)
        # Log result of status check.
        jstatus.log_event(status_file.StatusFile.EVENT_CHECK_END,
                          job_correctness)

    return (build_exit_value + submit_exit_value + run_exit_value + check_exit_value)


if __name__ == "__main__":
    exit_code = test_harness_driver()
    exit(exit_code)
