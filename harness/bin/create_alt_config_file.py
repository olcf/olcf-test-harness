#! /usr/bin/env python3
""" This module modifies the INI config files of the HARNESS.

The module is to be used as main program. For module usage
do the following command:

    create_alt_config_file.py -h | --help.

Only 1 entry of an INI file can be modified per program call. 
The user gives on the command line the section, key and new key value.
The specified command line input INI config file
is read, modfied, and written to disk with the specified command
line output filename. 
"""

# Python package imports

# My harness package imports


_KEY_GROUP_SIZE=3
"""int: The size of a key group.

The module level variable is used to validate
that the number of -k | --keys arguments is a 
multiple of 3, and for writing the new key values
to file.
"""
#-----------------------------------------------------
# Public members                                     -
#                                                    -
#-----------------------------------------------------

def main():
    """The entry point of this module.
    """

    # Parse the arguments on the command line arguments.
    args = _parse_arguments()

    # Create a logger object for general purpose debugging.
    logger = _create_logger(log_id='main_logger',
                            log_level=args.log_level)

    logger.info("Start of main program")

    # Check the validity of the command line arguments.
    _check_commandline_arguments_validity(logger,args)

    # Write the new config file.
    _write_new_config_file(logger,
                           args.input_config_filename[0],
                           args.output_config_filename[0],
                           args.keys[0])

    logger.info("End of main program")

#-----------------------------------------------------
# End of public members                              -
#                                                    -
#-----------------------------------------------------

#-----------------------------------------------------
# Private members                                    -
#                                                    -
#-----------------------------------------------------

def _create_logger_description():
    """Returns a string that contains the logger description.
    """
    frmt_header = "{0:10s} {1:40.40s} {2:5s}\n"
    frmt_items = frmt_header
    header1 =  frmt_header.format("Level", "Description", "Option Value" )  
    header1_len = len(header1)
    log_option_desc = "The logging level. The standard levels are the following:\n\n"
    log_option_desc += header1
    log_option_desc += "-"*header1_len  + "\n"
    log_option_desc += frmt_items.format("NOTSET", "All messages will be processed", "0" )  
    log_option_desc += frmt_items.format("", "processed", " \n" )  
    log_option_desc += frmt_items.format("INFO", "Confirmation that things", "10" )  
    log_option_desc += frmt_items.format("", "are working as expected.", " \n" )  
    log_option_desc += frmt_items.format("DEBUG", "Detailed information, typically of ", "20" )  
    log_option_desc += frmt_items.format("", "interest only when diagnosing problems.", "\n" )  
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

def _create_logger(log_id, log_level):
    """
    Returns a Logger object.

    The returned logger object is named *log_id* and has loglevel *log_level*.
    See logging module python documentation.

    Parameters
    ----------
        log_id : str
            The name of the logger

        log_level : A logging level 
            The log level (e.g. logging.DEBUG, logging.INFO, etc.).

    Returns
    -------
    Logger
    """
    import logging  # Needed for logging events.
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

def _parse_arguments():
    """
    Parses the command line arguments and returns namespace.

    Returns
    -------
        A namespace. 
            The namespace contains attributes
            that are the command line arguments.
    """
    import argparse # Needed for parsing command line arguments.

    # Create a string of the description of the 
    # program
    program_description =  "This program creates a new config file" 
    program_description += "by copying and modfying an existing config file." 

    # Create an argument parser.
    my_parser = argparse.ArgumentParser(
            description=program_description,
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=True)

    my_parser = _add_all_arguments(my_parser)


    my_args = my_parser.parse_args()

    return my_args 

def _add_all_arguments(a_parser):
    """
    Adds all arguments to parser and returns a parser.

    Parameters
    ----------
    a_parser: An ArgumentParser
        The parser of which is to be modified an returned.
    """
    a_parser = _add_argument_loglevel(a_parser)
    a_parser = _add_argument_multiple_keys(a_parser)
    a_parser = _add_argument_output(a_parser)
    a_parser = _add_argument_inputfile(a_parser)
    return a_parser

def _add_argument_loglevel(a_parser):
    """
    Adds the help argument to the parser argument and returns the parser object

    Parameters
    ----------
    a_parser: An ArgumentParser
        The parser of which is to be modified an returned.
    
    Returns
    -------
        A parser object
    """
    import logging  # Needed for logging events.

    # Add an optional argument for the logging level.
    a_parser.add_argument("--log-level",
                          type=int,
                          default=logging.WARNING,
                          help=_create_logger_description() )
    return a_parser

def _add_argument_multiple_keys(a_parser):
    """
    Adds multiple key arguments to the parser argument and returns the parser object.

    The key arguments are required requires multiple of _KEY_GROUP_SIZE arguments:
    -k | --keys <key_1> <section_1> <new value for key_1> ...

    Parameters
    ----------
    a_parser: An ArgumentParser
        The parser of which is to be modified an returned.
    
    Returns
    -------
        A parser object
    """
    a_parser.add_argument("-k","--keys",
                          action="append",
                          required=True,
                          nargs="+",
                          type=str,
                          help="The section, key and new key value .\n\n")
    return a_parser

def _add_argument_output(a_parser):
    """
    Adds the output argument to the parser argument and returns the parser object.

    The outp file argument is mandatory. The output file is the name of the new
    machine config file.

    Parameters
    ----------
    a_parser: An ArgumentParser
        The parser of which is to be modified an returned.
    
    Returns
    -------
        A parser object
    """
    a_parser.add_argument("-o","--output-config-filename",
                          required=True,
                          type=str,
                          nargs=1,
                          help=("The name of the newly created config file.\n"
                                "The output config filename must be different from the\n"
                                "input config filename.\n\n")
                          )
    return a_parser

def _add_argument_inputfile(a_parser):
    """
    Adds the input file argument to the parser argument and returns the parser object.

    Parameters
    ----------
    a_parser: An ArgumentParser
        The parser of which is to be modified an returned.
    
    Returns
    -------
        A parser object
    """
    a_parser.add_argument("-i","--input-config-filename",
                          required=True,
                          type=str,
                          nargs=1,
                          help=("The name of the input config file.\n"
                                "The input config filename must be different from the\n"
                                "output config filename.\n\n")
                          )
    return a_parser

def _check_commandline_arguments_validity(a_logger,args):
    """
    Check the validity of the values of the command line arguments.

    Parameters
    ----------
    logger: A Logger object
        Used primarily for debugging and logging messages to std out.

    args: A namespace
        Stores the attributes of the command line argument.

    """
    import sys

    try :
        _validate_io_file_arguments(input_filename=args.input_config_filename[0],
                                    output_filename=args.output_config_filename[0])

        _validate_multiple_key_arguments(key_arguments=args.keys[0])

    except (_SameIOFileError, _InputConfigFileError, _OutputConfigFileError) as err:
        a_logger.error("Error in i/o file arguments.")
        print(err.error_message)
        sys.exit()
    except ( _NumberKeyError ) as err:
        a_logger.error("Error in key arguments.")
        print(err.error_message)
        sys.exit()

def _validate_io_file_arguments(input_filename,
                                output_filename):
    """Validates the filenames with respect several criteria.
    
    If input_filename is the same as output_filename, then raises a _SameIOFileError exception.
    If the input file doesn't exist, then raise a _InputConfigFileError exception.
    If the output file exists, then raise a _OutputConfigFileError exception.
    
    Parameters
    ----------
    input_filename : str
        The input config file name

    output_filename : str
        The output config file name

    Raises
    ------
    _SameIOFileError
    _InputConfigFileError
    _OutputConfigFileError

    """

    import os

    if input_filename == output_filename:
        raise _SameIOFileError(input_filename,output_filename)

    if not os.path.exists(input_filename):
        raise _InputConfigFileError(input_filename)

    if os.path.exists(output_filename):
        raise _OutputConfigFileError(output_filename)

    return

def _validate_multiple_key_arguments(key_arguments):
    """Validates the key arguments.

    The key arguments must be a multiple of _KEY_GROUP_SIZE or the
    program will fail.

    Parameters
    ----------
    key_arguments: A list of strings
        Stores the sections, keys, and new key values.

    Raises
    ------
    _NumberKeyError


    """

    if len(key_arguments)%_KEY_GROUP_SIZE != 0:
        raise _NumberKeyError(key_arguments)

    pass

def _write_new_config_file(logger,
                           input_config_filename,
                           output_config_filename,
                           keys):
    """Writes to disk the new config file.

    The INI file "input_config_filename" is read and stored as
    a ConfigParser objects, obj1. The object is then modified 
    by the using the key variable. The modified object is written
    back to disk with filename "output_config_filename".

    Parameters
    ----------
    logger: A Logger object
        Used primarily for debugging and logging messages to std out.

    input_config_filename: A string
        The name of a file in INI format. This file will be read and
        stored in a ConfigParser object.

    output_config_filename: A string
        The new ConfigParser object will be named output_config_filename.

    keys: A string list of length of some multiple _KEY_GROUP_SIZE
        Each new config INI entry has group size of _KEY_GROUP_SIZE,
        therefore the number of changes to make is 

        nm_groups = len(keys)/_KEY_GROUP_SIZE. 
        
        The ip'th group entry has an offset of

        offset_ip = ip*{_KEY_GROUP_SIZE) 

        The following must be satisfied.
        keys[offset_ip] contains the name of the section.
        keys[offset_ip + 1] contains the name of the key.
        keys[offset_ip + 2] contains the new key value.
    """

    import configparser

    with open(input_config_filename,"r") as in_file:
        old_parser = configparser.ConfigParser()
        old_parser.read_file(in_file,input_config_filename)
        with open(output_config_filename,"w") as out_file:
            nm_groups = len(keys)//_KEY_GROUP_SIZE
            for ip in range(nm_groups):
                offset = ip*(_KEY_GROUP_SIZE) 
                (section,key,new_key_value)=(keys[offset],keys[offset+1],keys[offset+2])
                old_parser.set(section,key,new_key_value)
            old_parser.write(out_file)

class _Error(Exception):
    """Base class for exceptions in this module"""
    pass

class _SameIOFileError(_Error):
    """Raised when the input and output config files are the same. """

    def __init__(self,input_filename,output_filename):
        """The class constructor.
        
        Parameters
        ----------
        input_filename : str
            The input config file name.

        output_filename : str
            The output config file name.
        """

        self._input_filename=input_filename
        """str: The input config file name."""

        self._output_filename=output_filename
        """str: The output config file name."""

        self._errormessage=("On the command line, the specified input "
                            "and output config files have the same name - {}.\n".format(self._input_filename))
        """str: The message for this error."""

    @property
    def error_message(self):
        """Returns the error message.
        
        Returns
        -------
        str
           The error message string. 

        """
        return self._errormessage

class _InputConfigFileError(_Error):
    """Raised when the input config file does not exist. """

    def __init__(self,filename):
        """The class constructor

        Parameters
        ----------
        filename : str
            The name of the input config file.

        """

        self._filename = filename
        """str: The input filename"""

        self._errormessage="On the command line arguments, the specified input config file doesn't exist - {}.\n".format(self._filename)
        """str: The message for this error."""

    @property
    def error_message(self):
        """Returns the error message.
        
        Returns
        -------
        str
            The error message string. 

        """
        return self._errormessage

class _OutputConfigFileError(_Error):
    """Raised when the output config file exists. """

    def __init__(self,filename):
        """The class constructor

        Parameters
        ----------
        filename : str
            The name of the output config file.

        """

        self._filename = filename
        """str: The output filename"""

        self._errormessage="On the command, the specified output config file exists - {}.\n".format(self._filename)
        """str: The message for this error."""

    @property
    def error_message(self):
        """Returns the error message.
        
        Returns
        -------
        str
           The error message string. 

        """
        return self._errormessage

class _NumberKeyError(_Error):
    """Raised when the number of key values is not a multiple of _KEY_GROUP_SIZE """

    def __init__(self,key_args):
        """The class constructor

        Parameters
        ----------
        list of strings
            The list of key arguments.
        """
        import copy

        self._key_arguments = copy.deepcopy(key_args)
        """list of str: The key arguments."""

        self._errormessage=self._form_error_message()
        """str: The message for this error."""

    @property
    def error_message(self):
        """Returns the error message.
        
        Returns
        -------
        str
           The error message string. 

        """
        return self._errormessage

    def _form_error_message(self):
        err_msg="On the command line, the number of specified key arguments is not a multiple of _KEY_GROUP_SIZE.\n"
        err_msg+="The number of key arguments: {}.\n".format(len(self._key_arguments))
        index = -1
        for arg in self._key_arguments:
            index+=1
            err_msg+="Key argument ({}): {}\n".format(index,arg)
        return err_msg

#-----------------------------------------------------
# End of private members.                            -
#                                                    -
#-----------------------------------------------------

if __name__ == "__main__":
    main()
