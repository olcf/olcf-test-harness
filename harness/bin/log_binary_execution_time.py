#! /usr/bin/env python3

import argparse
import sys
import os

from libraries.subtest_factory import SubtestFactory
from libraries.status_file_factory import StatusFileFactory
from libraries.status_file import StatusFile
from libraries.layout_of_apps_directory import get_layout_from_scriptdir

def create_a_parser():
    """Parses the arguments.

    Arguments:
    None

    Returns:
    An ArgParser object that contains the information of the 
    arguments.

    """
    parser = argparse.ArgumentParser(description="Logs the current time to the appropiate \
                                                  status execution log file.",
                                     add_help=True)
        
    parser.add_argument("--scriptsdir", nargs=1, required=True,
                        help="The location of the test scripts directory. Must be an absolute path.")
    
    parser.add_argument("--uniqueid", nargs=1, required=True,
                        help="The unique id of the test.")
    

    parser.add_argument("--mode", required=True, nargs=1, choices=["start","final"],
                        help="Used to decide to where log the current time the start or final execution log file")
    
    return parser

def main():

    #----------------------------------
    # Create a parse for my arguments -
    #----------------------------------
    parser = create_a_parser()
    Vargs = parser.parse_args()

    log_mode = str(Vargs.mode[0])
    unique_id = Vargs.uniqueid[0]
    scriptsdir = Vargs.scriptsdir[0]

    # Change to the scripts directory of the test
    cwd = os.getcwd()
    if cwd != scriptsdir:
        os.chdir(scriptsdir)

    # Get status file
    (apps_root, app, test) = get_layout_from_scriptdir(scriptsdir)
    apptest = SubtestFactory.make_subtest(name_of_application=app,
                                          name_of_subtest=test,
                                          local_path_to_tests=apps_root,
                                          tag=unique_id)
    path_to_status_file = apptest.get_path_to_status_file()
    jstatus = StatusFileFactory.create(path_to_status_file=path_to_status_file)
    jstatus.initialize_subtest(unique_id)

    # Log the appropriate event to the status file
    if log_mode == "start":
        jstatus.log_event(StatusFile.EVENT_BINARY_EXECUTE_START)
    else:
        jstatus.log_event(StatusFile.EVENT_BINARY_EXECUTE_END)

    # Change back to the starting directory of the test
    if cwd != scriptsdir:
        os.chdir(cwd)

if __name__ == '__main__':
    main()
