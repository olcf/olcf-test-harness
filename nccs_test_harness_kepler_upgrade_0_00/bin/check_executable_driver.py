#! /usr/bin/env python3

import os
import sys
import subprocess
import getopt
import string
from libraries import status_file
from machine_types.machine_factory import MachineFactory

#
# Author: Arnold Tharrington
# Modified: Wayne Joubert, Veronica G. Vergara Larrea
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

#
# This program drives the check_executable.x script.
# It is designed such that it will be called from the Scripts directory.
#
#
def main():

    #
    # Get the command line arguments.
    #
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hi:p:")

    except getopt.GetoptError:
            usage()
            sys.exit(2)

    #
    # Parse the command line arguments.
    #
    for o, a in opts:
        if o == "-p":
            path_to_results = a
        elif o == "-i":
            test_id_string = a
        elif o == ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()


    #
    # Wait till job_id.txt is created. 
    #
    starting_directory = os.getcwd()
    (dir_head1, dir_tail1) = os.path.split(starting_directory)
    path1 = os.path.join(dir_head1,"Status",test_id_string,"job_id.txt")
    while (not os.path.lexists(path1)):
        file_obj = open(path1,"r")
        job_id = file_obj.readline()
        file_obj.close()
        job_id = str.strip(job_id)

        
    #
    # Call the check_executable.x script only after the job_id.txt file is created.
    #
    jstatus = status_file.StatusFile(test_id_string,mode="Old")
    jstatus.log_event(status_file.StatusFile.EVENT_CHECK_START)

    #
    # Add to environment the path to the Scripts directory.
    #
    os.putenv('RGT_PATH_TO_SCRIPTS_DIR',starting_directory)

    # Need to add the check for the rgt_test_input.txt file here.
    # If the rgt_test_input.txt file exists call user auto generated
    # check script, else call use generated check script.
    rgt_test_input_file = os.path.join(starting_directory,"rgt_test_input.txt")
    if os.path.isfile(rgt_test_input_file):
        auto_generated_check_script(path_to_results, 
                                    test_id_string)
    else:
        user_generated_check_script(path_to_results,
                                    test_id_string)
    

    # Run report_executable.x, if it exists.
    report_command_argv = ['./report_executable.x']
    if os.path.exists(report_command_argv[0]):
        for args1 in sys.argv[1:] :
            report_command_argv = report_command_argv + [args1]
            report_command_argv = subprocess.call(report_command_argv)

    jstatus = status_file.StatusFile(test_id_string,mode="Old")
    jstatus.log_event(status_file.StatusFile.EVENT_CHECK_START)

    #
    # Now read the result to the job_status.txt file.
    #
    path2 = os.path.join(dir_head1,"Status",test_id_string,"job_status.txt")
    file_obj2 = open(path2,"r")
    job_correctness = file_obj2.readline()
    file_obj2.close()
    job_correctness = str.strip(job_correctness)

    # Log result of status check.
    jstatus.log_event(status_file.StatusFile.EVENT_CHECK_END,
                      job_correctness)

    return

def user_generated_check_script(path_to_results,
                                test_id_string):

    path_to_scripts_dir = os.getcwd() 
    sys.path.insert(0,path_to_scripts_dir)
    check_executable_python_file = "./check_executable.py"

    if (os.path.isfile(check_executable_python_file) ):
        import check_executable
        check_executable.check_executable(path_to_results,
                                          test_id_string)
    else:
        check_command_argv = ["./check_executable.x"]
        for args1 in sys.argv[1:] :
            check_command_argv = check_command_argv + [args1]
        check_cmd_process = subprocess.call(check_command_argv)
    
    return

def auto_generated_check_script(path_to_results,
                                test_id_string):
    message =  "The_auto_generated_check_functionality_is_not_implemented."

    starting_directory = os.getcwd()
    (dir_head1, dir_tail1) = os.path.split(starting_directory)
    path2 = os.path.join(dir_head1,"Status",test_id_string,"job_status.txt")

    file_obj2 = open(path2,"w")
    file_obj2.write(message)
    file_obj2.close()

    # When this auto_generated_check_script functionality
    # is implmented we will use the machine class to launch the 
    # check scripts.
    #
    # mymachine = MachineFactory.create_machine(dir_head1,test_id_string)
    #      
    # check_exit_value = mymachine.check_executable()
    # print("check_exit_value = " + str(check_exit_value))

    # report_exit_value = mymachine.report_executable()
    # print("report_exit_value = " + str(report_exit_value))
    return

def usage():
    print ("Usage: check_executable_driver.py [-h|--help] [-i <test_id_string>] [-p <path_to_results>]")
    print ("A driver program that calls check_executable.x")
    print
    print ("-h, --help            Prints usage information.")                              
    print ("-p <path_to_results>  The absoulte path to the results of a test.")
    print ("-i <test_id_string>   The test string unique id.")



if __name__ == "__main__":
    main()
