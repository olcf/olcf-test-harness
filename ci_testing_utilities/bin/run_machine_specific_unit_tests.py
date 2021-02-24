#! /usr/bin/env python3
## @package run_basic_unit_tests
#  This module contains the main function to run the Harness basic unit tests.

# System imports
import os
import sys
import string
import argparse # Needed for parsing command line arguments.
import logging  # Needed for logging events.
import shlex,subprocess # Needed for launching command line jobs
from collections import OrderedDict

# Local imports
from harness_unit_tests import harness_unittests_exceptions
from harness_unit_tests.harness_unittests_logging import create_logger_description
from harness_unit_tests.harness_unittests_logging import create_logger

## @fn parse_arguments( )
## @brief Parses the command line arguments.
##
## @details Parses the command line arguments and
## returns A namespace.
##
## @return A namespace. The namespace contains attributes
##         that are the command line arguments.
def parse_arguments():

    # Create a string of the description of the 
    # program
    program_description = "Your program description" 

    # Create an argument parser.
    my_parser = argparse.ArgumentParser(
            description=program_description,
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=True)

    # Add an optional argument for the logging level.
    my_parser.add_argument("--log-level",
                           type=str,
                           default=logging.WARNING,
                           help=create_logger_description() )

    my_parser.add_argument("--machine",
                           type=str,
                           help="The name of the machine",
                           required=True) 

    my_parser.add_argument("--harness-config-tag",
                           type=str,
                           help="The harness configig tag",
                           required=True)

    my_args = my_parser.parse_args()

    return my_args 

def _do_machine_specific_tests():
    my_machine_name = os.getenv('HUT_MACHINE_NAME')
    if my_machine_name == None:
        message = "The environmental variable HUT_MACHINE_NAME is not set."
        raise harness_unittests_exceptions.EnvironmentalVariableNotSet('HUT_MACHINE_NAME',message)

    my_config_tag = os.getenv('HUT_CONFIG_TAG')
    if my_config_tag == None:
        message = "The environmental variable HUT_CONFIG_TAG is not set."
        raise harness_unittests_exceptions.EnvironmentalVariableNotSet('HUT_MACHINE_NAME',message)

    my_unittests = OrderedDict()
    my_unittests_return_code = OrderedDict()

    # Add test for machine specific tests.
    my_unittests["test_machine_specific_tests.py"] = "python3 -m unittest -v harness_unit_tests.test_machine_specific_tests"
    my_unittests_return_code["test_machine_specific_tests.py"] = 0

    for module_name,test_command_line in my_unittests.items():
        args = shlex.split(test_command_line)
        my_test_process = subprocess.run(args)
        my_unittests_return_code[module_name] = my_test_process.returncode

    return my_unittests_return_code

## @fn main ()
## @brief The main function.
def main():
    args = parse_arguments()

    logger = create_logger(log_id='machine_unit_tests.log',
                           log_level=args.log_level)

    logger.info("Start of main program")

    retcode = None
    try:
        retcode = _do_machine_specific_tests()
    except harness_unittests_exceptions.EnvironmentalVariableNotSet as err:
        print(err.message) 

    logger.info("End of main program")

    return retcode

if __name__ == "__main__":
    my_unittests_return_code = main()

    if my_unittests_return_code:
        nm_failed_tests = 0
        for module_name,test_return_code in my_unittests_return_code.items():
            if test_return_code != 0:
                nm_failed_tests += 1
        retcode = 0 if nm_failed_tests == 0 else 1
    else:
        retcode = 1

    sys.exit(retcode)
