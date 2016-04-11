#! /usr/bin/env python

import shutil
import time
import datetime
import os
import sys
from libraries.layout_of_apps_directory import apps_test_directory_layout
from libraries.status_file import rgt_status_file
from libraries.status_file import parse_status_file
from libraries.status_file import parse_status_file2
from libraries.status_file import summarize_status_file

#
# Inherits "apps_test_directory_layout".
#
class  subtest(apps_test_directory_layout):
    #Format of data is [<local_path_to_tests>, <application>, <test>] 
    apps_test_checked_out = []

    #
    # Constructor
    #
    def __init__(self,name_of_application=None, name_of_subtest=None, local_path_to_tests=None,number_of_iterations=-1):

        apps_test_directory_layout.__init__(self,name_of_application,name_of_subtest,local_path_to_tests)

        subtest.apps_test_checked_out = subtest.apps_test_checked_out + [[local_path_to_tests,name_of_application,name_of_subtest]]
        self.__name_of_application = name_of_application
        self.__name_of_subtest = name_of_subtest
        self.__local_path_to_tests = local_path_to_tests
        self.__number_of_iterations = number_of_iterations
        self.__number_of_tests = 0
        self.__number_of_tests_finished = 0
        self.__number_of_tests_not_finished = 0
        self.__number_of_passed_tests = 0
        self.__number_of_failed_tests = 0
        self.__number_of_inconclusive_tests = 0
       
     
        #Debug lines.
        #self.debug_layout()
        #self.debug_apptest()


    def name(self):
        return [self.__name_of_application,self.__name_of_subtest]

    #
    # Checks out the Appp and Test from the svn repository.
    #
    def check_out_test(self):
        print "Checking out test: ", self.__name_of_application, " ", self.__name_of_subtest

        #Get the current working directory.
        cwd = os.getcwd()

        #Set the destination of the app/test.
        dest = self.get_local_path_to_tests_wd()
        tmpdest = os.path.join(dest,self.__name_of_application)

        #Check out the application non-recursively.
        pathtoapplication = self.get_svn_path_to_application()

        exit_status = 0
        if os.path.exists(tmpdest):
            print tmpdest, " already exists."
            exit_status =  0
        else:
            checkout_command = "svn checkout -N " + pathtoapplication + " " + tmpdest
            print "svn command: ", checkout_command
            exit_status = os.system(checkout_command)

        if exit_status > 0:
            string1 = "Checkout command failed: " + checkout_command
            sys.exit(string1)

        #Create the Source directory by means of an update.
        os.chdir(tmpdest)
        dest = self.get_local_path_to_tests_wd()
        update_command = "svn update Source"
        exit_status = os.system(update_command)

        if exit_status > 0:
            string1 = "update command failed: " + update_command
            sys.exit(string1)

        
        #Create the test by means of an update.
        update_command = "svn update " + self.__name_of_subtest
        exit_status = os.system(update_command)
        if exit_status > 0:
            string1 = "update command failed: " + update_command
            sys.exit(string1)

        if self.__number_of_iterations > 0:
            tmpdest2 = os.path.join(tmpdest,self.__name_of_subtest,"Scripts",".testrc")
            file_obj = open(tmpdest2,"w")
            string1 = str(0) + "\n"
            string2 = str(self.__number_of_iterations) + "\n"
            file_obj.write(string1)
            file_obj.write(string2)
            file_obj.close() 
   
        #Change back to the starting directory.
        os.chdir(cwd)
         
    #
    # Starts the regression test.
    #
    def start_test(self):
         
        #Get the current working directory.
        cwd = os.getcwd()

        pathtoscripts = self.get_local_path_to_scripts() 

        os.chdir(pathtoscripts)

        # If the file kill file exits then remove it.
        pathtokillfile = self.get_local_path_to_kill_file() 

        if os.path.lexists(pathtokillfile):
           os.remove(pathtokillfile)

        starttestcomand = "test_harness_driver.py -r"

        exit_status = os.system(starttestcomand)
        if exit_status > 0:
            string1 = "Command failed: " + starttestcomand
            sys.exit(string1)

        os.chdir(cwd)


    #
    # Stops the test.
    #
    def stop_test(self):
         
        pathtokillfile = self.get_local_path_to_kill_file() 

        kill_file = open(pathtokillfile,"w")
        kill_file.write("")
        kill_file.close()


    #
    # Displays the status of the tests.
    #
    def display_status(self):
        failed_jobs = []
        print "Testing status of: ",self.__name_of_application, self.__name_of_subtest

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        (self.__status,failed_jobs) = parse_status_file2(path_to_status_file)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        appname = "%s, %s\n" % (self.__name_of_application, self.__name_of_subtest)
        w1 = "Warning: No tests passed!!\n"
        s1 = "%20s %20s %20s %20s\n" % ("Total tests","Test passed", "Test failed", "Test inconclusive")
        s2 = "%20s %20s %20s %20s\n" % (str(self.__status["number_of_tests"]),
                                        str(self.__status["number_of_passed_tests"]),
                                        str(self.__status["number_of_failed_tests"]),
                                        str(self.__status["number_of_inconclusive_tests"])
                                       )
        bheader = "\n====================\n"


        dfile_obj = open("test_status.txt","a")
        dfile_obj.write(theader)
        dfile_obj.write(time1)
        dfile_obj.write(appname)
        dfile_obj.write(s1)
        dfile_obj.write(s2)
        dfile_obj.write(bheader)
        dfile_obj.close()

        efile_obj = open("failed_jobs.txt","a")
        efile_obj.write(theader)
        efile_obj.write(time1)
        efile_obj.write(appname)
        for job in failed_jobs:
            s3 = "%20s %20s %20s\n" % (job[0],job[1],job[2])
            efile_obj.write(s3)
        efile_obj.write(bheader)
        efile_obj.close()

    #
    # Displays the status of the tests.
    #
    def display_status2(self,taskwords,mycomputer_with_events_record):
        failed_jobs = []
        print "Testing status of: ",self.__name_of_application, self.__name_of_subtest

        starttimestring = taskwords[0]
        starttimestring = starttimestring.strip()
        starttimewords = starttimestring.split("_")
        startdate = datetime.datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        print "The startdate is ", startdate.ctime()

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime.datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
                                      int(endtimewords[3]),int(endtimewords[4]))
        print "The enddate is ", enddate.ctime()

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        (self.__status,failed_jobs) = parse_status_file(path_to_status_file,startdate,enddate,mycomputer_with_events_record)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        appname = "%s, %s\n" % (self.__name_of_application, self.__name_of_subtest)
        w1 = "Warning: No tests passed!!\n"
        s1 = "%20s %20s %20s %20s\n" % ("Total tests","Test passed", "Test failed", "Test inconclusive")
        s2 = "%20s %20s %20s %20s\n" % (str(self.__status["number_of_tests"]),
                                        str(self.__status["number_of_passed_tests"]),
                                        str(self.__status["number_of_failed_tests"]),
                                        str(self.__status["number_of_inconclusive_tests"])
                                       )
        bheader = "\n====================\n"


        dfile_obj = open("test_status.txt","a")
        dfile_obj.write(theader)
        dfile_obj.write(time1)
        dfile_obj.write(appname)
        dfile_obj.write(s1)
        dfile_obj.write(s2)
        dfile_obj.write(bheader)
        dfile_obj.close()

        efile_obj = open("failed_jobs.txt","a")
        efile_obj.write(theader)
        efile_obj.write(time1)
        efile_obj.write(appname)
        for job in failed_jobs:
            s3 = "%20s %20s %20s\n" % (job[0],job[1],job[2])
            efile_obj.write(s3)
        efile_obj.write(bheader)
        efile_obj.close()


    def generateReport(self,logfile,taskwords,mycomputer_with_events_record):
        #Parse the status file.

        starttimestring = taskwords[0]
        starttimestring = starttimestring.strip()
        starttimewords = starttimestring.split("_")
        startdate = datetime.datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        print "The startdate is ", startdate.ctime()

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime.datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
                                      int(endtimewords[3]),int(endtimewords[4]))
        print "The enddate is ", enddate.ctime()

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        self.__summary = summarize_status_file(path_to_status_file,startdate,enddate,mycomputer_with_events_record)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        fieldheader = "{leading_space:41s} {attempts:10s} {passes:10s} {fails:10s} {inconclusive:10s}\n".format(leading_space="", 
                                                                                attempts="Attemps", 
                                                                                passes="Passed",
                                                                                fails="Failures",
                                                                                inconclusive="Inconclusive")

        appname = "{app:20s} {test:20s} ".format(app=self.__name_of_application, test=self.__name_of_subtest)
        results = "{attempts:10s} {passes:10s} {failures:10s} {inconclusive:10s}".format(
                                          attempts=str(self.__summary["number_of_tests"]),
                                          passes=str(self.__summary["number_of_passed_tests"]),
                                          failures=str(self.__summary["number_of_failed_tests"]),
                                          inconclusive=str(self.__summary["number_of_inconclusive_tests"]),
)

        bheader = "\n====================\n"


        dfile_obj = open(logfile,"a")
        dfile_obj.write(theader)
        dfile_obj.write(fieldheader)
        dfile_obj.write(appname)
        dfile_obj.write(results)
        dfile_obj.write(bheader)
        dfile_obj.close()

        flag_test_has_passes = False
        if self.__summary["number_of_failed_tests"] >= 0:
            flag_test_has_passes = True

        return {"Test_has_at_least_1_pass" : flag_test_has_passes,
                "Number_attemps" : self.__summary["number_of_tests"],
                "Number_passed" : self.__summary["number_of_passed_tests"],
                "Number_failed" : self.__summary["number_of_failed_tests"],
                "Number_inconclusive" : self.__summary["number_of_inconclusive_tests"],
                "Failed_jobs" : self.__summary["failed_jobs"],
                "Inconclusive_jobs" : self.__summary["inconclusive_jobs"]}
            
        
    #
    # Debug apptest.
    #
    def debug_apptest(self):
         print "\n\n"
         print "================================================================"
         print "Debugging apptest "
         print "================================================================"
         for tmp_test in subtest.apps_test_checked_out:
             print "%-20s  %-20s %-20s" % (tmp_test[0],tmp_test[1], tmp_test[2])
         print "================================================================\n\n"

        
