#! /usr/bin/env python3

from abc import ABC, abstractmethod, ABCMeta
import os
from datetime import datetime

class BaseDBLogger(ABC):

    """
    An abstract base class that implements the database logging interface.
    """
    __metaclass__ = ABCMeta

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self):
        return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of special methods                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


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

# Raised when there is an initialization error
class DatabaseInitError(Exception):
    """The base error class for this module."""
    def __init__(self,
                 message,
                 args):
        self.__message = message
        self.__args = args
        return

    @property
    def message(self):
        return self.__message

# Raised when there is an data error
class DatabaseDataError(Exception):
    """The base error class for this module."""
    def __init__(self,
                 message,
                 args):
        self.__message = message
        self.__args = args
        return

    @property
    def message(self):
        return self.__message

# Raised when there is an environment variable-related error
class DatabaseEnvironmentError(Exception):
    """The base error class for this module."""
    def __init__(self,
                 message,
                 args):
        self.__message = message
        self.__args = args
        return

    @property
    def message(self):
        return self.__message
