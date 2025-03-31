#! /usr/bin/env python3

"""
This module implements the logging capability of the harness.

"""

import logging
import time
import os

class rgt_logger:

    def __init__(self,
                 logger_name,
                 fh_filepath=None,
                 logger_threshold_log_level="CRITICAL",
                 fh_threshold_log_level="CRITICAL",
                 ch_threshold_log_level="CRITICAL"):
        """ 
        Parameters
        ----------
        logger_name : str
            The name of the logger.

        logger_threshold_log_level : str
            The threshold level for the logger object.

        fh_filepath : str
            The filepath for the logger file handler.

        fh_threshold_log_level : str
            The lower bound threshold to use the file handler.

        ch_threshold_log_level : str
            The lower bound threshold to use the console handler

        """

        # Save the string threshhold levels for querying after logger is created
        self.__logger_threshold_level = logger_threshold_log_level.upper()
        self.__fh_threshold_level = fh_threshold_log_level.upper()
        self.__ch_threshold_level = ch_threshold_log_level.upper()
        # Get the numeric threshhold level for logging
        # messages.
        self.__logger_numeric_threshold_level = getattr(logging, logger_threshold_log_level.upper(), None)
        self.__fh_numeric_threshold_level = getattr(logging, fh_threshold_log_level.upper(), None)
        self.__ch_numeric_threshold_level = getattr(logging, ch_threshold_log_level.upper(), None)
        self.__filepath = fh_filepath

        # We now create the parent directories for the file handler logger.
        dirname = os.path.dirname(fh_filepath) 
        os.makedirs(dirname,exist_ok=True)

        # Instantiate the logger.
        self.__myLogger = logging.getLogger(logger_name)
        self.__myLogger.setLevel(self.__logger_numeric_threshold_level)

        # Add the file handler.
        self._add_file_handler()

        # Add the console handler.
        self._add_console_handler()

        return

    def get_logger_threshold_level(self):
        return self.__logger_threshold_level

    def get_fh_threshold_level(self):
        return self.__fh_threshold_level

    def get_ch_threshold_level(self):
        return self.__ch_threshold_level

    def doDebugLogging(self,
                      message):
        self.__myLogger.debug(message)
        return

    def doInfoLogging(self,
                      message):
        self.__myLogger.info(message)
        return

    def doWarningLogging(self,
                         message):
        self.__myLogger.warning(message)
        return

    def doErrorLogging(self,
                       message):
        self.__myLogger.error(message)
        return

    def doCriticalLogging(self,
                          message):
        self.__myLogger.critical(message)

    # Private methods
    def _add_file_handler(self):
        # Define a file handler and set to fh threshold level.
        fh = logging.FileHandler(self.__filepath)
        fh.setLevel(self.__fh_numeric_threshold_level)

        # Define the formatter for the file handler.
        my_format_string  = "-----\n"
        my_format_string += "Time: %(asctime)s\n"
        my_format_string += "Logger: %(name)s\n"
        my_format_string += "Loglevel: %(levelname)s\n"
        my_format_string += "Message:\n"
        my_format_string += "%(message)s\n"
        my_format_string += "-----\n"
        formatter = logging.Formatter(my_format_string)
        fh.setFormatter(formatter)

        # Add file handler to logger.
        self.__myLogger.addHandler(fh)

    def _add_console_handler(self):
        ch = logging.StreamHandler()
        ch.setLevel(self.__ch_numeric_threshold_level)
        self.__myLogger.addHandler(ch)
        return
