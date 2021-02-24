#! /usr/bin/env python3
## @package harness_unittests_exceptions
#  This module conatins the exceptions that are raised for the Harness unit tests.
#

# System imports
import string
import argparse # Needed for parsing command line arguments.
import logging  # Needed for logging events.

# Local imports
from harness_unit_tests.harness_unittests_logging import create_logger_description 
from harness_unit_tests.harness_unittests_logging import create_logger
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class EnvironmentalVariableNotSet(Error):
    """Exception raised for environment variables not set

    Attributes:
        expression -- The environmnetal not set.
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

## @fn _parse_arguments( )
## @brief Parses the command line arguments.
##
## @details Parses the command line arguments and
## returns A namespace.
##
## @return A namespace. The namespace contains attributes
##         that are the command line arguments.
def _parse_arguments():

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
                           type=int,
                           default=logging.WARNING,
                           help=create_logger_description() )

    my_args = my_parser.parse_args()

    return my_args 

## @fn main ()
## @brief The main function.
def main():
    args = _parse_arguments()

    logger = create_logger(log_id='hut_exceptions.log',
                           log_level=args.log_level)

    logger.info("Start of main program")

    logger.info("End of main program")

if __name__ == "main":
    main()
