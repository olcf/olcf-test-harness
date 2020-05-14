#! /usr/bin/env python3

# Python package imports
import shlex
import argparse
import os
import sys
import string
import configparser

# My harness package imports
from libraries import input_files
from libraries import regression_test

#
# Authors: Arnold Tharrington, Wayne Joubert, Veronica Vergera, and Mark Berrill
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

def create_parser():
    """Parses the command line arguments.

    Arguments:
    None

    Returns:
    An ArgParser object that contains the information of the
    command line arguments.

    """
    parser = argparse.ArgumentParser(description="Execute specified harness task for application tests listed in input file",
                                     allow_abbrev=False,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--inputfile',
                        required=False,
                        default="rgt.input",
                        help="Input file name (default: %(default)s)")

    parser.add_argument("--loglevel",
                         required=False,
                         choices=["DEBUG","INFO","WARNING", "ERROR", "CRITICAL"],
                         default="INFO",
                         help="Logging level (default: %(default)s)")

    out_help = ("Destination for harness stdout/stderr messages:\n"
                "  'screen'  - print messages to console (default)\n"
                "  'logfile' - print messages to log file")
    parser.add_argument('-o', '--output',
                        required=False,
                        choices=['logfile','screen'],
                        default='screen',
                        help=out_help)

    mode_help = ("Harness task:\n"
                 "  'checkout' - checkout application tests listed in input file\n"
                 "  'start'    - start application tests listed in input file\n"
                 "  'stop'     - stop application tests listed in input file\n"
                 "  'status'   - check status of application tests listed in input file")
    parser.add_argument('-m', '--mode',
                        required=False,
                        help=mode_help)
                        #choices=['checkout', 'start', 'stop', 'status'],

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
    parser = create_parser()
    Vargs = parser.parse_args(argv)
    inputfile = Vargs.inputfile
    loglevel = Vargs.loglevel
    stdout_stderr = Vargs.output
    runmode = Vargs.mode

    # Print the effective command line to stdout.
    command_options = ("Effective command line: "
                       "runtests.py"
                       " --inputfile {my_inputfile}"
                       " --loglevel {my_loglevel}"
                       " --output {my_output}"
                       " --mode {my_runmode}")
    effective_command_line = command_options.format(my_inputfile = inputfile,
                                                    my_loglevel = loglevel,
                                                    my_output = stdout_stderr,
                                                    my_runmode = runmode)
    print(effective_command_line)


    # Determine the machine
    machinename = 'master'
    if 'OLCF_HARNESS_MACHINE' in os.environ:
        machinename = os.environ['OLCF_HARNESS_MACHINE']
    configfile = machinename + '.ini'
    print('Using machine config:', configfile)

    # Read the harnesss input file
    ifile = input_files.rgt_input_file(inputfilename=inputfile,
                                       configfilename=configfile,
                                       runmodecmd=runmode)

    # Create and run the harness
    rgt = regression_test.Harness(ifile, loglevel, stdout_stderr)
    rgt.run_me(my_effective_command_line=effective_command_line)

    return rgt

if __name__ == "__main__":
    runtests()

