#! /usr/bin/env python3

# Python package imports
import string
import os
import configparser
import re

# My harness package imports
from runtests import USE_HARNESS_TASKS_IN_RGT_INPUT_FILE
from runtests import get_main_logger
from libraries import rgt_utilities
from libraries.harness_internal_config import harness_modes
from libraries.rgt_loggers import rgt_logger_factory

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

class rgt_input_file:

    #These are the entries in the input file.
    test_entry = "test"
    include_entry = "include"
    path_to_test_entry = "path_to_tests"
    comment_line_entry = "#"
    harness_task_entry = "harness_task"

    def __init__(self,
                 inputfilename="rgt.input",
                 runmodecmd=None,
                 app_filter=None,
                 test_filter=None,
                 logger=None):
        self.__tests = []
        self.__harness_task = []
        self.__path_to_tests = os.environ["RGT_PATH_TO_TESTS"] if "RGT_PATH_TO_TESTS" in os.environ else ""
        self.__inputFileName = inputfilename
        self.__logger = logger

        if not logger:
            self.__logger = rgt_logger_factory.create_rgt_logger(
                                logger_name='rgt_input_file_logger',
                                fh_filepath=None,
                                logger_threshold_log_level='DEBUG',
                                fh_threshold_log_level='DEBUG',
                                ch_threshold_log_level='DEBUG')
            self.__logger.doInfoLogging("Created a logger in rgt_input_file, since one was not provided.")

        # Read the input file. Returns True upon successful read.
        # If read_file fails, self.__tests is emptied and False is returned
        err = self.__read_file(self.__inputFileName, app_filter=app_filter, test_filter=test_filter)
        if not err:
            self.__logger.doCriticalLogging("ERROR: Failed to parse input file.")
            # Short-circuit upon failure
            return

        if not self.__path_to_tests:
            self.__logger.doCriticalLogging("ERROR: Path_to_tests was not set by RGT_PATH_TO_TESTS or Path_to_tests in the input file.")
            # Short-circuit upon failure
            return

        # If a CLI task was input use that instead
        if not USE_HARNESS_TASKS_IN_RGT_INPUT_FILE in runmodecmd :
            self.__logger.doInfoLogging("Discarding tasks in inputfile since CLI mode was provided")
            self.__logger.doDebugLogging(f"runmodecmd = {runmodecmd}")
            unsorted_harness_task = []
            for modetask in runmodecmd:
                if modetask == "checkout":
                    runmodetask = harness_modes.checkout
                elif modetask == "start":
                    runmodetask = harness_modes.starttest
                elif modetask == "stop":
                    runmodetask = harness_modes.stoptest
                elif modetask == "status":
                    runmodetask = harness_modes.displaystatus
                else:
                    runmodetask = None
                    self.__logger.doErrorLogging(f"Found invalid task in the command line: {modetask}")

                # Append task to this harness instance
                if runmodetask != None:
                    self.__harness_task.append(runmodetask)

                # Clear mode to avoid duplicate
                runmodetask = None

        sorted_tasks = harness_modes.reorderTaskList(self.__harness_task)
        self.__harness_task = sorted_tasks

        if self.__harness_task == []:
            self.__logger.doCriticalLogging("ERROR: No valid tasks found in the inputfile or the CLI")

    def __read_file(self, input_file, app_filter=None, test_filter=None):
        ifile_obj = open(input_file,"r")
        lines = ifile_obj.readlines()
        ifile_obj.close()

        for tmpline in lines:

            #If this is a comment line, then continue to next line.
            if self.__is_comment_line(tmpline):
                continue

            words = str.split(tmpline)

            #If there are no words, then continue to next line.
            if len(words) == 0:
                continue

            #Convert the first word to lower case.
            firstword = str.lower(words[0])

            # Parse the line,depending upon what type of entry it is.
            if firstword == rgt_input_file.test_entry:
                # Check that there are at either 4 or 5 items in the line
                if not (len(words) == 4 or len(words) == 5):
                    log_message = "Invalid number of words in test line: " + tmpline
                    self.__logger.doCriticalLogging(log_message)
                    # Clear all tests -- invalid line in input file
                    self.__tests = []
                    return False
                # Determine the number of words. If the number of words is 4
                # The we run an indefinite number of times. If the number
                # of words is 5, the we run a definite number of times dictated
                # by the last word.
                app = words[2]
                subtest = words[3]

                # Check that no slashes are in app or subtest name
                if '/' in app:
                    self.__logger.doErrorLogging(f"Invalid application name contains slashes in line: {tmpline}. Skipping.")
                    continue
                if '/' in subtest:
                    self.__logger.doErrorLogging(f"Invalid test name contains slashes in line: {tmpline}. Skipping.")
                    continue

                nm_iters = 1
                if len(words) == 5:
                    nm_iters = int(words[4])
                include_test = True
                # if app_filter is provided and the app is not in the selection, drop it
                if app_filter and not any([re.search(patt, app) for patt in app_filter.split(',')]):
                    self.__logger.doDebugLogging(f"Dropping app.subtest {app}.{subtest} due to runtests.py --app-filter argument.")
                    include_test = False
                # if test_filter is provided and the test is not in the selection, drop it
                if test_filter and not any([re.search(patt, subtest) for patt in test_filter.split(',')]):
                    self.__logger.doDebugLogging(f"Dropping app.subtest {app}.{subtest} due to runtests.py --test-filter argument.")
                    include_test = False
                # if all checks have passed, add the test
                if include_test:
                    # Add nm_iters parallel copies of the same test
                    for i in range(0, nm_iters):
                        self.__tests.append([app,subtest])
            elif firstword == rgt_input_file.path_to_test_entry:
                if (len(words) == 3):
                    # Validate Path_to_tests here:
                    test_path = os.path.expanduser(words[2])
                    test_path = os.path.expandvars(test_path)
                    self.__logger.doDebugLogging(f"Validating if {test_path} (set via Path_to_tests) exists.")
                    if self.__path_to_tests:
                        self.__logger.doWarningLogging(f"Path_to_tests already set, ignoring Path_to_tests = {test_path}.")
                    elif os.path.exists(test_path):
                        self.__path_to_tests = test_path
                    else:
                        self.__logger.doCriticalLogging("Invalid path_to_test")
                        self.__tests = []
                        return False
                else:
                    log_message = "Invalid number of words in path line: " + tmpline
                    self.__logger.doCriticalLogging(log_message)
                    self.__tests = []
                    return False
            elif firstword == rgt_input_file.harness_task_entry:
                if (len(words) == 3):
                    if words[2] in harness_modes.valid_modes:
                        self.__harness_task.append(words[2])
                    else:
                        self.__logger.doCriticalLogging(f"Invalid harness task supplied in input file: {tmpline.strip()}. Valid tasks: {','.join(harness_modes.valid_modes)}")
                        self.__tests = []
                        return False
                else:
                    self.__logger.doCriticalLogging(f"Invalid number of words in task line: {tmpline}")
                    self.__tests = []
                    return False
            elif firstword == rgt_input_file.include_entry:
                if len(words) == 2:
                    if not self.__read_file(words[1]):
                        self.__logger.doCriticalLogging(f"Failed to parse included input file {words[1]}.")
                        self.__tests = []
                        return False
                else:
                    self.__logger.doCriticalLogging(f"Invalid number of words in include line: {tmpline}")
                    self.__tests = []
                    return False
            else:
                self.__logger.doCriticalLogging(f"Invalid line in harness input file: {tmpline}.")
                self.__tests = []
                return False
        return True

    def __is_comment_line(self,word):
        if word[0] == rgt_input_file.comment_line_entry:
            return True
        else:
            return False

    def get_harness_tasks(self):
            return self.__harness_task

    def get_tests(self):
            return self.__tests

    def get_path_to_tests(self):
            return self.__path_to_tests


