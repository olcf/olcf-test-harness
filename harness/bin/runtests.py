#! /usr/bin/env python3

# Python package imports
import shlex
import argparse
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

    con_help = ("Harness concurrency: (default: 'serial')\n"
                "  'serial'   - application tests are processed sequentially (one after the other)\n"
                "  'parallel' - harness may use threads to process application tests concurrently")
    parser.add_argument('-c', '--concurrency',
                        required=False,
                        choices=['serial', 'parallel'],
                        default='serial',
                        help=con_help)

    parser.add_argument('-i', '--inputfile',
                        required=False,
                        default="rgt.input",
                        help="Input file name (default: %(default)s)")
    
    parser.add_argument("--configfile",
                        required=False,
                        default="master.ini",
                        help="Configuration file name (default: %(default)s)")
    
    parser.add_argument("--loglevel",
                         required=False,
                         choices=["DEBUG","INFO","WARNING", "ERROR", "CRITICAL"],
                         default="INFO",
                         help="Logging level (default: %(default)s)")

    out_help = ("Destination for harness stdout/stderr messages:\n"
                "  'screen'  - print messages to console (default for '--concurrency=serial')\n"
                "  'logfile' - print messages to log file (default for '--concurrency=parallel')")
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
                        choices=['checkout', 'start', 'stop', 'status'],
                        help=mode_help)

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
    concurrency = Vargs.concurrency
    inputfile = Vargs.inputfile
    configfile = Vargs.configfile
    loglevel = Vargs.loglevel
    stdout_stderr = Vargs.output
    runmode = Vargs.mode

    # Warn user if running in parallel mode and output is written to screen.
    warning_message = None
    if (concurrency == 'parallel') and (stdout_stderr == 'screen'):
        warning_message = ("Warning! You have chosen to run the harness in 'parallel' mode\n"
                           "with stdout/stderr printed to the 'screen'. This may result in\n"
                           "incomprehensible output due to interleaved messages from concurrent\n"
                           "application tests. Resetting output mode to 'logfile'.")
        print(warning_message)
        stdout_stderr = 'logfile'

    # Print the effective command line to stdout.
    command_options = ("Effective command line: "
                       "runtests.py"
                       " --concurrency {my_concurrency}"
                       " --inputfile {my_inputfile}"
                       " --configfile {my_configfile}"
                       " --loglevel {my_loglevel}"
                       " --output {my_output}"
                       " --mode {my_runmode}")
    effective_command_line = command_options.format(my_concurrency = concurrency,
                                                    my_inputfile = inputfile,
                                                    my_configfile = configfile,
                                                    my_loglevel = loglevel,
                                                    my_output = stdout_stderr,
                                                    my_runmode = runmode)
    print(effective_command_line)


    #
    # Read the input and master config
    #    
    ifile = input_files.rgt_input_file(inputfilename=inputfile,configfilename=configfile,runmodecmd=runmode)
    
    # Create the harness object
    rgt = regression_test.Harness(ifile,
                                  concurrency,
                                  loglevel,
                                  stdout_stderr)

    rgt.run_me(my_effective_command_line=effective_command_line,
               my_warning_messages=warning_message)

    return rgt
    
if __name__ == "__main__":
    runtests()

