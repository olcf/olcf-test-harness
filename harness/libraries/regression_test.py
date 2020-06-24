#! /usr/bin/env python3

import time
import datetime
import collections
import queue
import concurrent.futures
import logging

from libraries import apptest
from fundamental_types.rgt_state import RgtState
from libraries.rgt_logging import rgt_logger

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

class Harness:

    # These strings define the tasks that the tests can do.
    checkout = "check_out_tests"
    starttest = "start_tests"
    stoptest = "stop_tests"
    displaystatus = "display_status"
    summarize_results = "summarize_results"

    # Defines the harness log file name.
    LOG_FILE_NAME = "harness_log_file"

    def __init__(self,
                 rgt_input_file,
                 log_level,
                 stdout_stderr):
        self.__tests = rgt_input_file.get_tests()
        self.__tasks = rgt_input_file.get_harness_tasks()
        self.__local_path_to_tests = rgt_input_file.get_path_to_tests()
        self.__apptests_dict = collections.OrderedDict()
        self.__log_level = log_level
        self.__myLogger = None
        self.__stdout_stderr = stdout_stderr
        self.__num_workers = 1

        self.__formAppTests()


    def run_me(self,
               my_effective_command_line=None,
               my_warning_messages=None):

        # Define a logger that streams to file.
        currenttime = time.localtime()
        time_stamp = time.strftime("%Y%m%d_%H%M%S",currenttime)
        self.__myLogger = rgt_logger(Harness.LOG_FILE_NAME,
                                     self.__log_level,
                                     time_stamp)

        # Log the start of the harness.
        message = "Start of harness."
        self.__myLogger.doInfoLogging(message)

        # Log the effective command line"
        if my_effective_command_line:
            self.__myLogger.doInfoLogging(my_effective_command_line)

        # Log the command line warning messages
        if my_warning_messages:
            self.__myLogger.doInfoLogging(my_warning_messages)

        # Mark status as tasks not completed.
        self.__returnState = RgtState.ALL_TASKS_NOT_COMPLETED

        app_subtests = collections.OrderedDict()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.__num_workers) as executor:
            for (appname, tests) in self.__apptests_dict.items():
                if appname not in app_subtests:
                    app_subtests[appname] = []
                for testname in tests:
                    subtest = apptest.subtest(name_of_application=appname,
                                              name_of_subtest=testname,
                                              local_path_to_tests=self.__local_path_to_tests,
                                              application_log_level=self.__log_level,
                                              timestamp=time_stamp)
                    app_subtests[appname].append(subtest)

            future_to_appname = {}
            for appname in app_subtests.keys():
                future = executor.submit(apptest.do_application_tasks,
                                         app_subtests[appname],
                                         self.__tasks,
                                         self.__stdout_stderr)
                future_to_appname[future] = appname

                # Log that the application has been submitted for tasks.
                message = "Application " + appname + " has been submitted for running tasks."
                self.__myLogger.doInfoLogging(message)

            for my_future in concurrent.futures.as_completed(future_to_appname):
                appname = future_to_appname[my_future]

                # Check if an exception has been raised
                my_future_exception = my_future.exception()
                if my_future_exception:
                    message = "Application {} future exception:\n{}".format(appname, my_future_exception)
                    self.__myLogger.doInfoLogging(message)
                else:
                    message = "Application {} future is completed.".format(appname)
                    self.__myLogger.doInfoLogging(message)

            message = "All applications completed. Yahoo!!"
            self.__myLogger.doInfoLogging(message)

        # If we get to this point mark all task as completed.
        self.__returnState = RgtState.ALL_TASKS_COMPLETED

        message = "End of harness."
        self.__myLogger.doInfoLogging(message)
        return

    def getState(self):
        return self.__returnState

    # Private member functions
    def __formAppTests(self):
        """ Sets up __apptests_dict. Keys are application name, values are list of test names. """
        application_names = set()
        for test in self.__tests:
            appname = test[0]
            testname = test[1]
            if appname not in application_names:
                application_names.add(appname)
                self.__apptests_dict[appname] = []
            self.__apptests_dict[appname].append(testname)
