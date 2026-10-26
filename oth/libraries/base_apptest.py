#! /usr/bin/env python3

import abc
import os
from datetime import datetime

class base_apptest(object):

    """
    An abstract base class that implements the apptest interface.

    When a concrete class is instatiated, the working directory must be
    in the same directory as the "rgt.input" file location.
    """
    __metaclass__ = abc.ABCMeta

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self,
                 name_of_application,
                 name_of_subtest,
                 local_path_to_tests,
                 tag):

        self.__appName = name_of_application
        self.__testName = name_of_subtest
        self.__threadTag = "<" + str(name_of_application) + "::" + str(name_of_subtest) + ">"
        self.__localPathToTests = local_path_to_tests

    def __str__(self):
        tmp_string  = "--\n"
        tmp_string += "Application name: {}\n".format(str(self.__appName))
        tmp_string += "Subtest name: {}\n".format(str(self.__testName))
        tmp_string += "Local path to tests: {}\n".format(str(self.__localPathToTests))
        tmp_string += "--\n"
        return tmp_string

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
    def getNameOfApplication(self):
        return self.__appName

    def getNameOfSubtest(self):
        return self.__testName

    def getLocalPathToTests(self):
        return self.__localPathToTests

    def getPathToApplicationTestLogFile(self,test_name):
        return self.__appTestLogFilePath

    def getPathToAppCheckoutLogFiles(self):
        return {"stdout":self.__appCheckOutLogFilePathStdOut,
                "stderr":self.__appCheckOutLogFilePathStdErr}

    def getPathToTestCheckoutLogFiles(self):
        return {"stdout":self.__appTestCheckOutLogFilePathStdOut,
                "stderr":self.__appTestCheckOutLogFilePathStdErr}

    def getPathToSourceUpdateLogFiles(self):
        return {"stdout":self.__appTestUpdateSourceOutLogFilePathStdOut,
                "stderr":self.__appTestUpdateSourceOutLogFilePathStdErr}

    def getPathToStartTestLogFiles(self):
        return {"stdout":self.__appStartTestLogFilePathStdOut,
                "stderr":self.__appStartTestLogFilePathStdErr}


    @property
    @abc.abstractmethod
    def logger(self):
        return

    @abc.abstractmethod
    def doTasks(self,myTasks,myTestCheckoutLock):
        return

    @abc.abstractmethod
    def check_out_test(self):
        return

    @abc.abstractmethod
    def display_status(self):
        return

    @abc.abstractmethod
    def generateReport(self,logfile,taskwords,mycomputer_with_events_record):
        return

    @abc.abstractmethod
    def debug_apptest(self):
        return

    @abc.abstractmethod
    def waitForAllJobsToCompleteQueue(self):
        return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Private methods.                                                @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    @abc.abstractmethod
    def _start_test(self):
        return

    @abc.abstractmethod
    def _stop_test(self):
        return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods.                                         @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class BaseApptestError(Exception):
    """The base error class for this module."""

    @property
    @abc.abstractmethod
    def message(self):
        return

