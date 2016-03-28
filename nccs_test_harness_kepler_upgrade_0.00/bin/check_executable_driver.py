#! /usr/bin/env python

import os
import sys
import subprocess
import getopt
import string
from libraries import status_file

#
# Author: Arnold Tharrington
# Modified: Wayne Joubert
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
    cwd = os.getcwd()
    (dir_head1, dir_tail1) = os.path.split(cwd)
    path1 = os.path.join(dir_head1,"Status",test_id_string,"job_id.txt")
    while (not os.path.lexists(path1)):
        file_obj = open(path1,"r")
        job_id = file_obj.readline()
        file_obj.close()
        job_id = str.strip(job_id)

        

    #
    # Call the check_executable.x script only after the job_id.txt file is created.
    #
    check_command_argv = ["./check_executable.x"]
    for args1 in sys.argv[1:] :
        check_command_argv = check_command_argv + [args1]
        
    check_cmd_process = subprocess.call(check_command_argv)

    #
    # Run report_executable.x, if it exists.
    #

    report_command_argv = ['./report_executable.x']
    if os.path.exists(report_command_argv[0]):
        for args1 in sys.argv[1:] :
            report_command_argv = report_command_argv + [args1]
        report_command_argv = subprocess.call(report_command_argv)

    #
    # Now read the result to the job_status.txt file.
    #
    path2 = os.path.join(dir_head1,"Status",test_id_string,"job_status.txt")
    file_obj2 = open(path2,"r")
    job_correctness = file_obj2.readline()
    file_obj2.close()
    job_correctness = str.strip(job_correctness)

    #
    # Create an instance of the job status and add the correct result to the status file.
    #
    jstatus = status_file.StatusFile(test_id_string,mode="Old")
    jstatus.add_result(job_correctness,mode="Add_Run_Result")

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
