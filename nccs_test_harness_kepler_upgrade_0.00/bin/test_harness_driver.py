#! /usr/bin/env python

import os
import sys
import string
import getopt
import shutil
import datetime
from shlex import split
import argparse

from libraries.rgt_utilities import unique_text_string
from libraries.rgt_utilities import test_work_space
from libraries.layout_of_apps_directory import apps_test_directory_layout
from libraries import status_file
from machine_types.machine_factory import MachineFactory


#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

#
# This program coordinates the scripts build_executable.x and submit_executable.x
# and is designed such that it will be called from the Scripts directory.
#
#
def test_harness_driver(argv=None):
        
    
    #
    # Check for the existence of the file "kill_test".
    # If the file exists then the program will exit
    # without building and submitting scripts.
    #
    kill_file = apps_test_directory_layout.kill_file
    if os.path.exists(kill_file):
        return

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
            attempts = attempts +1
            file_obj = open(testrc_file,"w")
            string1 = str(attempts) + "\n"
            string2 = str(limits) + "\n"
            file_obj.write(string1)
            file_obj.write(string2)
            file_obj.close()
            

    my_parser = create_parser()
    Vargs = None
    if argv == None:
        Vargs = my_parser.parse_args()
    else:
        Vargs = my_parser.parse_args(argv)
    resubmit_me = Vargs.r

    #
    # Make backup of master status file.
    #
    backup_status_file()

    #
    # Get the unique id for this test instance.
    #
    unique_id = unique_text_string()

    #
    # Make the Status directory.
    #
    make_path_to_status_dir(unique_id)

    #
    # Add entry to status file.
    #
    jstatus = status_file.StatusFile(unique_id,mode="New")

    #
    # Get the path to workspace for this test instance. 
    #
    workspace = test_work_space()

    #
    # Get the path name of the temporary workspace in path_to_workspace.
    # 
    path_to_tmp_workspace = get_path_to_tmp_workspace(workspace,unique_id)

    #
    # Make the Run_Archive directory.
    #
    make_path_to_Run_Archive_dir(unique_id)

    #
    # Add to environment the path to the Scripts directory.
    #
    currentdir = os.getcwd()
    os.putenv('RGT_PATH_TO_SCRIPTS_DIR',currentdir)

    rgt_test_input_file = os.path.join(currentdir,"rgt_test_input.txt")

    if not os.path.isfile(rgt_test_input_file):
        build_and_submit_exit_value = user_generated_scripts(path_to_tmp_workspace,unique_id,jstatus,resubmit_me)
    else:
        build_and_submit_exit_value = auto_generated_scripts(path_to_tmp_workspace,unique_id,jstatus,resubmit_me)

    return build_and_submit_exit_value

def create_parser():
    my_parser = argparse.ArgumentParser(description="Driver for Application and tests")
        
    my_parser.add_argument("-r",  
                         help="The batch script for the next test will resubmititself",
                         action="store_true")

    return my_parser

def user_generated_scripts(path_to_tmp_workspace,unique_id,jstatus,resubmit_me):
    """
    Executes scripts provided by the user for a test.

    This function runs the submit_executable.x, build_executable.x,
    check_executable.x, report_executable.x.
    
    """
    #
    # Execute the build script.
    #
    build_command = "./build_executable.x "
    build_command_args = "-p " + path_to_tmp_workspace + " -i " + unique_id
    command1 = build_command + build_command_args
    jstatus.log_event(status_file.StatusFile.EVENT_BUILD_START)
    build_exit_value = os.system(command1)
    jstatus.log_event(status_file.StatusFile.EVENT_BUILD_END, build_exit_value)

    #
    # Execute the submit script.
    #
    if resubmit_me:
        submit_command = "./submit_executable.x "
        submit_command_args = "-r " + "-p " + path_to_tmp_workspace + " -i " + unique_id
    else:
        submit_command = "./submit_executable.x "
        submit_command_args = "-p " + path_to_tmp_workspace + " -i " + unique_id

    command2 = submit_command + submit_command_args
    jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_START)
    submit_exit_value = os.system(command2)
    jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_END, submit_exit_value)

    #
    # Log the PBS job id.
    #
    job_id = read_job_id(unique_id)
    jstatus.log_event(status_file.StatusFile.EVENT_JOB_QUEUED, job_id)

    return build_exit_value and submit_exit_value

def auto_generated_scripts(path_to_tmp_workspace,unique_id,jstatus,resubmit_me):
    """
    Generates scripts for the user to build, submit and execute a test.

    This function uses the machine_types library.
    
    """
    
    # Make the batch script.
    mymachine = MachineFactory.create_machine(path_to_tmp_workspace,unique_id)

    # Build the executable for this test on the specified machine
    jstatus.log_event(status_file.StatusFile.EVENT_BUILD_START)
    build_exit_value = mymachine.build_executable()
    print("build_exit_value = " + str(build_exit_value))
    jstatus.log_event(status_file.StatusFile.EVENT_BUILD_END, build_exit_value)

    # Create the batch script
    mymachine.make_batch_script()

    jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_START)
    # Submit the batch file to the scheduler.
    submit_exit_value = mymachine.submit_batch_script()
    jstatus.log_event(status_file.StatusFile.EVENT_SUBMIT_END, submit_exit_value)

    job_id = read_job_id(unique_id)
    print("Job ID = " + job_id)
    jstatus.log_event(status_file.StatusFile.EVENT_JOB_QUEUED, job_id)
    
    return build_exit_value and submit_exit_value

def usage():
    print ("There are two modes of usage as a main program or as a function call")
    print
    print
    print ("Usage as a main program: test_harness_driver.py [-h] [-r]")
    print ("A driver program that orchestates the build and submit")
    print ("scripts.")
    print
    print ("-h, --help           Prints usage information.")                              
    print ("-r                   The batch script for the next test will resubmit")
    print ("                     itself, otherwise the batch script for the next ")
    print ("                     test won't resubmit itself.")
    print 
    print
    print ("Usage as a function: test_harness_driver()")
    print ("A driver program that orchestates the build and submit")
    print ("scripts.")
    print
    print ("-h, --help           Prints usage information.")
    print ("-r                   The batch script for the next test will resubmit")
    print ("                     itself, otherwise the batch script for the next ")
    print ("                     test won't resubmit itself.")
         
def get_path_to_tmp_workspace(path_to_workspace,test_id_string):
    #
    # Get the current working directory.
    #
    cwd = os.getcwd()

    #
    # Get the 3 tail paths in the cwd.
    #
    (dir_head1, dir_tail1) = os.path.split(cwd)
    (dir_head2, dir_tail2) = os.path.split(dir_head1)
    (dir_head3, dir_tail3) = os.path.split(dir_head2)

    #
    # Now join tail2 and tail3 to make the path. This path should be unique.
    #
    path1 = os.path.join(path_to_workspace,dir_tail3,dir_tail2,test_id_string)

    return path1



def make_path_to_status_dir(test_id_string):
    #
    # Get the current working directory.
    #
    cwd = os.getcwd()

    #
    # Get the 3 tail paths in the cwd.
    #
    (dir_head1, dir_tail1) = os.path.split(cwd)

    #
    # Now join dirhead1. This path should be unique.
    #
    path1 = os.path.join(dir_head1,"Status",test_id_string)

    os.makedirs(path1)

def backup_status_file():
    #
    # Get the current working directory.
    #
    cwd = os.getcwd()

    #
    # Get the 3 tail paths in the cwd.
    #
    (dir_head1, dir_tail1) = os.path.split(cwd)


    #
    # Set the name of the source file, the file being backed up.
    #
    src = os.path.join(dir_head1,"Status",status_file.StatusFile.FILENAME)

    #
    # Set the name of the destination file, the name of the backup file.
    #
    currenttime = datetime.datetime.now()
    backup_status_filename = ".backup." + status_file.StatusFile.FILENAME + "." +  currenttime.isoformat() 
    dest = os.path.join(dir_head1,"Status",backup_status_filename)

    #
    # Now copy the status file to the backup file.
    #
    if os.path.lexists(src):
        shutil.copyfile(src,dest)


def make_path_to_Run_Archive_dir(test_id_string):
    #
    # Get the current working directory.
    #
    cwd = os.getcwd()

    #
    # Get the tail paths in the cwd.
    #
    (dir_head1, dir_tail1) = os.path.split(cwd)

    #
    # Now join dirhead1. This path should be unique.
    #
    path1 = os.path.join(dir_head1,"Run_Archive",test_id_string)

    os.makedirs(path1)

def read_job_id(test_id_string):
    #
    # Get the current working directory.
    #
    cwd = os.getcwd()

    #
    # Now join dirhead1. This path should be unique.
    #
    (dir_head1, dir_tail1) = os.path.split(cwd)
    path1 = os.path.join(dir_head1,"Status",test_id_string,"job_id.txt")

    file_obj = open(path1,"r")
    job_id = file_obj.readline()
    file_obj.close()

    job_id = str.strip(job_id)

    return job_id


if __name__ == "__main__":
    test_harness_driver()
