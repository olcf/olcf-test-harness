#! /usr/bin/env python3

from abc import ABC, abstractmethod, ABCMeta
import os
from datetime import datetime
import re

class BaseDBLogger(ABC):

    """
    An abstract base class that implements the database logging interface.
    """
    __metaclass__ = ABCMeta


    def __init__(self):
        # Import the othctl_runtime_config for all DB implementations to use
        from oth.config import othctl_runtime_config
        self.othctl_runtime_config = othctl_runtime_config

        # Define what string to use if no value present, matches StatusFile.NO_VALUE
        self.NO_VALUE = '[NO_VALUE]'
        return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # The name of the dot-file that disables this backend
    @property
    @abstractmethod
    def disable_file_name(self):
        return

    # This environment variable name set to 1 disables this backend
    @property
    @abstractmethod
    def disable_envvar_name(self):
        return

    # The name of the dot-file that indicates successful, completed logging
    @property
    @abstractmethod
    def successful_file_name(self):
        return

    @property
    @abstractmethod
    def name(self):
        return

    @abstractmethod
    def send_event(self, event_dict : dict):
        return

    @abstractmethod
    def send_metrics(self, test_info_dict : dict, metrics_dict : dict):
        return

    @abstractmethod
    def send_node_health_results(self, test_info_dict : dict, node_health_dict : dict):
        return

    @abstractmethod
    def send_external_metrics(self, table : str, tags : dict, values : dict, log_time : str):
        return

    @abstractmethod
    def is_alive(self):
        return

    @abstractmethod
    def query(self, query):
        return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def _is_numeric(self, s : str):
        """ Checks if a string is an OTH-recognized numeric format """
        number_regex = re.compile(r'^[-]?([0-9]*\.)?[0-9]+([eE]{1}[+-]?[0-9]+)?$')
        if number_regex.match(s):
            return True
        else:
            return False

