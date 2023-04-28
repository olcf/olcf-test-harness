#! /usr/bin/env python3

# Python package imports
import string
import os
import configparser

# My harness package imports
from runtests import USE_HARNESS_TASKS_IN_RGT_INPUT_FILE
from runtests import get_main_logger
from libraries import rgt_utilities

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

class rgt_input_file:

    #These are the entries in the input file.
    test_entry = "test"
    path_to_test_entry = "path_to_tests"
    comment_line_entry = "#"
    harness_task_entry = "harness_task"

    def __init__(self,
                 inputfilename="rgt.input",
                 runmodecmd=None):
        self.__tests = []
        self.__harness_task = []
        self.__path_to_tests = ""
        self.__inputFileName = inputfilename

        # Read the input file. Returns True upon successful read.
        # If read_file fails, self.__tests is emptied and False is returned
        err = self.__read_file()
        if not err:
            print("ERROR: Failed to parse input file.")
            # Short-circuit upon failure
            return

        # If a CLI task was input use that instead
        if USE_HARNESS_TASKS_IN_RGT_INPUT_FILE not in runmodecmd :
            print("Overriding tasks in inputfile since CLI mode was provided")
            print("runmodecmd = ", runmodecmd)
            self.__harness_task = []
            for modetask in runmodecmd:
                if modetask == "checkout":
                    runmodetask = ["check_out_tests",None,None]
                elif modetask == "start":
                    runmodetask = ["start_tests",None,None]
                elif modetask == "stop":
                    runmodetask = ["stop_tests",None,None]
                elif modetask == "status":
                    runmodetask = ["display_tests",None,None]
                elif modetask == "influx_log":
                    runmodetask = ["influx_log",None,None]
                else:
                    runmodetask = None
                    print("Found invalid task in the command line: ", modetask)

                # Append task to this harness instance
                if runmodetask != None:
                    self.__harness_task.append(runmodetask)
                    print("self.__harness_task: ", self.__harness_task)

                # Clear mode to avoid duplicate
                runmodetask = None

        if self.__harness_task == []:
            print("ERROR: No valid tasks found in the inputfile or the CLI")

    def __read_file(self):
        ifile_obj = open(self.__inputFileName,"r")
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
                    print(log_message)
                    # Clear all tests -- invalid line in input file
                    self.__tests = []
                    return False
                # Determine the number of words. If the number of words is 4
                # The we run an indefinite number of times. If the number
                # of words is 5, the we run a definite number of times dictated
                # by the last word.
                app = words[2]
                subtest = words[3]
                nm_iters = -1
                if len(words) == 5:
                    nm_iters = int(words[4])
                self.__tests.append([app,subtest,nm_iters])

            elif firstword == rgt_input_file.path_to_test_entry:
                if (len(words) == 3):
                    # Validate Path_to_tests here:
                    self.__path_to_tests = words[2]
                else:
                    log_message = "Invalid number of words in path line: " + tmpline
                    print(log_message)
                    self.__tests = []
                    return False

            elif firstword == rgt_input_file.harness_task_entry:
                if (len(words) == 3):
                    self.__harness_task.append([words[2],None,None])
                elif (len(words) == 5):
                    self.__harness_task.append([words[2],words[3],words[4]])
                else:
                    log_message = "Invalid number of words in task line: " + tmpline
                    print(log_message)
                    self.__tests = []
                    return False
            else:
                log_message = "Invalid line: " + tmpline
                print(log_message)
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


