#! /usr/bin/env python3
"""Contains utilities for returning the registered unique name for a given machine.

This module makes avaiable methods for getting the registered unique machine names. 
Each machine must be registered in the INI file 'registered_machines.ini'. 

Exceptions Raised
-----------------
_NotFoundRegisteredMachineNameError
_RegisteredMachineFileError

"""


# System imports
import os
import sys
import string
import argparse
import logging

# Local imports

MODULE_LOGGER_NAME=__name__
"""str: The name of this module's logger."""

REGISTER_MACHINES = os.path.join(os.getenv("OLCF_HARNESS_DIR"),"configs","registered_machines.ini")
"""str : The file path to the the ini file that stores the registered machines"""

def _create_logger_description():
    frmt_header = "{0:10s} {1:40.40s} {2:5s}\n"
    frmt_items = frmt_header
    header1 =  frmt_header.format("Level", "Description", "Option Value" )  
    header1_len = len(header1)
    log_option_desc = "The logging level. The standard levels are the following:\n\n"
    log_option_desc += header1
    log_option_desc += "-"*header1_len  + "\n"
    log_option_desc += frmt_items.format("NOTSET", "All messages will be processed", "0" )  
    log_option_desc += frmt_items.format("", "processed", " \n" )  
    log_option_desc += frmt_items.format("DEBUG", "Detailed information, typically of ", "10" )  
    log_option_desc += frmt_items.format("", "interest only when diagnosing problems.", "\n" )  
    log_option_desc += frmt_items.format("INFO", "Confirmation that things", "20" )  
    log_option_desc += frmt_items.format("", "are working as expected.", " \n" )  
    log_option_desc += frmt_items.format("WARNING ", "An indication that something unexpected , ", "30" )  
    log_option_desc += frmt_items.format("", "happened or indicative of some problem", "" )  
    log_option_desc += frmt_items.format("", "in the near future.", "\n" )  
    log_option_desc += frmt_items.format("ERROR ", "Due to a more serious problem ", "40" )  
    log_option_desc += frmt_items.format("", "the software has not been able ", "" )  
    log_option_desc += frmt_items.format("", "to perform some function. ", "\n" )  
    log_option_desc += frmt_items.format("CRITICAL ", "A serious error, indicating ", "50" )  
    log_option_desc += frmt_items.format("", "that the program itself may be unable", "" )  
    log_option_desc += frmt_items.format("", "to continue running.", "\n" )  
    return log_option_desc

def _create_module_logger(log_id, log_level):
    logger = logging.getLogger(log_id)
    logger.setLevel(log_level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

def _get_module_logger():
    logger = logging.getLogger(MODULE_LOGGER_NAME)
    return logger


def _read_registered_machines_ini():
    """ Read the ini file REGISTERED_MACHINES and returns a ConfigParser object."""
    import configparser

    if not os.path.exists(REGISTER_MACHINES):
        raise _RegisteredMachineFileError(REGISTER_MACHINES)

    with open(REGISTER_MACHINES,"r") as in_file:
        ini_parser = configparser.ConfigParser()
        ini_parser.read_file(in_file,REGISTER_MACHINES)

    return ini_parser

class _Error(Exception):
    """Base class for exceptions in this module"""
    pass

class _NotFoundRegisteredMachineNameError(_Error):
    """Raised when the hostname does not match any regular expressions the registered machine INI file.
    
    Parameters
    ----------
    regex : str
        A string containing the Python regular expression.
    """

    def __init__(self,regex):
        self._regex=regex
        self._errormessage = ("No cluster in registered machines INI file "
                              "found that matches the python regular expression {}".format(self._regex))

    @property
    def error_message(self):
        """Returns the error message.
        
        Returns
        -------
        str
            The error message string. 

        """
        return self._errormessage

class _RegisteredMachineFileError(_Error):
    """Raised when the registered machine file is not found."""
    def __init__(self,filepath):
        """ The class constructor

        Parameters
        ----------
        filepath : str
            The path to the registered machine ini file.

        """

        self._filepath = filepath
        self._errormessage = ("The INI file that contains "
                              "the machines registrations is not found: {}".format(self._filepath))

    @property
    def error_message(self):
        """Returns a string containing the error message.
        
        Returns
        -------
        str
            The error message string. 

        """
        return self._errormessage

def get_registered_unique_name_based_on_hostname():
    """Returns the registered unique machine name for the machine on which this program is launched. 

    Returns
    -------
    str
        The regestered unique machine name as regestered in file regestered_machine.ini.

    """
    import socket
    import re

    # Initialize this machine registered unique machine name to temporary value.
    # We will get the actual registered machine name for this computer.
    unique_machine_name = None

    # Get this machine hostname as returned by getfqdn.
    machine_gethostname = socket.getfqdn()

    # Read the INI file that stores registered machines names.
    rm_ini = _read_registered_machines_ini()

    for cluster in rm_ini.sections():
        # For this cluster get the python regular expression for matching against.
        regex_pattern=rm_ini[cluster]["python regular expression"]
        re_compiled = re.compile(regex_pattern)
        if re_compiled.search(machine_gethostname) :
            # We have found a match, therefore get the 
            # registered machine name of this cluster
            unique_machine_name = rm_ini[cluster]["unique machine name"] 
            unique_machine_name = unique_machine_name.strip()
            break
    if unique_machine_name == None:
        raise _NotFoundRegisteredMachineNameError(regex_pattern)

    return unique_machine_name

def parse_arguments(argv):

    # Create a string of the description of the 
    # program
    program_description = "Returns a unique name for the machine that this program is launched on." 

    # Create an argument parser.
    my_parser = argparse.ArgumentParser(
            description=program_description,
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=True)

    # Add an optional argument for the logging level.
    my_parser.add_argument("--log-level",
                           type=int,
                           default=logging.WARNING,
                           help=_create_logger_description() )

    my_args = my_parser.parse_args(argv)

    return my_args 

def main():

    argv = sys.argv[1:]
    args = parse_arguments(argv)

    logger = _create_module_logger(log_id=MODULE_LOGGER_NAME,
                                   log_level=args.log_level)

    logger.info("Start of main program")

    try:
        registered_unique_machine_name = get_registered_unique_name_based_on_hostname()
    except (_NotFoundRegisteredMachineNameError) as err:
        logger.error("Error in getting machine unique registered name.")
        print(err.error_message)
        sys.exit()

    logger.info("Unique Machine Name: {}".format(registered_unique_machine_name)) 
    logger.info("End of main program")

if __name__ == "__main__" :

    main()
