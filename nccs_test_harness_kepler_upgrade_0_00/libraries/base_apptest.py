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

        if time_stamp:
            self.__master_log_files_dir = os.path.join(os.getcwd(), 'harness_log_files.' + time_stamp)
        else:
            self.__master_log_files_dir = os.path.join(os.getcwd(), 'harness_log_files')

        if not os.path.exists(self.__master_log_files_dir):
            os.mkdir(self.__master_log_files_dir)

        self.__nameOfApplication = name_of_application
        self.__name_of_subtest = name_of_subtest
        self.__threadTag = "<" + str(name_of_application) + "::" + str(name_of_subtest) + ">"
        self.__localPathToTests = local_path_to_tests
        self.__dirPathToLogFiles = os.path.join(self.__master_log_files_dir, name_of_application + "_Logfiles")
        self.__appLogFilePath = os.path.join(self.__dirPathToLogFiles, self.__nameOfApplication + ".logfile.txt")
        self.__appTestLogFilePath = os.path.join(self.__dirPathToLogFiles,
                                                 self.__nameOfApplication + "__" + self.__name_of_subtest + ".logfile.txt")

        self.__appCheckOutLogFilePathStdOut = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".appcheckout.stdout.txt")
        self.__appCheckOutLogFilePathStdErr = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".appcheckout.stderr.txt")
        self.__appTestCheckOutLogFilePathStdOut = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".testcheckout.stdout.txt")
        self.__appTestCheckOutLogFilePathStdErr = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".testcheckout.stderr.txt")
        self.__appTestUpdateSourceOutLogFilePathStdOut = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".sourceupdate.stdout.txt")
        self.__appTestUpdateSourceOutLogFilePathStdErr = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".sourceupdate.stderr.txt")
        self.__appStartTestLogFilePathStdOut = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".starttest.stdout.txt")
        self.__appStartTestLogFilePathStdErr = os.path.join(self.__dirPathToLogFiles,self.__nameOfApplication + "__" + self.__name_of_subtest + ".starttest.stderr.txt")

        if not os.path.exists(self.__dirPathToLogFiles):
            os.mkdir(self.__dirPathToLogFiles)
    
        self.__initializeLogFiles()

    def getNameOfApplication(self):
        return self.__nameOfApplication

    def getNameOfSubtest(self):
        return self.__name_of_subtest

    def getLocalPathToTests(self):
        return self.__localPathToTests

    def getDirPathToLogFiles(self):
        return self.__dirPathToLogFiles
    
    def getPathToApplicationTestLogFiles(self,test_name):
        return os.path.join(self.__dirPathToLogFiles,test_name + ".logfile.txt")

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
    
    def writeToLogFile(self,message):
        now = str(datetime.now())
        now = now.strip()
        message2 = "{0!s:<32} {1!s:<}\n".format(now, message)
        log_filehandle = open(self.__appLogFilePath,"a")
        log_filehandle.write(message2)
        log_filehandle.close()
        
    def writeToLogTestFile(self,message):
        now = str(datetime.now())
        now = now.strip()
        message2 = "{0!s:<32} Thread tag={1!s:<}  {2!s:<}\n".format(now, self.__threadTag, message)
        log_filehandle = open(self.__appTestLogFilePath,"a")
        log_filehandle.write(message2)
        log_filehandle.close()
  
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
        tmp_string = "--\n"
        tmp_string = tmp_string + "Application name: {}\n".format(str(self.__nameOfApplication))
        tmp_string = tmp_string + "Subtest name: {}\n".format(str(self.__name_of_subtest))
        tmp_string = tmp_string + "Local path to tests: {}\n".format(str(self.__localPathToTests))
        tmp_string = tmp_string + "--\n"

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
