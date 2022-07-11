#! /usr/bin/env python3

# Python imports
import os
import sys
import subprocess
import getopt
import string

# Harness imports
from libraries.apptest import subtest
from libraries.subtest_factory import SubtestFactory 
from libraries.layout_of_apps_directory import get_layout_from_runarchivedir
from libraries.layout_of_apps_directory import get_path_to_logfile_from_runarchivedir
from libraries.rgt_loggers import rgt_logger_factory

#
# Author: Arnold Tharrington, Scientific Computing Group
# Modified by: Wayne Joubert, Scientific Computing Group
# Modified by:: Veronica G. Vergara Larrea, User Assitance Group
# National Center for Computational Sciences
# Oak Ridge National Laboratory
#

#
# This program drives the check_executable.x script.
# It is designed such that it will be called from the Scripts directory.
#

MODULE_THRESHOLD_LOG_LEVEL = "DEBUG"
"""str : The logging level for this module. """

MODULE_LOGGER_NAME = "check_executable_driver"
"""The logger name for this module."""

def get_log_level():
    """Returns the test harness driver threshold log level.

    Returns
    -------
    int 
    """
    return MODULE_THRESHOLD_LOG_LEVEL

def get_logger_name():
    """Returns the logger name for this module."""
    return MODULE_LOGGER_NAME 

def usage():
    print ("Usage: check_executable_driver.py [-h|--help] [-i <test_id_string>] -p <path_to_results>")
    print ("A driver program that calls check_executable.x")
    print
    print ("-h, --help            Prints usage information.")
    print ("-p <path_to_results>  The absoulte path to the results of a test.")
    print ("-i <test_id_string>   The test's unique id.")

def main():

    #
    # Get the command line arguments.
    #
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hi:p:")

    except getopt.GetoptError:
            usage()
            sys.exit(2)

    path_to_results = None
    test_id_string = None

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
            sys.exit(2)
        else:
            usage()
            sys.exit(2)

    if path_to_results == None:
        usage()
        sys.exit(2)

    (apps_root, app, test, testid) = get_layout_from_runarchivedir(path_to_results)

    if test_id_string != None:
        if testid != test_id_string:
            print("ERROR: user-provided test id", test_id_string, "does not match run archive id", testid)
            sys.exit(1)

    logger_threshold = "INFO"
    fh_threshold_log_level = "INFO"
    ch_threshold_log_level = "WARNING"
    fh_filepath = get_path_to_logfile_from_runarchivedir(path_to_results)
    a_logger = rgt_logger_factory.create_rgt_logger(
                                         logger_name=get_logger_name(),
                                         fh_filepath=fh_filepath,
                                         logger_threshold_log_level=logger_threshold,
                                         fh_threshold_log_level=fh_threshold_log_level,
                                         ch_threshold_log_level=ch_threshold_log_level)

    apptest = SubtestFactory.make_subtest(name_of_application=app,
                                          name_of_subtest=test,
                                          local_path_to_tests=apps_root,
                                          logger=a_logger,
                                          tag=testid)


    currentdir = os.getcwd()
    scriptsdir = apptest.get_path_to_scripts()

    if currentdir != scriptsdir:
        os.chdir(scriptsdir)

    check_command = "test_harness_driver.py --check -i " + testid
    check_exit_value = os.system(check_command)

    message = f"The check command return status is {check_exit_value}."
    apptest.doInfoLogging(message)

    if currentdir != scriptsdir:
        os.chdir(currentdir)

    return check_exit_value

if __name__ == "__main__":
    main()
