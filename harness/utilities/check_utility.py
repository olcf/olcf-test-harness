#!/usr/bin/env python3
import glob
import os
import sys
import getopt

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#


def main():

    #
    # Get the command line arguments.
    #
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hp:")

    except getopt.GetoptError:
            usage()
            sys.exit(2)

    #
    # Parse the command line arguments.
    #
    for o, a in opts:
        if o == "-p":
            unix_regexp = a
        elif o == ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()

    #-----------------------------------------------------
    # Make a list of all the test directories.           -
    #                                                    -
    #-----------------------------------------------------
    tests = glob.glob(unix_regexp)

    #-----------------------------------------------------
    # For each test run the checks of all runs.          -
    #                                                    -
    #-----------------------------------------------------
    
    for test1 in tests:
        rerun_checks(test1)
def get_list_of_run_dirs(test1):
    #Open the status file and read.
    path_to_status_file = os.path.join(test1,"Status","rgt_status.txt")
    fileobj = open(path_to_status_file)
    lines = fileobj.readlines()
    fileobj.close()

    #Get the number of lines in the status file.
    nlines = len(lines)

    #Get the names of the rundirs.
    rundirs = []
    for ip in range(nlines-5):
        jp = ip + 5
        tmpline = lines[jp]
        words = tmpline.split() 
        rundirs = rundirs + [words[1]]
        
    return rundirs

def rerun_checks(test1):
    startdir = os.getcwd()
    print "==========================="
    print "Staring directory is ", startdir
    print "Rerunning checks in ", test1
    print "==========================="

    #-----------------------------------------------------
    # Make a list of all the run directories in          -
    # Run_Archive                                        -
    #                                                    -
    #-----------------------------------------------------
    rundirs = get_list_of_run_dirs(test1)
    path1 = os.path.join(test1,"Run_Archive")

    #-----------------------------------------------------
    # For each run directory generate the unique id and  -
    # the absolute path to run the directory.            -
    #                                                    -
    #-----------------------------------------------------
    testdict = {}
    for rundir1 in rundirs:
        #--Get path to the run directory and change to the
        #--run directory.
        path2 = os.path.join(path1,rundir1)
        os.chdir(path2)

        #--Here we get the absolute path
        lid = os.getcwd()

        #--Here we get the unique id.
        pid = rundir1

        #--Store in a dictionary.
        testdict[pid] = lid

        #--Change back to the starting directory.
        os.chdir(startdir)


    #-----------------------------------------------------
    # Check each test.                                   -
    #                                                    -
    #-----------------------------------------------------
    #--Get the path to the Scripts directory and change
    #--to the scripts directory.
    path3 = os.path.join(test1,"Scripts")
    os.chdir(path3)

    #--Get a list of the completed runs.
    crdict = get_dict_of_completed_runs()

    #--For each run, stored in testdict, rerun the test
    #--only if run has completed.
    for lid,pid in testdict.iteritems():
        if has_run_completed(lid,crdict):
            #--Rerun the check command.
            check_command = "check_executable_driver.py -i " + lid + " -p " + pid
            print check_command
            os.system(check_command)

    #--Print a summary of the results.
    printsummary(test1)

    #--Change back the the starting directory.
    os.chdir(startdir)

    print "==========================="
    print "===========================\n\n"

def printsummary(test1):

    #--Define empty dictionaries.
    passed_array = []
    failed_array = []
    nc_array = []

    #--Initialize counters.
    nm_total = 0
    nm_passed = 0
    nm_failed = 0
    nm_notcmp = 0

    #--Get path to rgt_status.txt file.
    path1 = "../Status/rgt_status.txt"

    #--Read the records of the rgt_status.txt file
    fileobj = open(path1,'r')
    filerecords = fileobj.readlines()
    fileobj.close()

    #--The 6th record is where we start reading.
    #--We only want the 2-6 fields. Don't forget
    #--we offset by -1 because python  lists start with
    #--index 0.
    for record in filerecords[5:]:
        #--Remove the trailing newlines and beginning whitespace.
        tmprecord = record.strip()
        words = tmprecord.split()
        uid = words[1]

        #--Increment the counters as appropiate.
        nm_total = nm_total + 1
        if words[-1] == "***": #Not completed
             nm_notcmp = nm_notcmp + 1
             nc_array = nc_array + [uid]  
        elif words[-1] == "0" :
             nm_passed = nm_passed + 1
             passed_array = passed_array + [uid]  
        else: 
            nm_failed = nm_failed + 1
            failed_array = failed_array + [uid]  

    sfileobj = open("../../summary.txt",'a')
    tmpstring = "Test: " + test1 + "\n"
    sfileobj.write(tmpstring)

    tmpstring = "=====================\n"
    sfileobj.write(tmpstring)

    tmpstring = "Total number         = " + str(nm_total) + "\n"
    sfileobj.write(tmpstring)

    tmpstring = "Number passed        = " + str(nm_passed) + "\n"
    sfileobj.write(tmpstring)

    tmpstring = "Number failed        = " + str(nm_failed) + "\n"
    sfileobj.write(tmpstring)

    tmpstring = "Number not completed = " + str(nm_notcmp) + "\n\n"
    sfileobj.write(tmpstring)

   
    tmpstring = "List of failed:\n" 
    sfileobj.write(tmpstring)
    for ip in failed_array:
        tmpstring = ip + "\n"
        sfileobj.write(tmpstring)
    
    tmpstring = "\n"
    sfileobj.write(tmpstring)

    tmpstring = "List of incompleted:\n" 
    sfileobj.write(tmpstring)
    for ip in nc_array:
        tmpstring = ip + "\n"
        sfileobj.write(tmpstring)
    
    tmpstring = "\n\n\n"
    sfileobj.write(tmpstring)


    sfileobj.close()

def get_dict_of_completed_runs():

    #--Define an empty dictionary.
    cr_dict = {}

    #--Get path to rgt_status.txt file.
    path1 = "../Status/rgt_status.txt"

    #--Read the records of the rgt_status.txt file
    fileobj = open(path1,'r')
    filerecords = fileobj.readlines()
    fileobj.close()

    #--The 6th record is where we start reading.
    #--We only want the 2-6 fields. Don't forget
    #--we offset by -1 because python  lists start with
    #--index 0.
    for record in filerecords[5:]:
        #--Remove the trailing newlines and beginning whitespace.
        tmprecord = record.strip()
        words = tmprecord.split()

        #--If last word equals "***" the test has not completed. Skip to next run of test.
        #--Else add run to list of valid tests.
        if words[-1] == "***": #Not completed
            pass
        else:                  #Completed
            uid = words[1]
            cr_dict[uid] = tmprecord
            
    return cr_dict

def has_run_completed(lid,crdict):
    boolval = False
    if crdict.has_key(lid):
        boolval = True
    else:
        boolval = False

    return boolval


def usage():
    print "Usage: check_utility [-h|--help] [-p 'Unix regular expression']"
    print ""
    print "-h, --help            Prints usage information."                              
    print "-p                    A unix regular expression."

main()
