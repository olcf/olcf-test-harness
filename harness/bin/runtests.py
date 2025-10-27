#! /usr/bin/env python3

# Python package imports
import shlex
import argparse
import os
import sys

# My harness package imports
from libraries import input_files
from libraries import regression_test
from libraries import command_line
from libraries.config_file import rgt_config_file
from libraries.rgt_loggers import rgt_logger_factory

#
# Authors: Arnold Tharrington, Wayne Joubert, Veronica Vergera, Mark Berrill, and Mike Brim
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

#-----------------------------------------------------
# This section defines the main logger and its       -
# file and console handlers.                         -
#                                                    -
#-----------------------------------------------------

MAIN_LOGGER_NAME='main_logger'
"""str: The name of the main logger."""

MAIN_LOGGER_LEVEL='DEBUG'
"""The log level of the main logger."""

MAIN_LOGGER_FILEHANDLER_FILENAME="main.log"
"""str: The file name for the main logger fileHandler."""

MAIN_LOGGER_FILEHANDLER_LOGLEVEL='DEBUG'
"""The log level for the main log file handler."""

MAIN_LOGGER_CONSOLE_HANDLER_LOGLEVEL='WARNING'
"""The log level for the main log console handler."""

def get_main_logger():
    """ Returns the main logger.

    Returns
    -------
    Logger
    """
    return rgt_logger_factory.create_rgt_logger(
                        logger_name=MAIN_LOGGER_NAME,
                        fh_filepath=MAIN_LOGGER_FILEHANDLER_FILENAME,
                        logger_threshold_log_level=MAIN_LOGGER_LEVEL,
                        fh_threshold_log_level=MAIN_LOGGER_FILEHANDLER_LOGLEVEL,
                        ch_threshold_log_level=MAIN_LOGGER_CONSOLE_HANDLER_LOGLEVEL)

#-----------------------------------------------------
# End of section we define the main logger and its   -
# file and console handlers.                         -
#                                                    -
#-----------------------------------------------------

#-----------------------------------------------------
# This section sets the permitted and/or default     -
# for the command line options of the command        -
# runtests.py.                                       -
#                                                    -
# We put the permitted values in a tuple so as       -
# to make the values immutable.                      -
#-----------------------------------------------------

# This section pertains to the harness tasks option.

USE_HARNESS_TASKS_IN_RGT_INPUT_FILE="use_input_file"
"""
str: A flag for the harness to use the designated input file for runtests.py for the
     the harness tasks.

"""

DEFAULT_HARNESS_TASK=USE_HARNESS_TASKS_IN_RGT_INPUT_FILE
"""
str: The default harness task.

If no task option is specified on the command line runtests.py, then the
default harness task will we default to the tasks in the runtests.py input file.

"""

PERMITTED_HARNESS_TASKS=('checkout','start','stop','status', USE_HARNESS_TASKS_IN_RGT_INPUT_FILE)
"""
A tuple of the permitted harness tasks.

These tasks are set by means of command line arguments to the runtests.py
command: --mode | -m <permitted_tasks>. The following tasks are supported.

* use_input_file - Uses the harness tasks in the runtests.py input file.
* checkout - Checks out via a git clone command the harness application-test form the repository.
* start - Starts the application-test(s).
* stop - Stops an application-test(s).
* status - Prints to std out the status of the application-test(s).

Specifying an unsupported task will result in the harness aborting with
an error.

To add an additional task do the following:

* Add the value to the PERMITTED_HARNESS_TASKS tuple.
* In function create_parser(), located in module bin.runtests.py, add the appropriate arguments to the parser.
* Implement unit tests in module ci_testing_utilities.harness_unit_tests.test_runtests.py.

"""


# This section pertains to the log level option.
PERMITTED_LOG_LEVELS=("NOTSET","DEBUG","INFO","WARNING", "ERROR", "CRITICAL")
"""
A tuple of str: The permitted log levels.

The log levels are set by means of the command line arguments to the
runtests.py command: --loglevel <permitted_loglevel>. The following loglevels
are supported.

* NOTSET
* DEBUG
* INFO
* WARNING
* ERROR
* CRITICAL

Specifying an unsupported loglevel will result in the harness aborting with an
error.
"""

DEFAULT_LOG_LEVEL="WARNING"
"""
str: The default log level.

If no loglevel option is specified on the command line, then default loglevel
will be set to WARNING.
"""

# This section pertains to the concurrency option. It
# is deprecated.
PERMITTED_CONCURRENCY_VALUES=('serial','parallel')
"""
A tuple of str: deprecated feature. This concurrency option is hard-coded to serial.

This tuple are vestiges of running the harness in parallel.
The parallel running of the harness is disabled, and this
tuple will be removed.
"""

DEFAULT_CONCURRENCY=PERMITTED_CONCURRENCY_VALUES[0]
"""
str: A deprecated feature. This concurrency option is hard-coded to serial.

The parallel running of the harness is disabled, and this
module constant will be removed.
"""

# This section pertains to the input file option.
DEFAULT_INPUT_FILE='rgt.input'
"""
str: The default harness input file.

The harness input file is set by means of the command line arguments to the
runtests.py command: --inputfile | -i <harness_input_file>
If no input file is specified on the command line, then the default input
file will be used.
"""

# This section pertains to the output option.
PERMITTED_OUTPUT_VALUES=('screen','logfile')
"""
A tuple of str: The permitted values of the output option.

The harness output  options is set by means of the command line arguments to the
runtests.py command: --outputfile | -o <output>.
This tuple contains the permitted values of the output option. If no output option
is specified, then the default option will be used.

* screen - Writes logging to std out and std err.
* logfile - Writes logging to a file
"""

DEFAULT_OUTPUT=PERMITTED_OUTPUT_VALUES[0]
"""
str: The default output option.
"""

#-----------------------------------------------------
# End of section that sets the permitted and/or      -
# default for the command line options of the        -
# command runtests.py.                               -
#                                                    -
#-----------------------------------------------------

def create_parser(logger=None):
    """
    Returns an ArgumentParser object.

    The returned ArgumentParser object holds the information
    to parse the command line into Python data types.

    Parameters
    ----------
        None

    Returns
    -------
    ArgumentParser
        An object that contains the information of the
        command line arguments.

    """
    parser = argparse.ArgumentParser(description="Execute specified harness task for application tests listed in input file",
                                     allow_abbrev=False,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--inputfile',
                        required=False,
                        default=DEFAULT_INPUT_FILE,
                        help="Input file name (default: %(default)s)")

    parser.add_argument('--shuffle',
                        action='store_true',
                        help="Shuffle the order of tests before launching.")

    parser.add_argument('-c', '--configfile',
                        required=False,
                        default=rgt_config_file.getDefaultConfigFile(logger=logger),
                        type=str,
                        help="Configuration file name (default: %(default)s)")

    parser.add_argument('-l', '--loglevel',
                         required=False,
                         choices=PERMITTED_LOG_LEVELS,
                         default=DEFAULT_LOG_LEVEL,
                         help="Logging level (default: %(default)s)")

    out_help = ("Destination for harness stdout/stderr messages:\n"
                "  'screen'  - print messages to console (default)\n"
                "  'logfile' - print messages to log file\n")
    parser.add_argument('-o', '--output',
                        required=False,
                        choices=PERMITTED_OUTPUT_VALUES,
                        default=DEFAULT_OUTPUT,
                        type=str,
                        help=out_help)

    mode_help = ("Harness task:\n"
                 "  'checkout'   - checkout application tests listed in input file\n"
                 "  'start'      - start application tests listed in input file\n"
                 "  'stop'       - stop application tests listed in input file\n"
                 "  'status'     - check status of application tests listed in input file\n")
    parser.add_argument('-m', '--mode',
                        required=False,
                        help=mode_help,
                        default=USE_HARNESS_TASKS_IN_RGT_INPUT_FILE,
                        nargs='+',
                        choices=PERMITTED_HARNESS_TASKS)

    parser.add_argument("--fireworks",
                        action='store_true',
                        help="Use FireWorks to run harness tasks")

    parser.add_argument("-sb", "--separate-build-stdio",
                        action='store_true',
                        required=False,
                        default=False,
                        help="Separate output from build into build_out.stderr.txt and build_out.stdout.txt")

    parser.add_argument("--reuse-first-build",
                        action='store_true',
                        required=False,
                        default=False,
                        help="If running a test that can resubmit, re-use the first instance of the build for all tests in that chain.")

    parser.add_argument("--reuse-build-from-id",
                        action='store',
                        required=False,
                        default='',
                        help="Re-use the build from the specified test ID.")

    return parser

def parse_commandline_argv(argv, logger):
    """
    Returns a object of type HarnessParsedArguments.

    The returned object holds the Python data types of
    the Python command line.

    Parameters
    ----------
        argv : list
            Holds the command line arguments

        logger : Python logging object
            Handles logging commands

    Returns
    -------
    HarnessParsedArguments
        Stores the Python data of the command line arguments. See module
        command_line.py for details on HarnessParsedArguments object.


    """

    parser = create_parser(logger=logger)
    Vargs = parser.parse_args(argv)
    harness_parsed_args = command_line.HarnessParsedArguments(inputfile=Vargs.inputfile,
                                                              shuffle=Vargs.shuffle,
                                                              loglevel=Vargs.loglevel,
                                                              configfile=Vargs.configfile,
                                                              stdout_stderr=Vargs.output,
                                                              runmode=Vargs.mode,
                                                              use_fireworks=Vargs.fireworks,
                                                              separate_build_stdio=Vargs.separate_build_stdio,
                                                              reuse_first_build=Vargs.reuse_first_build,
                                                              reuse_build_from_id=Vargs.reuse_build_from_id)
    return harness_parsed_args

def runtests(my_arg_string=None):
    """
    The entry point of running the Harness.

    If my_arg_string is None, then sys.argv is the command line argument list.

    Parameters
    ----------
        my_arg_string : list
            A list that holds command line arguments.

    Returns
    -------
        Harness
            An object that stores/encapsulates the running of the NCCS Harness. See module
            regression_test.py for details on Harness object.
    """

    main_logger = get_main_logger()

    argv = None
    if my_arg_string == None:
        argv = sys.argv[1:]
    else:
        argv = shlex.split(my_arg_string)

    main_logger.doInfoLogging("Parsing the command line arguments.")

    harness_arguments = parse_commandline_argv(argv, main_logger)

    # Print the effective command line to stdout.
    effective_command_line = harness_arguments.effective_command_line
    main_logger.doInfoLogging(effective_command_line)

    main_logger.doInfoLogging("Completed parsing command line arguments.")

    # Read the input and master config
    main_logger.doInfoLogging("Reading the harness input file.")
    ifile = input_files.rgt_input_file(inputfilename=harness_arguments.inputfile,
                                       runmodecmd=harness_arguments.runmode,
                                       logger=main_logger)
    main_logger.doInfoLogging("Completed reading the harness input file.")

    # Check if there were any tests found:
    if len(ifile.get_tests()) == 0:
        main_logger.doErrorLogging("No tests found in input file. Aborting.")
        return
    
    main_logger.doInfoLogging("Reading the harness config file.")
    try:
        config = rgt_config_file(configfilename=harness_arguments.configfile, logger=main_logger)
    except NameError as e:
        main_logger.doCriticalLogging(f"Could not find Harness config file: {harness_arguments.configfile}.")
        exit(1)
    main_logger.doInfoLogging("Completed reading the harness config file.")

    # Create and run the harness
    rgt = regression_test.Harness(config, ifile,
                                  harness_arguments.loglevel,
                                  harness_arguments.stdout_stderr,
                                  harness_arguments.use_fireworks,
                                  harness_arguments.separate_build_stdio,
                                  harness_arguments.reuse_first_build,
                                  harness_arguments.reuse_build_from_id,
                                  shuffle=harness_arguments.shuffle)

    main_logger.doInfoLogging("Created an instance of the harness.")
    main_logger.doInfoLogging("Harness: " + str(rgt))
    main_logger.doInfoLogging("Running the harness tasks.")
    rgt.run_me(my_effective_command_line=effective_command_line)
    main_logger.doInfoLogging("Completed running the harness tasks.")

    return rgt

if __name__ == "__main__":

    my_main_logger = get_main_logger()

    my_main_logger.doInfoLogging("Start of harness")

    rgt = runtests()

    my_main_logger.doInfoLogging("End of harness.")


