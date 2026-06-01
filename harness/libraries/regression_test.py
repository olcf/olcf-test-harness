#! /usr/bin/env python3

# Python imports

import collections
import concurrent.futures
import datetime
import getpass
import os
import time
import random # for shuffle

# Harness package imports.
from libraries import apptest
from libraries.subtest_factory import SubtestFactory
from libraries.rgt_state import RgtState
from libraries.rgt_loggers import rgt_logger_factory
from machine_types.machine_factory import MachineFactory

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

class Harness:

    # Defines the harness log file name.
    LOGGER_NAME = __name__

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self,
                 config,
                 rgt_input_file,
                 log_level,
                 stdout_stderr,
                 separate_build_stdio,
                 reuse_first_build,
                 reuse_build_from_id,
                 shuffle=False):
        self.__config = config
        self.__tests = rgt_input_file.get_tests()
        self.__tasks = rgt_input_file.get_harness_tasks()
        self.__local_path_to_tests = rgt_input_file.get_path_to_tests()
        self.__apptests_dict = collections.OrderedDict()
        self.__app_subtests = []
        self.__log_level = log_level
        self.__stdout_stderr = stdout_stderr
        self.__num_workers = 1
        self.__separate_build_stdio = separate_build_stdio
        self.__reuse_first_build = reuse_first_build
        self.__reuse_build_from_id = reuse_build_from_id
        self.__shuffle = shuffle
        self.__formAppTests()

        currenttime = time.localtime()
        time_stamp = time.strftime("%Y%m%d_%H%M%S", currenttime)
        self.__timestamp = time_stamp

        # Generate common launch id
        now_str = datetime.datetime.now().isoformat()
        if len(now_str) == 26: # now_str includes microseconds
            time_str = now_str[0:-4] # strip off last four characters
        else:
            time_str = now_str
        user_str = getpass.getuser()
        testshot_key = 'system_log_tag'
        testshot_str = 'notag'
        testshot_cfg = self.__config.get_testshot_config()
        if testshot_key in testshot_cfg.keys():
            testshot_str = testshot_cfg[testshot_key]
        self.__launch_id = f'{testshot_str}/{user_str}@{time_str}'
        self.__launched_tests = 0
        self.__failed_tests = 0
        self.__failed_test_list = []

        # Define a logger that streams to file.
        logger_name=Harness.LOGGER_NAME
        fh_filepath="./harness_log_files" + "." + self.__timestamp + "/" + Harness.LOGGER_NAME + "." + self.__timestamp + ".txt"
        logger_threshold = "DEBUG"
        # Log file always has a consistent log level. Console log level changes
        fh_threshold_log_level = "INFO" if not self.__log_level == "DEBUG" else "DEBUG"
        ch_threshold_log_level = self.__log_level
        self.__myLogger = rgt_logger_factory.create_rgt_logger(
                                     logger_name=logger_name,
                                     fh_filepath=fh_filepath,
                                     logger_threshold_log_level=logger_threshold,
                                     fh_threshold_log_level=fh_threshold_log_level,
                                     ch_threshold_log_level=ch_threshold_log_level)

    def __str__(self):
        message = ( "\n Local path to tests: " + self.__local_path_to_tests  + "\n"
                    "Tests: " + str(self.__tests) + "\n"
                    "Tasks: " + str(self.__tasks) + "\n")
        return message

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of special methods                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def run_me(self,
               my_effective_command_line=None,
               my_warning_messages=None):

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

        # Form a collection of applications with their subtests.
        self.__app_subtests = self.__formCollectionOfTests()

        # Run subtests
        self.__run_subtests_asynchronously()

        # If we get to this point mark all task as completed.
        self.__returnState = RgtState.ALL_TASKS_COMPLETED

        message = "End of harness."
        self.__myLogger.doInfoLogging(message)
        return

    def getState(self):
        return self.__returnState

    def wait_for_completion_in_queue(self,timeout):
        """Waits 'timeout' minutes for all jobs to be completed in the queue.

        Parameters
        ----------
        timeout : float
            The maximum time to wait in minutes for the subtest cycle to complete.
        """
        future_to_appname = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.__num_workers) as executor:
            for appname in self.__app_subtests.keys():
                future = executor.submit(apptest.wait_for_jobs_to_complete_in_queue,
                                         self.__config,
                                         self.__app_subtests[appname],
                                         timeout)

                future_to_appname[future] = appname

            for my_future in concurrent.futures.as_completed(future_to_appname):
                appname = future_to_appname[my_future]
                my_future_exception = my_future.exception()
                if my_future_exception:
                    message = "Application {} future for queue exception:\n{}".format(appname, my_future_exception)
                    self.__myLogger.doCriticalLogging(message)
                else:
                    message = "Application {} future for queue is completed.".format(appname)
                    self.__myLogger.doInfoLogging(message)
        return

    def didAllTestsPass(self):
        """Returns True if all tests have passed, otherwise False is returned.

        Returns
        -------
        bool
            A True return value means all tests have passed, otherwise a False value
            is returned.
        """
        ret_value = True
        for appname in self.__app_subtests.keys():
            for stests in self.__app_subtests[appname]:
                tmp_ret_value = stests.did_all_tests_pass(self.__config)
                ret_value = ret_value and tmp_ret_value

        return ret_value

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Private methods.                                                @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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

    def __doing_unit_testing(self):
        value = False
        if os.getenv('UNIT_TESTS_CWD'):
            value = True
            message = f"UNIT_TESTS_CWD: {value}"
            self.__myLogger.doInfoLogging(message)
        return value

    def __formCollectionOfTests(self):
        app_subtests = []
        for (appname, tests) in self.__apptests_dict.items():
            for testname in tests:
                logger_name = appname + "." + testname + "." + self.__timestamp
                fh_filepath = "harness_log_files" + "." + self.__timestamp + "/" + appname + "/" + appname + "__" + testname +  ".logfile.txt"
                logger_threshold = "DEBUG"
                # Log file always has a consistent log level. Console log level changes
                fh_threshold_log_level = "INFO" if not self.__log_level == "DEBUG" else "DEBUG"
                ch_threshold_log_level = self.__log_level
                a_logger = rgt_logger_factory.create_rgt_logger(logger_name=logger_name,
                                      fh_filepath=fh_filepath,
                                      logger_threshold_log_level=logger_threshold,
                                      fh_threshold_log_level=fh_threshold_log_level,
                                      ch_threshold_log_level=ch_threshold_log_level)

                subtest = SubtestFactory.make_subtest(name_of_application=appname,
                                                      name_of_subtest=testname,
                                                      local_path_to_tests=self.__local_path_to_tests,
                                                      logger = a_logger,
                                                      tag=self.__timestamp)

                app_subtests.append(subtest)
        if self.__shuffle:
            random.shuffle(app_subtests)
        return app_subtests

    def __run_subtests_asynchronously(self):
        future_to_appname = {}

        # Submit futures by means of thread pool.
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.__num_workers) as executor:
            for subtest in self.__app_subtests:
                # gracefully handle keyboard interrupts in main thread
                try:
                    future = executor.submit(apptest.do_application_tasks,
                                         self.__launch_id,
                                         subtest,
                                         self.__tasks,
                                         self.__stdout_stderr,
                                         self.__separate_build_stdio,
                                         self.__reuse_first_build,
                                         self.__reuse_build_from_id)
                    future_to_appname[future] = f'{subtest.getNameOfApplication()}.{subtest.getNameOfSubtest()}'
                except KeyboardInterrupt:
                    pass

            # Log when all job tasks are initiated.
            all_finished = False
            while not all_finished:
                # gracefully handle keyboard interrupts in main thread
                try:
                    for my_future in concurrent.futures.as_completed(future_to_appname):
                        # appname is appname.testname, as set above
                        appname = future_to_appname[my_future]

                        # Check if an exception has been raised
                        my_future_exception = my_future.exception()
                        if my_future_exception:
                            message = "Test {} exception encountered:\n{}".format(appname, my_future_exception)
                            self.__myLogger.doCriticalLogging(message)

                        subtest_result = my_future.result()
                        if subtest_result:
                            self.__launched_tests += 1
                            message = "Test {} is launched.\n\n".format(appname)
                            self.__myLogger.doErrorLogging(message)
                        else:
                            self.__failed_tests += 1
                            self.__failed_test_list.append(appname)
                            message = "Test {} failed to launch.\n\n".format(appname)
                            self.__myLogger.doErrorLogging(message)
                    all_finished = True
                except KeyboardInterrupt:
                    pass

            message = "All tests are launched. Yahoo!!"
            self.__myLogger.doInfoLogging(message)
            self.__myLogger.doCriticalLogging(f"Launched {self.__launched_tests} tests, failed to launch {self.__failed_tests} tests.")
            if self.__failed_tests:
                self.__myLogger.doErrorLogging("Failed tests:")
                for t in self.__failed_test_list:
                    self.__myLogger.doErrorLogging(f"\t{t}")

        return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods.                                         @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

