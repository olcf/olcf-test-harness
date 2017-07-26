#! /usr/bin/env python3

import time
import datetime
import collections
import queue
import concurrent.futures
import logging
from types import *

from libraries import apptest
from fundamental_types.rgt_state import RgtState
from libraries import application_test_dictionary

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

class Harness:

    #These strings define the tasks that the tests can do.
    checkout = "check_out_tests"
    starttest = "start_tests"
    stoptest = "stop_tests"
    displaystatus = "display_status"
    summarize_results = "summarize_results"
    status_file = "applications_status.txt"

    # Defines the harness log file name.
    LOG_FILE_NAME = "harness_log_file.txt"
    
    def __init__(self,
                 rgt_input_file,
                 concurrency):
        self.__tests = rgt_input_file.get_tests()
        self.__tasks = rgt_input_file.get_harness_tasks()
        self.__local_path_to_tests = rgt_input_file.get_local_path_to_tests()
        self.__appsubtest = []
        self.__concurrency = concurrency
        mycomputer_with_events_record = None

    def run_me_serial(self,
                      log_level=None):
        
        numeric_level = getattr(logging, log_level.upper(), None)
        list_of_applications = []
        list_of_applications_names = []
        future_to_application_name = {}
        app_test_dict = {}
        
        # Mark status as tasks not completed.
        self.__returnState = RgtState.ALL_TASKS_NOT_COMPLETED

        my_tests = self.__formListOfTests()

        for application_test in my_tests:
            list_of_applications.append(application_test)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as application_executor:
            app_future = {}
            for ip in range(len(list_of_applications)):
                app_test = list_of_applications[ip]
                my_app_name = app_test.ApplicationName
                my_tests = app_test.Tests

                list_of_applications_names.append(my_app_name)
                app_test_dict[my_app_name] = []
                for test in my_tests:
                    my_application_name = test[0]
                    my_subtest_name = test[1]

                    app_test_dict[my_application_name].append(apptest.subtest(name_of_application=my_application_name,
                                                              name_of_subtest=my_subtest_name,
                                                              local_path_to_tests=self.__local_path_to_tests,
                                                              application_log_level=log_level))

            # for my_application_name in list_of_applications_names:
            #     future_to_application_name[my_application_name] = application_executor.submit(apptest.do_application_tasks,my_application_name,app_test_dict[my_application_name],self.__tasks)
            # The line below is the same as the immediate 2 lines above.
            future_to_application_name = {application_executor.submit(apptest.do_application_tasks,app_name,app_test_dict[app_name],self.__tasks) : app_name for app_name in list_of_applications_names}
           
            for my_future in concurrent.futures.as_completed(future_to_application_name):
                name = future_to_application_name[my_future]
                message = "Application {} future is completed".format(name)
                print(message)

                # Check the result of the future.
                # my_future_result = my_future.result()
                # if my_future_result:
                #     message = "Application {} future result:\n{}\n".format(name,my_future_result)
                #     # print(message)

                # Check if an exception has been raised
                my_future_exception = my_future.exception()
                if my_future_exception:
                    message = "Application {} future exception:\n{}\n".format(name,my_future_exception)
                    print(message)

            message = "All applications completed. Yahoo!!"
            print(message)


        # If we get to this point mark all task as completed.
        self.__returnState = RgtState.ALL_TASKS_COMPLETED

        # This code will be neeeded later
        return

    def run_me_concurrent(self,
                          log_level=None):
        # Form a queue of the apps.
        
    
        return

    def getState(self):
        return self.__returnState

    # Private member functions
    def __formListOfTests(self):
        """ Returns a list with each element being of type 
            application_test_dictionary.ApplicationSubtestDictionary.
        """
        # Form a set of application names.
        my_set_of_application_names = set([])
        for test in self.__tests:
            name_of_application=test[0]
            if name_of_application not in my_set_of_application_names:
                my_set_of_application_names.add(name_of_application) 

        # Form a list of tests without the subtests, and keep
        # the sequence of the the application in a dictionary.
        ip = -1
        my_tests = []
        application_sequence_index = {}
        for application_name in my_set_of_application_names:
            ip += 1
            application_sequence_index[application_name] = ip
            my_tests.append(application_test_dictionary.ApplicationSubtestDictionary(application_name))

        # We now add the subtests for each appication.
        for test in self.__tests:
            name_of_application=test[0]
            name_of_subtest=test[1]
            index = application_sequence_index[name_of_application] 
            my_tests[index].addAppSubtest(name_of_application,
                                          name_of_subtest)
        return my_tests
    
    def __check_out_test(self,apptest1):
        # Check out the files.
        apptest1.check_out_test()

    def __start_test(self,apptest1):
        #Start the test.
        apptest1.start_test()

    def __stop_test(self,apptest1):
        #Stop the test.
        apptest1.stop_test()

    def __display_status(self,apptest1,taskwords,mycomputer_with_events_record):
        #Display the test status.
        print("In display_status")
        if mycomputer_with_events_record == None:
            apptest1.display_status()
        else:
            apptest1.display_status2(taskwords,mycomputer_with_events_record)

    def __summarize_results(self,taskwords,mycomputer_with_events_record):
        failed_list = []
        inconclusive_list = []
        results = {"Test_has_at_least_1_pass" : 0,
                   "Number_attemps" : 0,
                   "Number_passed" : 0,
                   "Number_failed" : 0,
                   "Number_inconclusive" : 0,
                   "Failed_jobs" : [] ,
                   "Inconclusive_jobs" : []}

        #-----------------------------------------------------
        #                                                    -
        #                                                    -
        #-----------------------------------------------------
        tests_with_no_passes = []

        #-----------------------------------------------------
        # Generate a time stamp of the current time.         -
        #                                                    -
        #-----------------------------------------------------
        currenttime = time.localtime()
        timestamp = time.strftime("%Y%b%d_%H:%M:%S",currenttime)

        #-----------------------------------------------------
        # Generate the name of the logfile.                  -
        #                                                    -
        #-----------------------------------------------------
        logfile = Harness.status_file + "__" + str(timestamp)
        for appsubtest1 in self.__appsubtest:
            app_status = appsubtest1.generateReport(logfile,taskwords,mycomputer_with_events_record)

            if app_status["Number_passed"] == 0:
                tests_with_no_passes = tests_with_no_passes + [appsubtest1.name()]

            if app_status["Number_failed"] > 0:
                for tmpjob in app_status["Failed_jobs"]:
                    log_message = "Failed job: " + tmpjob
                    print(log_message)

            if app_status["Number_inconclusive"] > 0:
                for tmpjob in app_status["Inconclusive_jobs"]:
                    log_message = "Inconclusive job: " + tmpjob
                    print(log_message)


            for key in app_status.keys():
                results[key] = results[key] + app_status[key]

        dfile_obj = open(logfile,"a")
        dfile_obj.write("\n\n\nTest with 0 passes\n")
        dfile_obj.write("==================\n")
        for [application,subtest] in tests_with_no_passes:
            appname = "{app:20s} {test:20s}\n".format(app=application,test=subtest)
            dfile_obj.write(appname)

        dfile_obj.write("\n\n\nSummary\n")
        dfile_obj.write("==================\n")
        tmp_string = "Number of attempts = {attemps:10s}\n".format(attemps=str(results["Number_attemps"]))
        dfile_obj.write(tmp_string)
        tmp_string = "Number of passes = {passes:10s}\n".format(passes=str(results["Number_passed"]))
        dfile_obj.write(tmp_string)
        tmp_string = "Number of fails = {fails:10s}\n".format(fails=str(results["Number_failed"]))
        dfile_obj.write(tmp_string)
        tmp_string = "Number inconclusive = {inconclusive:10s}\n".format(inconclusive=str(results["Number_inconclusive"]))
        dfile_obj.write(tmp_string)

        dfile_obj.close()
