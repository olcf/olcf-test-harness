#! /usr/bin/env python

import sys
import os
import getopt
import filecmp
import re



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
    # Get path to the correct results.
    #
    path_to_correct_results = get_path_to_correct_results()

    #
    # Compare the results.
    #
    jstatus = check_results(path_to_results)

    #
    # Write the statis of the results to job data file.
    #
    write_to_job_data(path_to_results,jstatus)
    
def get_path_to_correct_results():
    cwd = os.getcwd()

    #
    # Get the head path in the cwd.
    #
    (dir_head1, dir_tail1) = os.path.split(cwd)

    #
    # This is the path to the correct results.
    #
    crslts = os.path.join(dir_head1,"Correct_Results")
    
    return crslts



def check_results(path_to_results):
    #-----------------------------------------------------
    #Define good and bad results.
    #                                                    -
    #-----------------------------------------------------
    GOOD_RESULTS=1
    BAD_RESULTS=0

    re_exp = re.compile("^Success$")

    #
    # Make the file name paths to numbers squared.
    #
    file1 = os.path.join(path_to_results,"std.out.txt")
    file_obj = open(file1,"r")
    tlines = file_obj.readlines()
    file_obj.close()

    ip = 0
    for record1 in tlines:
        if re_exp.match(record1):
            ip = ip+1;

    if ip == 16:
        ival = GOOD_RESULTS
    else:
        ival = BAD_RESULTS
 
    return ival

def write_to_job_data(path_to_results,jstatus):

    (dir_head1, dir_tail1) = os.path.split(path_to_results)
    (dir_head2, dir_tail2) = os.path.split(dir_head1)

    file1 = os.path.join(dir_head2,"Status",dir_tail1,"job_status.txt")
    file1_obj = open(file1,"w")

    # Set the string to write to the job_status.txt file.
    if jstatus == 0:
        pf = "1"
    elif jstatus == 1:
        pf = "0"
    elif jstatus >= 2:
        pf = "2"
    string1 = "%s\n" % (pf)

    file1_obj.write(string1)
    file1_obj.close()



def usage():
    print("Usage: check_executable.x [-h|--help] [-i <test_id_string>] [-p <path_to_results>]")
    print("A program that checks the results located at <path_to_results>")
    print("The check executable must write the status of the results to the file")
    print("Status/<test_id_string>/job_status.txt'.")
    print("")
    print("-h, --help            Prints usage information.")                              
    print("-p <path_to_results>  The absoulte path to the results of a test.")
    print("-i <test_id_string>   The test string unique id.")



if __name__ == "__main__":
    main()
