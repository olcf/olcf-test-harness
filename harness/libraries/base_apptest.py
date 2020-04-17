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

    def __init__(self,
                 name_of_application,
                 name_of_subtest,
                 local_path_to_tests,
                 time_stamp=None):

        self.__appName = name_of_application
        self.__testName = name_of_subtest
        self.__threadTag = "<" + str(name_of_application) + "::" + str(name_of_subtest) + ">"
        self.__localPathToTests = local_path_to_tests

        # Create harness log directories
        logdir_name = 'harness_log_files'
        if time_stamp:
            logdir_name += '.' + time_stamp
        self.__dirPathToLogFiles = os.path.join(os.getcwd(), logdir_name)
        if not os.path.exists(self.__dirPathToLogFiles):
            os.mkdir(self.__dirPathToLogFiles)

        self.__appLogFileBaseDir = os.path.join(self.__dirPathToLogFiles, self.__appName)
        if not os.path.exists(self.__appLogFileBaseDir):
            os.mkdir(self.__appLogFileBaseDir)

        self.__appTestLogFileBaseDir = os.path.join(self.__dirPathToLogFiles, self.__appName, self.__testName)
        if not os.path.exists(self.__appTestLogFileBaseDir):
            os.mkdir(self.__appTestLogFileBaseDir)

        # Set harness log file names
        self.__appLogFilePathBase = os.path.join(self.__appLogFileBaseDir, self.__appName)
        self.__appTestLogFilePathBase = os.path.join(self.__appTestLogFileBaseDir, self.__appName + '__' + self.__testName)

        self.__appLogFilePath = self.__appLogFilePathBase + ".logfile.txt"
        self.__appTestLogFilePath = self.__appTestLogFilePathBase + ".logfile.txt"
        self.__appCheckOutLogFilePathStdOut = self.__appTestLogFilePathBase + ".appcheckout.stdout.txt"
        self.__appCheckOutLogFilePathStdErr = self.__appTestLogFilePathBase + ".appcheckout.stderr.txt"
        self.__appTestCheckOutLogFilePathStdOut = self.__appTestLogFilePathBase + ".testcheckout.stdout.txt"
        self.__appTestCheckOutLogFilePathStdErr = self.__appTestLogFilePathBase + ".testcheckout.stderr.txt"
        self.__appTestUpdateSourceOutLogFilePathStdOut = self.__appTestLogFilePathBase + ".sourceupdate.stdout.txt"
        self.__appTestUpdateSourceOutLogFilePathStdErr = self.__appTestLogFilePathBase + ".sourceupdate.stderr.txt"
        self.__appStartTestLogFilePathStdOut = self.__appTestLogFilePathBase + ".starttest.stdout.txt"
        self.__appStartTestLogFilePathStdErr = self.__appTestLogFilePathBase + ".starttest.stderr.txt"

        self.__initializeLogFiles()

    def getNameOfApplication(self):
        return self.__appName

    def getNameOfSubtest(self):
        return self.__testName

    def getLocalPathToTests(self):
        return self.__localPathToTests

    def getDirPathToLogFiles(self):
        return self.__dirPathToLogFiles
    
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
    
    # def writeToLogFile(self,
    #                    message):
    #     now = str(datetime.now())
    #     now = now.strip()
    #     message2 = "{0!s:<32} {1!s:<}\n".format(now, message)
    #     log_filehandle = open(self.__appLogFilePath,"a")
    #     log_filehandle.write(message2)
    #     log_filehandle.close()
    #     
    # def writeToLogTestFile(self,message):
    #     now = str(datetime.now())
    #     now = now.strip()
    #     message2 = "{0!s:<32} Thread tag={1!s:<}  {2!s:<}\n".format(now, self.__threadTag, message)
    #     log_filehandle = open(self.__appTestLogFilePath,"a")
    #     log_filehandle.write(message2)
    #     log_filehandle.close()
  
    @abc.abstractmethod
    def doTasks(self,myTasks,myTestCheckoutLock):
        return
    
    @abc.abstractmethod
    def appTestName(self):
        return

    @abc.abstractmethod
    def check_out_test(self):
        return

    @abc.abstractmethod
    def start_test(self):
        return

    @abc.abstractmethod
    def stop_test(self):
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


    #-----------------------------------------------------
    # Special methods                                    -
    #                                                    -
    #-----------------------------------------------------
    def __str__(self):
        tmp_string  = "--\n"
        tmp_string += "Application name: {}\n".format(str(self.__appName))
        tmp_string += "Subtest name: {}\n".format(str(self.__testName))
        tmp_string += "Local path to tests: {}\n".format(str(self.__localPathToTests))
        tmp_string += "--\n"

        return tmp_string


    #-----------------------------------------------------
    # Private methods                                    -
    #                                                    -
    #-----------------------------------------------------  
    def __initializeLogFiles(self):
        file_handle = open(self.__appLogFilePath,"a")
        file_handle.close()
        
        file_handle = open(self.__appTestLogFilePath,"a")
        file_handle.close()

    def __absolutePathToStdOut(self):
        pass
