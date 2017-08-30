#! /usr/bin/env python3

"""
.. module:: rgt_logging
   :synopsis: This module implements the logging capability of the harness

.. moduleauthor:: Arnold Tharrington
"""

import logging
import time

class rgt_logger:

    def __init__(self,
                log_name,
                log_level,
                time_stamp=None):
        # Get the numeric threshhold level for logging
        # messages.
        numeric_threshold_level = getattr(logging, log_level.upper(), None)

        # Instantiate a logger that has name log_name.
        self.__myLogger = logging.getLogger(log_name)
        
        # Define the file name of the logger.
        currenttime = time.localtime()
        if time_stamp:
            timestamp =  time_stamp
        else:
            timestamp = time.strftime("%Y%b%d_%H:%M:%S",currenttime)

        self.__fileName = log_name + ".logger." + timestamp + ".txt" 

        # Define the handler and set to DEBUG threshold level.
        ch = logging.FileHandler(self.__fileName)
        ch.setLevel(logging.DEBUG)

        # Define the formatter
        my_format_string  = "-----\n"
        my_format_string += "Time: %(asctime)s\n"
        my_format_string += "Logger: %(name)s\n"
        my_format_string += "Loglevel: %(levelname)s\n"
        my_format_string += "Message:\n"
        my_format_string += "%(message)s\n"
        my_format_string += "-----\n"
        formatter = logging.Formatter(my_format_string)
        ch.setFormatter(formatter)

        self.__myLogger.setLevel(numeric_threshold_level)
        self.__myLogger.addHandler(ch)

        return

    def doInfoLogging(self,
                      message):
        self.__myLogger.info(message)
        return
