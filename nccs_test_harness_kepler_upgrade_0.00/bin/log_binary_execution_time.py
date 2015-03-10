#! /usr/bin/env python

import argparse
import sys
import os
from libraries import status_file

def main():

    argv = sys.argv

    #----------------------------------
    # Create a parse for my arguments -
    #----------------------------------
    parser = create_a_parser()

    Vargs = parser.parse_args()

    log_mode = str(Vargs.mode[0])
    unique_id = Vargs.uniqueid[0]
    scriptsdir = Vargs.scriptsdir[0]


    #
    # Get the current working directory.
    #
    cwd = os.getcwd()
   
    #
    # Change to the scripts directory of the test,
    #
    os.chdir(scriptsdir) 

    jstatus = status_file.rgt_status_file(unique_id,mode="Old")

    if log_mode == "start":
        jstatus.logStartExecutionTime()
        jstatus.add_result("17",mode="Add_Binary_Running")
    else:
        jstatus.logFinalExecutionTime()

    #
    # Change back to the starting directory of the test,
    #
    os.chdir(cwd) 
    
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
        
    parser.add_argument("--scriptsdir", nargs=1,required=True,
                        help="The location of the test scripts directory. Must be an absolute path.")
    
    parser.add_argument("--uniqueid", nargs=1,required=True,
                        help="The unique id of the test.")
    

    parser.add_argument("--mode", required=True,nargs=1,choices=["start","final"],
                        help="Used to decide to where log the current time the start or final execution log file")
    
    return parser

if __name__ == '__main__':
    main()
