#! /usr/bin/env python

""" 
.. module:: threadedDecorator
   :synopsis: This module implements a thread decorator for base_apptest objects.

.. moduleauthor:: Arnold Tharrington
 
"""

import threading
import subprocess
import multiprocessing
import time
from datetime import datetime
from libraries.apptest import subtest
from libraries import apptest
from libraries.base_apptest import base_apptest
import abc
import copy
import random
import sys
import os
from Queue import *


class BaseAppThreadDecorator(threading.Thread,base_apptest):
    """
    An abstract base class that implements the "application" concurrency interface.


    This class inherents from the "threading.Thread" and "base_apptest" classes.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):

        threading.Thread.__init__(self)

    @abc.abstractmethod
    def run(self):
        return

    @abc.abstractmethod
    def doTasks(self,myTasks):
        return

class ThreadDecorator(BaseAppThreadDecorator):
    """
    When this class is instatiated, the working directory must be 
    in the same directory as the "rgt.input" file location. This
    class instantiates a "python" thread over an application. Each
    application contains tests on which tasks are done on. Each test
    is threaded with the "multiprocessing.Process" thread. Each 
    multiprocessing.Process test thread does the tasks on the on the
    test.

    :param string name_of_application: The name of the application.
    :param name_of_subtest: List of the application tests.
    :type name_of_subtest: List of strings
    :param integer number_of_iterations: The number of iterations to run the 
                                         harness application/subtest.
    :param tasks: The harness tasks the application/subtest will perform. 
    :type tasks: A list of strings

    """
    
    
    MAX_APP_THREADS = 10
    """ The maximum number of python threads over the applications"""
    
    app_semaphore = threading.Semaphore(MAX_APP_THREADS)
    """
    A threading locking semaphore that restricts to running
    at most MAX_APP_THREADS concurrently.
    """
   
    MAX_APPTEST_PROCESS_THREADS = 32
    """ 
    The maximum number of python process threads over
    all applications subtests.
    """

    apptest_semaphore = multiprocessing.Semaphore(MAX_APPTEST_PROCESS_THREADS)
    """
    A multiprocessing threading locking semaphore that restricts to running
    at most MAX_APPTEST_PROCESS_THREADS concurrently.
    """

    def __init__(self,name_of_application=None,
                      name_of_subtest=None,
                      local_path_to_tests=None,
                      number_of_iterations=None,
                      tasks=None):

        BaseAppThreadDecorator.__init__(self)

        self.__nameOfApplication = copy.deepcopy(name_of_application)
        self.__nameOfApplicationTests = copy.deepcopy(name_of_subtest)
        self.__pathToApplicationTests = copy.deepcopy(local_path_to_tests)
        self.__numberIterations = -1
        self.__harnessTasks = copy.deepcopy(tasks)
        if tasks:
            self.__harnessTasks = apptest.subtest.reorderTaskList(self.__harnessTasks)


        
        self.__applicationTests = []
        self.__testQueue = Queue()

        for name_of_test in self.__nameOfApplicationTests:
            #Instantiate the application tests.
            self.__applicationTests  = self.__applicationTests + [apptest.subtest(name_of_application=self.__nameOfApplication,
                                                                  name_of_subtest=name_of_test,
                                                                  local_path_to_tests=self.__pathToApplicationTests,
                                                                  number_of_iterations=self.__numberIterations) ]

    #-----------------------------------------------------
    # Public Methods                                     -
    #                                                    -
    #-----------------------------------------------------
    def run(self):

        # Acquire a application semaphore lock.
        ThreadDecorator.app_semaphore.acquire()

        tmp_string = "Starting thread of application {application1}".format(application1=self.__nameOfApplication)
        self.__writeToLogFile(tmp_string)
        
        self.__fillApplicationTestQueue()
          
        # The application source checkout must be performed first,
        # then all other harnes tasks may proceed.
        if subtest.checkout in self.__harnessTasks:
            self.__checkoutApplicationSource()

        #Start the application tests.
        number_tests = self.__testQueue.qsize()
        application_test_processes = [None for x in range(number_tests)]
        self.__startApplicationTests(application_test_processes)

        self.__waitForApplicationTestsToFinishStarting(application_test_processes)

        tmp_string = "Ending thread of application {application1}".format(application1=self.__nameOfApplication)
        self.__writeToLogFile(tmp_string)
        
        # Release the application lock semaphore.
        ThreadDecorator.app_semaphore.release()

        return


    def doTasks(self,tasks=None):
        """
        Starts the tasks on the application and its tests.

        :param tasks: A list of strings that contain the test tasks.
        :type tasks: List of strings.

        """

        if tasks != None:
            self.__harnessTasks = copy.deepcopy(tasks)
            self.__harnessTasks = apptest.subtest.reorderTaskList(self.__harnessTasks)
        self.start()


    def appTestName(self):
        return self.__myApp.appTestName()


    def getNameOfApplication(self):
        return self.__nameOfApplication
 

    #----------------------------------------
    #--These functions need to be threaded. -
    #----------------------------------------
    def check_out_test(self):
        self.__myApp.check_out_test()


    def start_test(self,my_tasks):
        self.__myApp.start_test()


    def stop_test(self):
        self.__myApp.stop_test()


    def debug_apptest(self):
        self.__myApp.debug_apptest()


    def display_status(self):
        self.__myApp.display_status()


    def generateReport(self):
        self.__myApp.generateReport()


    #-----------------------------------------------------
    # Private Methods                                    -
    #                                                    -
    #-----------------------------------------------------

        
    def __fillApplicationTestQueue(self):
        """
        This function does 2 things: Fills the application test queue and
        if unable raises an exception and release the application locking 
        semaphore.
        """
        name_of_application = self.__nameOfApplication
        for job in self.__applicationTests:
            test_name = job.getTestName()
            try:
                self.__testQueue.put(copy.deepcopy(job),block=True)  
                tmpstring = "Inserted application '{}', test '{}' into the queue.".format(name_of_application,test_name)
                self.__writeToLogFile(tmpstring)           
            except Exception:
                tmp_string = "Error in Filling Application test queue in {application1}".format(application1=name_of_application)
                self.__writeToLogFile(tmp_string)
                tmp_string = "Ending python thread of application {application1}".format(application1=name_of_application)
                self.__writeToLogFile(tmp_string)
                ThreadDecorator.app_semaphore.release()
                raise
 

    def __checkoutApplicationSource(self):
        try:
            job = copy.deepcopy(self.__applicationTests[0])
            tmp_string = "In __checkoutApplicationSource job is {}".format(str(job))
            self.__writeToLogFile(tmp_string)
            tmp_string = "Current directory is {}".format(os.getcwd())
            self.__writeToLogFile(tmp_string)
            
            if subtest.checkout in self.__harnessTasks:
                job.check_out_source()
                tmp_string = "Checked out the source of application {application1}".format(application1=self.__nameOfApplication)
                self.__writeToLogFile(tmp_string)
        except Exception as exc:
                tmp_string = "Failed to checkout the source of application {application1}".format(application1=self.__nameOfApplication)
                self.__writeToLogFile(tmp_string)
                tmp_string = "Ending python thread of application {application1}".format(application1=self.__nameOfApplication)
                self.__writeToLogFile(tmp_string)
                ThreadDecorator.app_semaphore.release()
                raise
        except subprocess.CalledProcessError as exc:
                tmp_string = "Caught exception 'CalledProcessError' {application1}".format(application1=self.__nameOfApplication)
                self.__writeToLogFile(tmp_string)
                ThreadDecorator.app_semaphore.release()
                raise
 
    def __startApplicationTests(self,application_test_processes):
        test_index = 0

        while True:
            if self.__testQueue.empty() == True:  
                tmp_string =  "The test queue is empty for application {}!".format(self.__nameOfApplication)   
                self.__writeToLogFile(tmp_string)
                break
            else:
                try:
                    job = self.__testQueue.get(block=True)
                    try:
                        ThreadDecorator.apptest_semaphore.acquire()
                        application_test_processes[test_index] = ProcessAppTest(job,self.__harnessTasks)
                        application_test_processes[test_index].start()  
                        tmp_string =  "Started tasks on job {}".format(job.appTestName())
                        self.__writeToLogFile(tmp_string)
                    except:
                        tmp_string =  "Failed to perform tasks on job {}".format(job.appTestName())
                        self.__writeToLogFile(tmp_string)
                        ThreadDecorator.apptest_semaphore.release()
                        raise
                    test_index = test_index + 1
                except Exception:
                    tmp_string =  "Failed to get job from Queue"
                    self.__writeToLogFile(tmp_string)
                    tmp_string = "Ending python thread of application {application1}".format(application1=self.__nameOfApplication)
                    self.__writeToLogFile(tmp_string)
                    raise


    def __waitForApplicationTestsToFinishStarting(self,application_test_processes):
        TEST_PROCESSS_IS_DEAD = 0
        TEST_PROCESS_IS_ALIVE = 1
        number_test_processes = len(application_test_processes)
        plist = [ TEST_PROCESS_IS_ALIVE for x in range(number_test_processes)]
        while True:
            
            time.sleep(5)
            
            number_alive_test_processes = 0
            
            for ip in range(number_test_processes):
                [application_name,test_name] = application_test_processes[ip].getApplicationTestName()
                if plist[ip] == TEST_PROCESS_IS_ALIVE:
                    if application_test_processes[ip].is_alive():
                        number_alive_test_processes = number_alive_test_processes + 1
                    else:
                        plist[ip] = TEST_PROCESSS_IS_DEAD
                        message = "The python process for application {application1} test {test1} has completed.".format(application1=application_name,
                                                                                                                         test1=test_name)
                        self.__writeToLogFile(message)
                        ThreadDecorator.apptest_semaphore.release()
                    
            if number_alive_test_processes <= 0:
                break     


    def __writeToLogFile(self,message):
        self.__applicationTests[0].writeToLogFile(message)


class ProcessAppTest(multiprocessing.Process):
    test_checkout_lock = multiprocessing.Lock()
    test_display_lock = multiprocessing.Lock()
    def __init__(self,my_job,my_tasks=None):
        multiprocessing.Process.__init__(self)
        self.__job = copy.deepcopy(my_job)
        self.__harnessTasks = copy.deepcopy(my_tasks)

    def run(self):
        self.__job.doTasks(self.__harnessTasks,
                           test_checkout_lock=ProcessAppTest.test_checkout_lock,
                           test_display_lock=ProcessAppTest.test_display_lock)

    def getApplicationTestName(self):
        return self.__job.appTestName()
        
