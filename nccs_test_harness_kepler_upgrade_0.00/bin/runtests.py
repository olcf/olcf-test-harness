#! /usr/bin/env python
from libraries import input_files
from libraries import regression_test

import shlex
import argparse
import sys
import string

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

def create_a_parser():
    """Parses the command line arguments.

    Arguments:
    None

    Returns:
    An ArgParser object that contains the information of the 
    command line arguments.

    """
    parser = argparse.ArgumentParser(description="Runs the harness tasks of the selected Application and tests",
                                     add_help=True)
        
    parser.add_argument("--concurrency", 
                        required=True,choices=["serial","threaded"],
                        help="The manner of concurrency to run. Serial performs each Application/Subtest in sequence. Threaded is concurrency over the Application/Subtest.")

    return parser

def runtests(my_arg_string=None):
    argv = None
    if my_arg_string == None:
        argv = sys.argv[1:]
    else:
        argv = shlex.split(my_arg_string)
       

    #
    # Parse command line arguments
    #
    parser = create_a_parser()
    Vargs = parser.parse_args(argv)
    concurrency = Vargs.concurrency
    
    #
    # Read the input
    #    
    ifile = input_files.rgt_input_file()
    
    rgt = regression_test.run_me(ifile,concurrency)
    return rgt
    
if __name__ == "__main__":
    runtests()

