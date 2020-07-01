#! /usr/bin/env python3

import os
import sys
import string
import argparse
import datetime
import shutil
from shlex import split

from libraries.apptest import subtest
from libraries.layout_of_apps_directory import apptest_layout as layout
from libraries.layout_of_apps_directory import get_layout_from_scriptdir
from libraries import rgt_utilities
from libraries import status_file
from machine_types.machine_factory import MachineFactory


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

def create_parser():
    my_parser = argparse.ArgumentParser(description="Application Test Driver",
                                        allow_abbrev=False)
    my_parser.add_argument('-b', '--build',
                           help='Build the application test',
                           action='store_true')
    my_parser.add_argument('-c', '--check',
                           help='Check the application test results',
                           action='store_true')
    my_parser.add_argument('-d', '--scriptsdir',
                           default=os.getcwd(),
                           help='Provide full path to app/test/Scripts directory (default: current working directory)')
    my_parser.add_argument('-i', '--uniqueid',
                           help='Use previously generated unique id')
    my_parser.add_argument('-r', '--resubmit',
                           help='Have the application test batch script resubmit itself',
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


def auto_generated_scripts(apptest,
                           test_workspace,
                           unique_id,
                           jstatus,
                           actions):
    """
    Generates and executes scripts to build, run, and check a test.

    This function uses the machine_types library.

    """

    status_dir = apptest.get_path_to_status()

    # Instantiate the machine for this computer.
    mymachine = MachineFactory.create_machine(apptest)

    build_exit_value = 0
    if actions['build']:
        # Build the executable for this test on the specified machine
        jstatus.log_event(status_file.StatusFile.EVENT_BUILD_START)
        build_exit_value = mymachine.build_executable()
        jstatus.log_event(status_file.StatusFile.EVENT_BUILD_END, build_exit_value)

    submit_exit_value = 0
    job_id = "0"
    if actions['submit']:
        if build_exit_value != 0:
            # do not submit a failed build
            submit_exit_value = 1
        else:
            # Create and submit the batch script
            mymachine.make_batch_script()
            jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_START)
            submit_exit_value = mymachine.submit_batch_script()
            jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_END, submit_exit_value)

        if 0 == submit_exit_value:
            # Log the job id.
            job_id = read_job_file(status_dir)
            if job_id != "0":
                jstatus.log_event(status_file.StatusFile.EVENT_JOB_QUEUED, job_id)
            else:
                print("SUBMIT ERROR: failed to retrieve job id!")
                submit_exit_value = 1

    check_exit_value = 0
    if actions['check']:
        if not actions['submit']:
            job_id = read_job_file(status_dir)
        if job_id != "0":
            jstatus.log_event(status_file.StatusFile.EVENT_CHECK_START)
            check_exit_value = mymachine.check_executable()
            mymachine.report_executable()
        else:
            print("CHECK ERROR: failed to retrieve job id!")
            check_exit_value = 1

    exit_values = {'build': build_exit_value,
                   'check': check_exit_value,
                   'submit': submit_exit_value}
    return exit_values


def user_generated_scripts(apptest,
                           test_workspace,
                           unique_id,
                           jstatus,
                           actions):
    """
    Executes user-provided build, submit, and check scripts for a test.
    """

    status_dir = apptest.get_path_to_status()
    runarchive_dir = apptest.get_path_to_runarchive()

    build_exit_value = 0
    if actions['build']:
        jstatus.log_event(status_file.StatusFile.EVENT_BUILD_START)
        build_exit_value = execute_user_build_script(test_workspace, unique_id)
        jstatus.log_event(status_file.StatusFile.EVENT_BUILD_END, build_exit_value)

    submit_exit_value = 0
    job_id = "0"
    if actions['submit']:
        if build_exit_value != 0:
            # do not submit a failed build
            submit_exit_value = 1
        else:
            jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_START)
            submit_exit_value = execute_user_submit_script(test_workspace,
                                                           unique_id,
                                                           actions['resubmit'])
            jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_END, submit_exit_value)

        if 0 == submit_exit_value:
            # Log the job id.
            job_id = read_job_file(status_dir)
            if job_id != "0":
                jstatus.log_event(status_file.StatusFile.EVENT_JOB_QUEUED, job_id)
            else:
                print("SUBMIT ERROR: failed to retrieve job id!")
                submit_exit_value = 1

    check_exit_value = 0
    if actions['check']:
        if not actions['submit']:
            job_id = read_job_file(status_dir)
        if job_id != "0":
            jstatus.log_event(status_file.StatusFile.EVENT_CHECK_START)
            check_exit_value = execute_user_check_script(runarchive_dir, unique_id)
        else:
            print("CHECK ERROR: failed to retrieve job id!")
            check_exit_value = 1

    exit_values = {'build': build_exit_value,
                   'check': check_exit_value,
                   'submit': submit_exit_value}
    return exit_values


def execute_user_build_script(test_workspace, unique_id):
    # save current dir
    path_to_scripts_dir = os.getcwd()

    #
    # Use build_executable.py if it exists.
    # Otherwise, use build_executable.x script.
    #
    python_file = "./build_executable.py"
    script_file = "./build_executable.x"
    if os.path.isfile(python_file):
        # Call build_executable.py as a main program.
        import build_executable
        build_exit_value = build_executable.build_executable(test_workspace,
                                                             unique_id)
    elif os.path.isfile(script_file):
        # Execute the build script via os.system().
        build_command = script_file + " -p " + test_workspace + " -i " + unique_id
        build_exit_value = os.system(build_command)
    else:
        print("BUILD ERROR: no build script found!")
        build_exit_value = 1

    # restore current dir
    os.chdir(path_to_scripts_dir)

    return build_exit_value


def execute_user_submit_script(test_workspace, unique_id, resubmit):
    # save current dir
    path_to_scripts_dir = os.getcwd()

    #
    # Use submit_executable.py if it exists.
    # Otherwise, use submit_executable.x script.
    #
    python_file = "./submit_executable.py"
    script_file = "./submit_executable.x"
    if os.path.isfile(python_file):
        # Call submit_executable.py as a main program.
        import submit_executable
        submit_exit_value = submit_executable.submit_executable(test_workspace,
                                                                unique_id,
                                                                batch_recursive_mode=resubmit)
    elif os.path.isfile(script_file):
        # Execute the submit script via os.system().
        submit_command = script_file + " -p " + test_workspace + " -i " + unique_id
        if resubmit:
            submit_command += " -r"
        submit_exit_value = os.system(submit_command)
    else:
        print("SUBMIT ERROR: no submit script found!")
        submit_exit_value = 1

    # restore current dir
    os.chdir(path_to_scripts_dir)

    return submit_exit_value


def execute_user_check_script(path_to_results, unique_id):
    # save current dir
    path_to_scripts_dir = os.getcwd()

    #
    # Use check_executable.py if it exists.
    # Otherwise, use check_executable.x script.
    #
    python_file = "./check_executable.py"
    script_file = "./check_executable.x"
    if os.path.isfile(python_file):
        # Call check_executable.py as a main program.
        import check_executable
        check_exit_value = check_executable.check_executable(path_to_results, unique_id)
    elif os.path.isfile(script_file):
        # Execute the check script via os.system().
        check_command = script_file + " -p " + path_to_results + " -i " + unique_id
        check_exit_value = os.system(check_command)
    else:
        # check scripts are optional
        check_exit_value = 0

    #
    # Use report_executable.py if it exists.
    # Otherwise, use report_executable.x script.
    #
    report_python_file = "./report_executable.py"
    report_script_file = "./report_executable.x"
    report_exit_value = 0
    if os.path.isfile(report_python_file):
        # Call report_executable.py as a main program.
        import report_executable
        report_exit_value = report_executable.report_executable(path_to_results, unique_id)
    elif os.path.isfile(report_script_file):
        # Execute the report script via os.system().
        report_command = report_script_file + " -p " + path_to_results + " -i " + unique_id
        report_exit_value = os.system(report_command)
    else:
        # check scripts are optional
        report_exit_value = 0

    # restore current dir
    os.chdir(path_to_scripts_dir)

    # Q: Do we care if report_executable fails?
    return check_exit_value + report_exit_value


#
# This program coordinates the scripts build_executable.x and submit_executable.x
# and is designed such that it will be called from the Scripts directory.
#
def test_harness_driver(argv=None):

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

    #
    # If none of the individual actions were specified, act
    # like the previous version and do build + submit
    #
    if not (do_build or do_submit or do_check):
        do_build  = True
        do_submit = True

    do_resubmit = False
    if do_submit:
        do_resubmit = Vargs.resubmit

    actions = {'build'    : do_build,
               'check'    : do_check,
               'submit'   : do_submit,
               'resubmit' : do_resubmit}

    # Get the unique id for this test instance.
    existing_id = True
    unique_id = Vargs.uniqueid
    if unique_id == None:
        existing_id = False
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
    apptest = subtest(name_of_application=app,
                      name_of_subtest=test,
                      local_path_to_tests=apps_root,
                      harness_id=unique_id)

    if do_submit:
        # Check for the existence of the file "kill_test".
        # If the file exists then the program will exit
        # without building and submitting scripts.
        kill_file = apptest.get_path_to_kill_file()
        if os.path.exists(kill_file):
            message = f'The kill file {kill_file} exists. It must be removed to run this test.'
            sys.exit(message)

        # Q: What is the purpose of the testrc file??
        testrc_file = apptest.get_path_to_rc_file()
        if os.path.exists(testrc_file):
            file_obj = open(testrc_file,"r")
            lines = file_obj.readlines()
            file_obj.close()

            attempts = int(lines[0].strip())
            limits = int(lines[1].strip())

            if attempts >= limits:
                message = f'Number of tests {attempts} exceeds limit {limits}.'
                sys.exit(message)
            else:
                attempts = attempts + 1
                file_obj = open(testrc_file,"w")
                string1 = str(attempts) + "\n"
                string2 = str(limits) + "\n"
                file_obj.write(string1)
                file_obj.write(string2)
                file_obj.close()

    # Create the status and run archive directories for this test instance
    status_dir = apptest.create_test_status()
    ra_dir = apptest.create_test_runarchive()

    # Create the temporary workspace path for this test instance
    workspace = rgt_utilities.harness_work_space()
    test_workspace = apptest.create_test_workspace(workspace)

    # Update environment with the paths to test directories
    os.putenv('RGT_APP_SOURCE_DIR', apptest.get_path_to_source())
    os.putenv('RGT_TEST_SCRIPTS_DIR', testscripts)
    os.putenv('RGT_TEST_BUILD_DIR', apptest.get_path_to_workspace_build())
    os.putenv('RGT_TEST_WORK_DIR', apptest.get_path_to_workspace_run())
    os.putenv('RGT_TEST_STATUS_DIR', status_dir)
    os.putenv('RGT_TEST_RUNARCHIVE_DIR', ra_dir)

    # Make backup of master status file
    backup_status_file(status_dir)

    # Add entry to status file
    mode_str = 'New'
    if existing_id:
        mode_str = 'Old'
    jstatus = status_file.StatusFile(unique_id, mode_str)

    #
    # Determine whether we are using auto-generated or user-generated
    # scripts based on existence of rgt_test_input file
    #
    input_txt = os.path.join(testscripts, layout.test_input_txt_filename)
    input_ini = os.path.join(testscripts, layout.test_input_ini_filename)
    if (os.path.isfile(input_txt) or os.path.isfile(input_ini)):
        exit_values = auto_generated_scripts(apptest, test_workspace,
                                             unique_id, jstatus, actions)
    else:
        exit_values = user_generated_scripts(apptest, test_workspace,
                                             unique_id, jstatus, actions)

    build_exit_value = 0
    if actions['build']:
        build_exit_value = exit_values['build']
        print("build_exit_value = " + str(build_exit_value))

    submit_exit_value = 0
    if actions['submit']:
        submit_exit_value = exit_values['submit']
        print("submit_exit_value = " + str(submit_exit_value))

    check_exit_value = 0
    if actions['check']:
        check_exit_value = exit_values['check']
        print("check_exit_value = " + str(check_exit_value))

        # Now read the result from the job_status.txt file.
        jspath = os.path.join(status_dir, layout.job_status_filename)
        jsfile = open(jspath, "r")
        job_correctness = jsfile.readline()
        jsfile.close()
        job_correctness = str.strip(job_correctness)
        # Log result of status check.
        jstatus.log_event(status_file.StatusFile.EVENT_CHECK_END,
                          job_correctness)

    return build_exit_value + submit_exit_value + check_exit_value


if __name__ == "__main__":
    test_harness_driver()
