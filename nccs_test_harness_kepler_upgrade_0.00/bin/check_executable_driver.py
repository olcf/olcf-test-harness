#! /usr/bin/env python

import os
import sys
import popen2
import getopt
import string
from libraries import status_file

#
# Author: Arnold Tharrington
# Email: arnoldt@ornl.gov
# National Center of Computational Science, Scientifc Computing Group.
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
        job_id = string.strip(job_id)

        

    #
    # Call the check_executable.x script only after the job_id.txt file is created.
    #
    check_command = "./check_executable.x"
    for args1 in sys.argv[1:] :
        check_command = check_command + " " + args1
    check_job = popen2.Popen3(check_command)
    check_job.wait()

    #
    # Run report_executabe.x, if it exists.
    #

    report_command = './report_executable.x'
    if os.path.exists(report_command):
        for args1 in sys.argv[1:] :
            report_command = report_command + " " + args1
        report_job = popen2.Popen3(report_command)
        report_job.wait()

    #
    # Now read the result to the job_status.txt file.
    #
    path2 = os.path.join(dir_head1,"Status",test_id_string,"job_status.txt")
    file_obj2 = open(path2,"r")
    job_correctness = file_obj2.readline()
    file_obj2.close()
    job_correctness = string.strip(job_correctness)

    #
    # Create an instance of the job status and add the correct result to the status file.
    #
    jstatus = status_file.rgt_status_file(test_id_string,mode="Old")
    jstatus.add_result(job_correctness,mode="Add_Run_Result")

    return


def usage():
    print "Usage: check_executable_driver.py [-h|--help] [-i <test_id_string>] [-p <path_to_results>]"
    print "A driver program that calls check_executable.x"
    print
    print "-h, --help            Prints usage information."                              
    print "-p <path_to_results>  The absoulte path to the results of a test."
    print "-i <test_id_string>   The test string unique id."



if __name__ == "__main__":
    main()
