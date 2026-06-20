#! /usr/bin/env python3

"""
This module implements the logging capability of the harness.

"""

import logging
import time
import os
import inspect

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

        # Create log file dir if file path is non-empty and a path (not just a filename)
        if self.__filepath and len(self.__filepath) > 0 and '/' in self.__filepath:
            # We now create the parent directories for the file handler logger.
            dirname = os.path.dirname(self.__filepath) 
            os.makedirs(dirname,exist_ok=True)

        # Instantiate the logger.
        self.__myLogger = logging.getLogger(logger_name)

        # Check for existing logger of the same name
        if self.__myLogger.hasHandlers():
            self.doInfoLogging("Found existing handlers for logger name {logger_name}. Not adding more handlers, will using the existing logger.")
            return

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

    def getLocation(self, message):
        if message != "" and self.get_logger_threshold_level() == "DEBUG":
            loc=""
            stack = inspect.stack()
            # Step up stack until we are out of the logging bits
            i = 2
            while stack[i][3] == stack[1][3] and i < len(stack):
                i += 1
            loc = "In function " + stack[i][3] + ": " + message
            return loc
        else:
            return message

    def doDebugLogging(self,
                      message):
        self.__myLogger.debug(self.getLocation(message))
        return

    def doInfoLogging(self,
                      message):
        self.__myLogger.info(self.getLocation(message))
        return

    def doWarningLogging(self,
                         message):
        self.__myLogger.warning(self.getLocation(message))
        return

    def doErrorLogging(self,
                       message):
        self.__myLogger.error(self.getLocation(message))
        return

    def doCriticalLogging(self,
                          message):
        self.__myLogger.critical(self.getLocation(message))

    # Private methods
    def _add_file_handler(self):
        # if no file path provided, skip
        if not self.__filepath or len(self.__filepath) == 0:
            return

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
