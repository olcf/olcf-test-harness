#! /usr/bin/env python3

import os
import sys
import string
import argparse
import datetime
import shutil
from shlex import split

from libraries.rgt_utilities import unique_text_string, test_work_space, try_symlink
from libraries.layout_of_apps_directory import apps_test_directory_layout
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


def get_app_test_from_scriptdir(scriptdir_path):
    """
    Convert given scripts directory path into app and test names,
    after checking that it is actually a scripts directory
    """
    app = None
    test = None

    (dir_head1, scriptdir) = os.path.split(scriptdir_path)
    if scriptdir == 'Scripts':
        (dir_head2, test) = os.path.split(dir_head1)
        (__, app) = os.path.split(dir_head2)

    return app, test


def get_test_status_dir(apptest_dir, id_string):
    """
    Get Status directory for test instance with given id_string.
    Create directory if it does not exist.
    """
    #
    # spath = apptest_dir/Status/id_string
    # This path should be unique.
    #
    spath = os.path.join(apptest_dir, 'Status', id_string)
    if not os.path.exists(spath):
        os.makedirs(spath)

        #
        # Create convenience link to latest status dir
        #
        latest_lnk = os.path.join(apptest_dir, 'Status', 'latest')
        if os.path.exists(latest_lnk):
            os.unlink(latest_lnk)
        try_symlink(id_string, latest_lnk)

    return spath


def get_test_runarchive_dir(apptest_dir, id_string):
    """
    Get Run_Archive directory for test instance with given id_string.
    Create directory if it does not exist.
    """
    #
    # rpath = apptest_dir/Run_Archive/id_string
    # This path should be unique.
    #
    rpath = os.path.join(apptest_dir, 'Run_Archive', id_string)
    if not os.path.exists(rpath):
        os.makedirs(rpath)

        #
        # Create convenience link to latest Run_Archive dir
        #
        latest_lnk = os.path.join(apptest_dir, 'Run_Archive', 'latest')
        if os.path.exists(latest_lnk):
            os.unlink(latest_lnk)
        try_symlink(id_string, latest_lnk)

    return rpath


def get_test_workspace_path(path_to_workspace, app, test, id_string):
    """
    Get temporary workspace path for apptest instance with given id_string.
    Create it if it does not exist.
    """
    wpath = os.path.join(path_to_workspace, app, test, id_string)
    os.makedirs(wpath, exist_ok=True)
    return wpath


def create_links_from_workspace(test_workspace, status_dir, runarchive_dir):
    #
    # Create convenience links from this workspace to associated
    # Status and Run_Archive directories.
    #
    try_symlink(status_dir, os.path.join(test_workspace, 'Status'))
    try_symlink(runarchive_dir, os.path.join(test_workspace, 'Run_Archive'))
    return


def create_links_to_workspace(srcdir, test_workspace):
    #
    # Create convenience links to associated workspace directories
    #
    try_symlink(os.path.join(test_workspace, 'build_directory'),
                os.path.join(srcdir, 'build_directory'))
    try_symlink(os.path.join(test_workspace, 'workdir'),
                os.path.join(srcdir, 'workdir'))
    return


def backup_status_file(status_dir):
    """ Make a backup copy of master status file """
    #
    # Set the name of the source file (i.e., the status file to backup).
    # parent_dir = status_dir/.. (app/test/Status)
    #
    parent_dir = os.path.dirname(status_dir)
    fname = status_file.StatusFile.FILENAME
    src = os.path.join(parent_dir, fname)

    #
    # Set the name of the destination file (i.e., the backup file)
    #
    currenttime = datetime.datetime.now().isoformat()
    backup_filename = ".backup." + fname + "." + currenttime
    dest = os.path.join(parent_dir, backup_filename)

    #
    # Now copy the status file to the backup file.
    #
    if os.path.exists(src):
        shutil.copyfile(src, dest)


def read_status_file(test_status_dir):
    """ Read test_status_dir/job_status.txt to get job status """
    job_correctness = ""
    fpath = os.path.join(test_status_dir, 'job_status.txt')
    if os.path.exists(fpath):
        jfile = open(fpath, "r")
        job_line = jfile.readline()
        jfile.close()
        job_correctness = str.strip(job_line)
    return job_correctness


def read_job_file(test_status_dir):
    """ Read test_status_dir/job_id.txt to get job id """
    job_id = "0"
    fpath = os.path.join(test_status_dir, 'job_id.txt')
    if os.path.exists(fpath):
        jfile = open(fpath, "r")
        job_line = jfile.readline()
        jfile.close()
        job_id = str.strip(job_line)
    return job_id


def auto_generated_scripts(test_workspace,
                           apptest_dir,
                           unique_id,
                           jstatus,
                           actions):
    """
    Generates and executes scripts to build, run, and check a test.

    This function uses the machine_types library.

    """

    status_dir = get_test_status_dir(apptest_dir, unique_id)

    # Instantiate the machine for this computer.
    mymachine = MachineFactory.create_machine(test_workspace,
                                              unique_id)

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
            mymachine.make_custom_batch_script()
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


def user_generated_scripts(test_workspace,
                           apptest_dir,
                           unique_id,
                           jstatus,
                           actions):
    """
    Executes user-provided build, submit, and check scripts for a test.
    """

    status_dir = get_test_status_dir(apptest_dir, unique_id)
    runarchive_dir = get_test_runarchive_dir(apptest_dir, unique_id)

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

    #
    # Make sure we are executing in app/test/Scripts
    # 
    testscripts = Vargs.scriptsdir
    (app, test) = get_app_test_from_scriptdir(testscripts)
    if app == None or test == None:
        sys.exit(f'HARNESS ERROR: Invalid test scripts directory {testscripts}.')
    if os.getcwd() != testscripts:
        os.chdir(testscripts)
    apptest_dir = os.path.dirname(testscripts)

    #
    # Update my environment with the path to the Scripts directory
    #
    os.putenv('RGT_PATH_TO_SCRIPTS_DIR', testscripts)

    #
    # Prepend path to Scripts directory to my PYTHONPATH
    #
    sys.path.insert(0, testscripts)

    #
    # Check for the existence of the file "kill_test".
    # If the file exists then the program will exit
    # without building and submitting scripts.
    #
    kill_file = apps_test_directory_layout.kill_file
    if os.path.exists(kill_file):
        message = f'The kill file {kill_file} exists. It must be removed to run this test.'
        sys.exit(message)

    # Q: What is the purpose of the testrc file??
    testrc_file = apps_test_directory_layout.rc_file
    if os.path.exists(testrc_file):
        file_obj = open(testrc_file,"r")
        lines = file_obj.readlines()
        file_obj.close()

        attempts = int(lines[0].strip())
        limits = int(lines[1].strip())

        if attempts >= limits:
            return
        else:
            attempts = attempts + 1
            file_obj = open(testrc_file,"w")
            string1 = str(attempts) + "\n"
            string2 = str(limits) + "\n"
            file_obj.write(string1)
            file_obj.write(string2)
            file_obj.close()

    #
    # Get the unique id for this test instance.
    #
    existing_id = True
    unique_id = Vargs.uniqueid
    if unique_id == None:
        existing_id = False
        unique_id = unique_text_string()
        print(f'Generated test unique id: {unique_id}')

    #
    # Get the Status and Run_Archive dirs for this test instance
    #
    status_dir = get_test_status_dir(apptest_dir, unique_id)
    runarchive_dir = get_test_runarchive_dir(apptest_dir, unique_id)

    #
    # Get the temporary workspace path for this test instance
    #
    workspace = test_work_space()
    test_workspace = get_test_workspace_path(workspace, app, test, unique_id)

    #
    # Create links between test workspace and Status and Run_Archive dirs
    #
    create_links_to_workspace(status_dir, test_workspace)
    create_links_to_workspace(runarchive_dir, test_workspace)
    create_links_from_workspace(test_workspace, status_dir, runarchive_dir)

    #
    # Make backup of master status file.
    #
    backup_status_file(status_dir)

    #
    # Add entry to status file.
    #
    mode_str = 'New'
    if existing_id:
        mode_str = 'Old'
    jstatus = status_file.StatusFile(unique_id, mode_str)

    rgt_test_input_file = os.path.join(testscripts,"rgt_test_input.txt")
    if not os.path.isfile(rgt_test_input_file):
        exit_values = user_generated_scripts(test_workspace, apptest_dir,
                                             unique_id, jstatus, actions)
    else:
        exit_values = auto_generated_scripts(test_workspace, apptest_dir,
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
        jspath = os.path.join(status_dir, 'job_status.txt')
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
