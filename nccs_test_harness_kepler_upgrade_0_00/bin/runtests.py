#! /usr/bin/env python3
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
                        required=False,choices=["serial","parallel"],
                        default="serial",
                        help="The manner of concurrency to run. Serial performs each Application/Subtest in sequence. Parallel is concurrency over the Application/Subtest. Threaded has been deprecated and will be removed in a future release.")

    parser.add_argument("--inputfile",
                        required=False,
                        default="rgt.input",
                        help="Optional argument to pass an input with a name other than rgt.input.")

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
    inputfile = Vargs.inputfile
    
    #
    # Read the input
    #    
    ifile = input_files.rgt_input_file(inputfilename=inputfile)
    
    rgt = regression_test.Harness(ifile,
                                 concurrency)
    if concurrency == "serial":
        rgt.run_me_serial()
    elif concurrency == "parallel":
        rgt.run_me_parallel()

    return rgt
    
if __name__ == "__main__":
    runtests()

