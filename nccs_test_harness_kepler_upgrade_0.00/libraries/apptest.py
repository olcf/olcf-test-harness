#! /usr/bin/env python

"""
.. module:: apptest
   :synopsis: This module implements an abstraction of an application and subtest.

.. moduleauthor:: Arnold Tharrington
"""

import subprocess
import shlex
import time
import datetime
import os
import sys
import copy
import multiprocessing
from types import *
from libraries.base_apptest import base_apptest
from libraries.layout_of_apps_directory import apps_test_directory_layout
from libraries.status_file import parse_status_file
from libraries.status_file import parse_status_file2
from libraries.status_file import summarize_status_file
from bin.test_harness_driver import test_harness_driver

#
# Inherits "apps_test_directory_layout".
#
class  subtest(base_apptest,apps_test_directory_layout):
    #These strings define the tasks that the tests can do.
    checkout = "check_out_tests"
    starttest = "start_tests"
    stoptest = "stop_tests"
    displaystatus = "display_status"
    summarize_results = "summarize_results"
    status_file = "applications_status.txt"
    


    #
    # Constructor
    #
    def __init__(self,
                 name_of_application=None,
                 name_of_subtest=None,
                 local_path_to_tests=None,
                 number_of_iterations=-1):

        base_apptest.__init__(self,
                              name_of_application,
                              name_of_subtest,
                              local_path_to_tests)

        apps_test_directory_layout.__init__(self,
                                            name_of_application,
                                            name_of_subtest,
                                            local_path_to_tests)

        #Format of data is [<local_path_to_tests>, <application>, <test>] 
        self.__apps_test_checked_out = []

        self.__apps_test_checked_out = self.__apps_test_checked_out + [[self.getLocalPathToTests(),
                                                                        self.getNameOfApplication(),
                                                                        name_of_subtest]]
        self.__number_of_iterations = -1



    ##################
    # Public Methods #
    ##################
    def doTasks(self,tasks=None,
                     test_checkout_lock=None,
                     test_display_lock=None):
        """
        :param list_of_string my_tasks: A list of the strings 
                                        where each element is an application
                                        harness task to be preformed on this app/test
        """


        message = "In {app1}  {test1} doing {task1}".format(app1=self.getNameOfApplication(),
                                                                test1=self.getNameOfSubtest(),
                                                                task1=tasks)
        self.writeToLogTestFile(message)

        if tasks != None:
            tasks = copy.deepcopy(tasks)
            tasks = subtest.reorderTaskList(tasks)

        for harness_task in tasks:
            if harness_task == subtest.checkout:
                if test_checkout_lock:
                    test_checkout_lock.acquire()

                self.check_out_source()
                self.check_out_test()

                if test_checkout_lock:
                    test_checkout_lock.release()
            elif harness_task == subtest.starttest:
                self.start_test()

            elif harness_task == subtest.stoptest:
                self.stop_test()

            elif harness_task == subtest.displaystatus:
                if test_display_lock:
                    test_display_lock.acquire()

                self.display_status()

                if test_display_lock:
                    test_display_lock.release()

            elif harness_task == subtest.summarize_results:
                self.generateReport() 

    def getTestName(self):
        return self.getNameOfSubtest()
    
    def appTestName(self):
        return [self.getNameOfApplication(),self.getNameOfSubtest()]

    def check_out_source(self):
        message = "Checking out source of application: " + self.getNameOfApplication()
        self.writeToLogFile(message)

        #Get the current working directory.
        cwd = os.getcwd()
        
        #Get the relative path, with respect to cwd, to the 
        #application directory.
        relative_path_to_app_dir = self.get_local_path_to_tests_wd()

        #Get the url of the application with respect the the svn repo.
        svn_path_to_application = self.get_svn_path_to_application()

        #Get the name of the application
        application_name = self.getNameOfApplication()

        #Get the name of the subtest
        subtest_name = self.getNameOfSubtest() 

        #Form the absolute path to the application root directory.
        abspath_app_root_dir = os.path.join(cwd,relative_path_to_app_dir)

        #Form the absolute path to the application directory.
        abspath_app_dir = os.path.join(cwd,relative_path_to_app_dir,self.getNameOfApplication())

        #Form the absolute path to the Source directory.
        abspath_source_dir = os.path.join(cwd,relative_path_to_app_dir,self.getNameOfApplication(),"Source")


        exit_status = 0
        checkout_command = "svn checkout -N " + svn_path_to_application + " " + abspath_app_dir
        if os.path.exists(abspath_app_dir ):
            message = "Source of application: " + application_name + " already exists."
            self.writeToLogFile(message)
            exit_status = 0
        else:
            app_checkout_log_files = self.getPathToAppCheckoutLogFiles()
            stdout_path = app_checkout_log_files["stdout"]
            stderr_path = app_checkout_log_files["stderr"]
            with open(stdout_path,"a") as out:
                with open(stderr_path,"a") as err:
                    exit_status = subprocess.call(checkout_command,shell=True,stdout=out,stderr=err)
            
        if exit_status > 0:
            string1 = "Checkout of source command failed: " + checkout_command
            sys.exit(string1)

        message = "For the source update my current directory is " + abspath_app_dir 
        self.writeToLogTestFile(message)

        update_log_files = self.getPathToSourceUpdateLogFiles()
        stdout_path = update_log_files["stdout"]
        stderr_path = update_log_files["stderr"]

        message = "Source update command stdout path is {}".format(stdout_path)
        self.writeToLogTestFile(message)

        message = "Source update command stderr path is {}".format(stderr_path)
        self.writeToLogTestFile(message)

        update_command = "svn update " + abspath_source_dir
        with open(stdout_path,"a") as out:
            with open(stderr_path,"a") as err:
                subprocess.check_call(update_command,shell=True,stdout=out,stderr=err)

   
    #
    # Checks out the App and Test from the svn repository.
    #
    def check_out_test(self):
        message =  "Checking out test: " + self.getNameOfApplication() + " " + self.getNameOfSubtest()
        self.writeToLogTestFile(message)

        #Get the current working directory.
        cwd = os.getcwd()

        #Get the relative path, with respect to cwd, to the 
        #application directory.
        relative_path_to_app_dir = self.get_local_path_to_tests_wd()

        #Get the name of the subtest
        subtest_name = self.getNameOfSubtest() 

        #Form the absolute path to the application root directory.
        abspath_app_root_dir = os.path.join(cwd,relative_path_to_app_dir)

        #Form the absolute path to the application directory.
        abspath_app_dir = os.path.join(abspath_app_root_dir,self.getNameOfApplication())

        #Form the absolute path to the subtest directory.
        abspath_subtest_dir = os.path.join(abspath_app_dir,subtest_name)

        #Check out the application non-recursively.
        if os.path.exists(abspath_app_dir):
            message = "In " + self.getNameOfApplication() + " " + \
                      self.getNameOfSubtest() + ", the " + self.getNameOfApplication() + \
                      "  directory already exists."
            self.writeToLogTestFile(message)
        else:
            message =  "Error! Application directory {} does not exist.".format(self.getNameOfApplication())
            self.writeToLogTestFile(message)
            sys.exit(message)
        
        
        #Create the test by means of an update.
        update_log_files = self.getPathToTestCheckoutLogFiles()
        stdout_path = update_log_files["stdout"]
        stderr_path = update_log_files["stderr"]

        update_command = "svn update " + abspath_subtest_dir 
        with open(stdout_path,"a") as out:
            with open(stderr_path,"a") as err:
                exit_status = subprocess.call(args=update_command,shell=True,stdout=out,stderr=err)
                if exit_status > 0:
                    message = "Update command failed: " + update_command
                    self.writeToLogTestFile(message)

        if self.__number_of_iterations > 0:
            tmpdest2 = os.path.join(abspath_subtest_dir ,"Scripts",".testrc")
            file_obj = open(tmpdest2,"w")
            string1 = str(0) + "\n"
            string2 = str(self.__number_of_iterations) + "\n"
            file_obj.write(string1)
            file_obj.write(string2)
            file_obj.close() 

    #
    # Starts the regression test.
    #
    def start_test(self):
         
        #Get the current working directory.
        cwd = os.getcwd()

        pathtoscripts = self.get_local_path_to_scripts() 


        # If the file kill file exits then remove it.
        pathtokillfile = self.get_local_path_to_kill_file() 

        if os.path.lexists(pathtokillfile):
            os.remove(pathtokillfile)

        start_test_log_files = self.getPathToStartTestLogFiles()
        stdout_path = start_test_log_files["stdout"]
        stderr_path = start_test_log_files["stderr"]
        arguments = "-r"
        starttestcomand = "test_harness_driver('-r')"
        os.chdir(pathtoscripts) 
        with open(stdout_path,"a") as out:
            with open(stderr_path,"a") as err:
                arguments="-r"
                my_argv = shlex.split(arguments)
                exit_status = test_harness_driver(my_argv)
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
        log_message = "Testing status of: " + self.getNameOfApplication() + self.getNameOfSubtest()
        print(log_message)

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        (self.__status,failed_jobs) = parse_status_file2(path_to_status_file)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        appname = "%s, %s\n" % (self.getNameOfApplication(), self.getNameOfSubtest())
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
        log_message =  "Testing status of: " + self.getNameOfApplication() +self.getNameOfSubtest()
        print(log_message)

        starttimestring = taskwords[0]
        starttimestring = starttimestring.strip()
        starttimewords = starttimestring.split("_")
        startdate = datetime.datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        log_message =  "The startdate is " + startdate.ctime()
        print (log_message)

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime.datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
                                      int(endtimewords[3]),int(endtimewords[4]))
        log_message = "The enddate is " + enddate.ctime()
        print(log_message)

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        (self.__status,failed_jobs) = parse_status_file(path_to_status_file,startdate,enddate,mycomputer_with_events_record)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        appname = "%s, %s\n" % (self.getNameOfApplication(), self.getNameOfSubtest())
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


    def generateReport(self,logfile,taskwords):
        #Parse the status file.

        starttimestring = taskwords[0]
        starttimestring = starttimestring.strip()
        starttimewords = starttimestring.split("_")
        startdate = datetime.datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        log_message = "The startdate is " + startdate.ctime()
        print(log_message)

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime.datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
                                      int(endtimewords[3]),int(endtimewords[4]))
        log_message = "The enddate is " + enddate.ctime()
        print(log_message)

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

        appname = "{app:20s} {test:20s} ".format(app=self.getNameOfApplication(), test=self.getNameOfSubtest())
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
        print ("\n\n")
        print ("================================================================")
        print ("Debugging apptest ")
        print ("================================================================")
        for tmp_test in self.__apps_test_checked_out:
            print( "%-20s  %-20s %-20s" % (tmp_test[0],tmp_test[1], tmp_test[2]))
        print( "================================================================\n\n")

    @classmethod
    def reorderTaskList(cls,tasks):
        taskwords1 = []
        for taskwords in tasks:
            task = None
            if type(taskwords) == list:
                task = taskwords[0]
            else:
                task = taskwords
            taskwords1 = taskwords1 + [task]

        app_tasks1 = []

        if (cls.checkout in taskwords1) :
            app_tasks1.append(cls.checkout)
            taskwords1.remove(cls.checkout)

        if (cls.starttest in taskwords1) :
            app_tasks1.append(cls.starttest)
            taskwords1.remove(cls.starttest)

        if (cls.stoptest in taskwords1):
            app_tasks1.append(cls.stoptest)
            taskwords1.remove(cls.stoptest)

        if (cls.displaystatus in taskwords1):
            app_tasks1.append(cls.displaystatus)
            taskwords1.remove(cls.displaystatus)

        if (cls.summarize_results in taskwords1):
            app_tasks1.append(cls.summarize_results)
            taskwords1.remove(cls.summarize_results)
            
        return app_tasks1
        
