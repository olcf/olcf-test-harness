#! /usr/bin/env python3

""" The apptest module encapsulates the application-test directory structure layout.

"""

# Python package imports
import subprocess
import shlex
import time
from datetime import datetime
import os
import sys
import copy
import re
from types import *

# NCCS Test Harness Package Imports
from libraries.base_apptest import base_apptest
from libraries.base_apptest import BaseApptestError
from libraries.layout_of_apps_directory import apptest_layout
from libraries.status_file import parse_status_file
from libraries.status_file import parse_status_file2
from libraries.status_file import summarize_status_file
from libraries.status_file import StatusFile
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command_return_exitstatus
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command_return_stdout_stderr_exitstatus

from libraries.rgt_database_loggers.rgt_database_logger_factory import create_rgt_db_logger

#
# Inherits "apptest_layout".
#
class subtest(base_apptest, apptest_layout):
    """Encapsulates the application-test layout.

    Only one method is public and it exposes the doing of harness tasks:
        * do_tasks.

    The class is derived from classes base_apptest and apptest_layout.


    """

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self,
                 name_of_application=None,
                 name_of_subtest=None,
                 local_path_to_tests=None,
                 number_of_iterations=-1,
                 logger=None,
                 tag=None):

        # Ensure that tag is not None.
        if (tag == None):
            keywords = {"timestamp" : tag}
            message = "The argument tag must not be None."
            raise ApptestImproperInstantiationError(message,keywords)

        base_apptest.__init__(self,
                              name_of_application,
                              name_of_subtest,
                              local_path_to_tests,
                              tag)

        apptest_layout.__init__(self,
                                local_path_to_tests,
                                name_of_application,
                                name_of_subtest,
                                logger=logger,
                                harness_id=tag)

        # Format of data is [<local_path_to_tests>, <application>, <test>]
        self.__apps_test_checked_out = []
        self.__apps_test_checked_out.append([self.getLocalPathToTests(),
                                             self.getNameOfApplication(),
                                             name_of_subtest])
        self.__number_of_iterations = -1
        self.__myLogger = logger

        self.__db_logger = create_rgt_db_logger(logger=logger)

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

    @property
    def logger(self):
        """logger: Returns the logger of the subtest class. """
        return self.__myLogger

    def doTasks(self,
                launchid=None,
                tasks=None,
                test_checkout_lock=None,
                test_display_lock=None,
                stdout_stderr=None,
                separate_build_stdio=False):
        """
        :param list_of_string my_tasks: A list of the strings
                                        where each element is an application
                                        harness task to be preformed on this app/test
        """

        from libraries.regression_test import Harness

        if tasks != None:
            tasks = copy.deepcopy(tasks)
            tasks = subtest.reorderTaskList(tasks)

        message = "In {app1}  {test1} doing {task1}".format(app1=self.getNameOfApplication(),
                                                                test1=self.getNameOfSubtest(),
                                                                task1=tasks)
        self.doInfoLogging(message)

        for harness_task in tasks:
            if harness_task == Harness.checkout:
                if test_checkout_lock:
                    test_checkout_lock.acquire()

                from libraries.repositories import RepositoryFactory

                repository_type = RepositoryFactory.get_type_of_repository()
                name_of_application = self.getNameOfApplication()
                url_to_remote_repsitory_application = RepositoryFactory.get_repository_url_of_application(name_of_application)
                my_repository_branch = RepositoryFactory.get_repository_git_branch()

                my_repository = RepositoryFactory.create(repository_type,
                                                         url_to_remote_repsitory_application,
                                                         my_repository_branch)

                self.doInfoLogging("Start of cloning repository")
                destination = self.getLocalPathToTests()

                exit_code = self.cloneRepository(my_repository,
                                     destination)

                self.doInfoLogging("End of cloning repository")

                if test_checkout_lock:
                    test_checkout_lock.release()

                if exit_code:
                    return 1

            else:
                if not self.check_paths():
                    self.logger.doErrorLogging(f"Aborting task {harness_task}. Could not find all required paths.")
                    message = "Could not find all required paths on the file system for application {app1}, test {test1}.".format(app1=self.getNameOfApplication(),
                                                                                                                                test1=self.getNameOfSubtest())
                    return 1
                if harness_task == Harness.starttest:
                    message = "Start of starting test."
                    self.doInfoLogging(message)

                    exit_code = self._start_test(launchid, stdout_stderr, separate_build_stdio=separate_build_stdio)

                    message = "End of starting test"
                    self.doInfoLogging(message)

                    if exit_code:
                        return 1

                elif harness_task == Harness.stoptest:
                    self._stop_test()

                elif harness_task == Harness.displaystatus:
                    if test_display_lock:
                        test_display_lock.acquire()

                    self.display_status()

                    if test_display_lock:
                        test_display_lock.release()

                elif harness_task == Harness.summarize_results:
                    self.generateReport()

    def cloneRepository(self,my_repository,destination):
        #Get the current working directory.
        cwd = os.getcwd()

        message = "For the cloning, my current directory is " + cwd
        self.doInfoLogging(message)

        my_repository.cloneRepository(destination,
                                      self.__myLogger)

        exit_status = 0

        if exit_status > 0:
            string1 = "Cloning of repository failed."
            self.doCriticalLogging(string1)
            return 1
        else:
            message = "Cloning of repository passed"
            self.doInfoLogging(message)

        return 0

    #
    # Displays the status of the tests.
    #
    def display_status(self):
        failed_jobs = []
        log_message = "Testing status of: " + self.getNameOfApplication() + self.getNameOfSubtest()
        print(log_message)

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        (self.__status,failed_jobs) = parse_status_file2(path_to_status_file)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        appname = "%s, %s\n" % (self.getNameOfApplication(), self.getNameOfSubtest())
        w1 = "Warning: No tests passed!!\n"
        s1 = "%20s %20s %20s %20s\n" % ("Total tests","Test passed", "Test failed", "Test inconclusive")
        s2 = "%20s %20s %20s %20s\n" % (str(self.__status["number_of_tests"]),
                                        str(self.__status["number_of_passed_tests"]),
                                        str(self.__status["number_of_failed_tests"]),
                                        str(self.__status["number_of_inconclusive_tests"])
                                       )
        bheader = "\n====================\n"

        filename= apptest_layout.test_status_filename
        dfile_obj = open(filename,"a")
        dfile_obj.write(theader)
        dfile_obj.write(time1)
        dfile_obj.write(appname)
        dfile_obj.write(s1)
        dfile_obj.write(s2)
        dfile_obj.write(bheader)
        dfile_obj.close()

        efile_obj = open("failed_jobs.txt","a")
        efile_obj.write(theader)
        efile_obj.write(time1)
        efile_obj.write(appname)
        for job in failed_jobs:
            s3 = "%20s %20s %20s\n" % (job[0],job[1],job[2])
            efile_obj.write(s3)
        efile_obj.write(bheader)
        efile_obj.close()

    #
    # Displays the status of the tests.
    #
    def display_status2(self,taskwords,mycomputer_with_events_record):
        failed_jobs = []
        log_message =  "Testing status of: " + self.getNameOfApplication() +self.getNameOfSubtest()
        print(log_message)

        starttimestring = taskwords[0]
        starttimestring = starttimestring.strip()
        starttimewords = starttimestring.split("_")
        startdate = datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        log_message =  "The startdate is " + startdate.ctime()
        print (log_message)

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
                                      int(endtimewords[3]),int(endtimewords[4]))
        log_message = "The enddate is " + enddate.ctime()
        print(log_message)

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        (self.__status,failed_jobs) = parse_status_file(path_to_status_file,startdate,enddate,mycomputer_with_events_record)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        appname = "%s, %s\n" % (self.getNameOfApplication(), self.getNameOfSubtest())
        w1 = "Warning: No tests passed!!\n"
        s1 = "%20s %20s %20s %20s\n" % ("Total tests","Test passed", "Test failed", "Test inconclusive")
        s2 = "%20s %20s %20s %20s\n" % (str(self.__status["number_of_tests"]),
                                        str(self.__status["number_of_passed_tests"]),
                                        str(self.__status["number_of_failed_tests"]),
                                        str(self.__status["number_of_inconclusive_tests"])
                                       )
        bheader = "\n====================\n"


        filename= apptest_layout.test_status_filename
        dfile_obj = open(filename,"a")
        dfile_obj.write(theader)
        dfile_obj.write(time1)
        dfile_obj.write(appname)
        dfile_obj.write(s1)
        dfile_obj.write(s2)
        dfile_obj.write(bheader)
        dfile_obj.close()

        efile_obj = open("failed_jobs.txt","a")
        efile_obj.write(theader)
        efile_obj.write(time1)
        efile_obj.write(appname)
        for job in failed_jobs:
            s3 = "%20s %20s %20s\n" % (job[0],job[1],job[2])
            efile_obj.write(s3)
        efile_obj.write(bheader)
        efile_obj.close()


    def generateReport(self,logfile,taskwords):
        #Parse the status file.

        starttimestring = taskwords[0]
        starttimestring = starttimestring.strip()
        starttimewords = starttimestring.split("_")
        startdate = datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        log_message = "The startdate is " + startdate.ctime()
        print(log_message)

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
                                      int(endtimewords[3]),int(endtimewords[4]))
        log_message = "The enddate is " + enddate.ctime()
        print(log_message)

        #Parse the status file.
        path_to_status_file = self.get_path_to_status_file()
        self.__summary = summarize_status_file(path_to_status_file,startdate,enddate,mycomputer_with_events_record)

        currenttime = time.localtime()
        time1 = time.strftime("%Y %b %d %H:%M:%S\n",currenttime)
        theader = "\n--------------------\n"
        fieldheader = "{leading_space:41s} {attempts:10s} {passes:10s} {fails:10s} {inconclusive:10s}\n".format(leading_space="",
                                                                                attempts="Attemps",
                                                                                passes="Passed",
                                                                                fails="Failures",
                                                                                inconclusive="Inconclusive")

        appname = "{app:20s} {test:20s} ".format(app=self.getNameOfApplication(), test=self.getNameOfSubtest())
        results = "{attempts:10s} {passes:10s} {failures:10s} {inconclusive:10s}".format(
                                          attempts=str(self.__summary["number_of_tests"]),
                                          passes=str(self.__summary["number_of_passed_tests"]),
                                          failures=str(self.__summary["number_of_failed_tests"]),
                                          inconclusive=str(self.__summary["number_of_inconclusive_tests"]))

        bheader = "\n====================\n"


        dfile_obj = open(logfile,"a")
        dfile_obj.write(theader)
        dfile_obj.write(fieldheader)
        dfile_obj.write(appname)
        dfile_obj.write(results)
        dfile_obj.write(bheader)
        dfile_obj.close()

        flag_test_has_passes = False
        if self.__summary["number_of_failed_tests"] >= 0:
            flag_test_has_passes = True

        return {"Test_has_at_least_1_pass" : flag_test_has_passes,
                "Number_attemps" : self.__summary["number_of_tests"],
                "Number_passed" : self.__summary["number_of_passed_tests"],
                "Number_failed" : self.__summary["number_of_failed_tests"],
                "Number_inconclusive" : self.__summary["number_of_inconclusive_tests"],
                "Failed_jobs" : self.__summary["failed_jobs"],
                "Inconclusive_jobs" : self.__summary["inconclusive_jobs"]}


    #
    # Debug apptest.
    #
    def debug_apptest(self):
        print ("\n\n")
        print ("================================================================")
        print ("Debugging apptest ")
        print ("================================================================")
        for tmp_test in self.__apps_test_checked_out:
            print( "%-20s  %-20s %-20s" % (tmp_test[0], tmp_test[1], tmp_test[2]))
        print( "================================================================\n\n")

    @classmethod
    def reorderTaskList(cls,tasks):
        from libraries.regression_test import Harness
        taskwords1 = []
        for taskwords in tasks:
            task = None
            if type(taskwords) == list:
                task = taskwords[0]
            else:
                task = taskwords
            taskwords1 = taskwords1 + [task]

        app_tasks1 = []

        if (Harness.checkout in taskwords1):
            app_tasks1.append(Harness.checkout)
            taskwords1.remove(Harness.checkout)

        if (Harness.starttest in taskwords1) :
            app_tasks1.append(Harness.starttest)
            taskwords1.remove(Harness.starttest)

        if (Harness.stoptest in taskwords1):
            app_tasks1.append(Harness.stoptest)
            taskwords1.remove(Harness.stoptest)

        if (Harness.displaystatus in taskwords1):
            app_tasks1.append(Harness.displaystatus)
            taskwords1.remove(Harness.displaystatus)

        if (Harness.summarize_results in taskwords1):
            app_tasks1.append(Harness.summarize_results)
            taskwords1.remove(Harness.summarize_results)

        return app_tasks1

    def doInfoLogging(self,message):
        if self.__myLogger:
            self.__myLogger.doInfoLogging(message)

    def doCriticalLogging(self,message):
        if self.__myLogger:
            self.__myLogger.doCriticalLogging(message)

    def waitForAllJobsToCompleteQueue(self, harness_config, timeout):
        """Waits for subtest cycle to end.

        A subtest cycle is the build, submit to job scheduler, and the
        completion of the subtest in the scheduler.

        Parameters
        ----------
        timeout : int
            The maximum time to wait in minutes till the subtest cycle is complete.

        Returns
        -------
        None

        """

        from machine_types.machine_factory import MachineFactory

        # Set the time counters and other flags for ensuring a maximum
        # wait time while checking completion of the test cycle.
        time_between_checks = 5.0
        timeout_secs = timeout*60.0
        elapsed_time = 0.0

        # Print an informational message on the maximum wait time.
        message  = 'Waiting for all {} : {} tests to complete the testing cycle.\n'.format(self.getNameOfApplication(),self.getNameOfSubtest())
        message += 'The maximum wait time is {}.\n'.format(str(timeout_secs))
        message += 'The time between checks is {}.\n'.format(str(time_between_checks))
        self.logger.doInfoLogging(message)

        # Instantiate the machine for this computer.
        mymachine = MachineFactory.create_machine(harness_config, self)

        continue_checking = True
        start_time = datetime.now()
        while continue_checking:
            time.sleep(time_between_checks)
            elapsed_time = datetime.now() - start_time
            message = 'Checking for subtest cycle completion at {} seconds.\n'.format(str(elapsed_time))
            self.logger.doInfoLogging(message)

            if mymachine.isTestCycleComplete(self):
               continue_checking = False
               break

            elapsed_time = datetime.now() - start_time
            if elapsed_time.total_seconds() > timeout_secs:
                continue_checking = False
                message_elapsed_time = 'After {} seconds the testing cycle has exceeded the maximum wait time.\n'.format(str(elapsed_time))
                self.logger.doWarningLogging(message_elapsed_time)

        return

    def did_all_tests_pass(self, harness_config):
        from machine_types.machine_factory import MachineFactory
        from libraries.status_file_factory import StatusFileFactory

        # Instantiate the machine for this computer.
        mymachine = MachineFactory.create_machine(harness_config, self)

        ret_val = mymachine.did_all_tests_pass(self)

        return ret_val

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
    def _start_test(self,
                    launchid,
                    stdout_stderr,
                    separate_build_stdio=False):

        # If the file kill file exits then remove it.
        pathtokillfile = self.get_path_to_kill_file()
        if os.path.lexists(pathtokillfile):
            os.remove(pathtokillfile)

        # This will automatically build & submit
        starttestcomand = f"test_harness_driver.py -r -l {launchid} --loglevel {self.logger.get_ch_threshold_level()}"
        if separate_build_stdio:
            starttestcomand += "--separate-build-stdio"

        pathtoscripts = self.get_path_to_scripts()

        if stdout_stderr == "logfile":
            (stdout,stderr,exit_status) = \
            run_as_subprocess_command_return_stdout_stderr_exitstatus(starttestcomand,
                                                                      command_execution_directory=pathtoscripts)
        elif stdout_stderr == "screen":
            (stdout,stderr,exit_status) = \
            run_as_subprocess_command_return_exitstatus(starttestcomand,
                                                        command_execution_directory=pathtoscripts)
        if exit_status > 0:
            message = ( "In function {function_name} we have a critical error.\n"
                        "The command '{cmd}' has exited with a failure.\n"
                        "The exit return value is {value}\n.").format(function_name=self.__name_of_current_function(), cmd=starttestcomand,value=exit_status)
            self.doCriticalLogging(message)

            string1 = "Command failed: " + starttestcomand
            return 1
        else:
            message =  "In function {function_name}, the command '{cmd}' has executed sucessfully.\n".format(function_name=self.__name_of_current_function(),cmd=starttestcomand)
            message += "stdout of command : {}\n".format(stdout)
            message += "stderr of command : {}\n".format(stderr)
            self.doInfoLogging(message)

    def _stop_test(self):
        pathtokillfile = self.get_path_to_kill_file()
        with open(pathtokillfile,"w") as kill_file:
            kill_file.write("")

        message =  "In function {function_name}, The kill file '{filename}' has been created.\n".format(function_name=self.__name_of_current_function(),filename=pathtokillfile)
        self.doInfoLogging(message)

    def _run_db_extensions(self):
        """
        Enables the harness database logging extensions for Metrics and Node Health
        """
        currentdir = os.getcwd()
        self.logger.doDebugLogging(f"Current directory in apptest: {currentdir}")
        runarchive_dir = self.get_path_to_runarchive()
        os.chdir(runarchive_dir)
        self.logger.doInfoLogging(f"Starting the harness database extensions in apptest: {os.getcwd()}")

        # Find the machine name, or give a best-guess
        if not 'RGT_MACHINE_NAME' in os.environ:
            machine_name = subprocess.check_output(['hostname', '--long'])
            self.logger.doWarningLogging(f"WARNING: RGT_MACHINE_NAME not found in os.environ, setting to {machine_name}")
        else:
            machine_name = os.environ['RGT_MACHINE_NAME']

        test_info = {
            'app': self.getNameOfApplication(),
            'test': self.getNameOfSubtest(),
            'runtag': os.environ['RGT_SYSTEM_LOG_TAG'] if 'RGT_SYSTEM_LOG_TAG' in os.environ else 'unknown',
            'machine': machine_name,
            'test_id': self.get_harness_id(),
            'event_time': self._get_event_time(event=StatusFile.EVENT_CHECK_START)
        }

        success_log = 0
        failed_log = 0

        metrics = self._get_metrics()

        if len(metrics) == 0:
            self.logger.doInfoLogging(f"No metrics found to log to influxDB")
        else:
            metrics[f'{test_info["app"]}-{test_info["test"]}-build_time'] = self._get_build_time()
            metrics[f'{test_info["app"]}-{test_info["test"]}-execution_time'] = self._get_execution_time()
            if metrics[f'{test_info["app"]}-{test_info["test"]}-build_time'] < 0:
                self.logger.doErrorLogging(f"Invalid build time for jobID {test_info['test_id']}.")
                do_log_metric = False
            elif metrics[f'{test_info["app"]}-{test_info["test"]}-execution_time'] < 0:
                self.logger.doErrorLogging(f"Invalid execution time for jobID {test_info['test_id']}.")
                do_log_metric = False
            elif self.__db_logger.log_metrics(test_info, metrics):
                success_log += 1
                self.logger.doDebugLogging(f"Successfully logged {len(metrics)} metrics to all databases.")
            else:
                failed_log += 1
                self.logger.doWarningLogging(f"Logging metrics failed to log to at least one database.")
    
        # add node-based health checking
        node_healths = self._get_node_health()
        self.logger.doDebugLogging(f"Found {len(node_healths)} nodes reported for node health")
        if len(node_healths) > 0:
            if not self.__db_logger.log_node_health(test_info, node_healths):
                failed_log += 1
                self.logger.doWarningLogging(f"Logging node_health failed to log to at least one database.")
            else:
                success_log += 1
                self.logger.doDebugLogging(f"Successfully logged {len(node_healths)} node health results to all databases.")

        os.chdir(currentdir)
        return failed_log == 0

    def _get_build_time(self):
        """ Parses the build time from the status file """
        return self._get_time_diff_of_status_files(StatusFile.EVENT_DICT[StatusFile.EVENT_BUILD_START][0], \
                                                    StatusFile.EVENT_DICT[StatusFile.EVENT_BUILD_END][0])

    def _get_execution_time(self):
        """ Parses the binary execution time from the status file """
        return self._get_time_diff_of_status_files(StatusFile.EVENT_DICT[StatusFile.EVENT_BINARY_EXECUTE_START][0], \
                                                    StatusFile.EVENT_DICT[StatusFile.EVENT_BINARY_EXECUTE_END][0])

    def _get_run_timestamp(self, event=StatusFile.EVENT_CHECK_END):
        # Check for start event file and end event file
        check_status_file = f"{self.get_path_to_test()}/{self.test_status_dirname}/{self.get_harness_id()}/"
        check_status_file += f"{StatusFile.EVENT_DICT[event][0]}"

        if not os.path.exists(f"{check_status_file}"):
            self.logger.doWarningLogging(f"Couldn't find required file for post-run time logging: {check_status_file}")
            return -1
        with open(f"{check_status_file}", 'r') as check_fstr:
            line = next(check_fstr)
            check_timestamp = line.split()[0]
            # Convert to UTC
            #dt_utc = datetime.strptime(check_timestamp, "%Y-%m-%dT%H:%M:%S.%f") \
                #+ (datetime.utcnow() - datetime.now())
            dt_utc = datetime.strptime(check_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            ns_utc = int(datetime.timestamp(dt_utc)) * 1000 * 1000 * 1000
        return ns_utc

    def _get_event_time(self, event=StatusFile.EVENT_CHECK_END):
        # Check for start event file and end event file
        status_file = f"{self.get_path_to_test()}/{self.test_status_dirname}/{self.get_harness_id()}/"
        status_file += f"{StatusFile.EVENT_DICT[event][0]}"

        if not os.path.exists(f"{status_file}"):
            self.logger.doWarningLogging(f"Couldn't find required file event time fetching: {status_file}")
            return -1
        with open(f"{status_file}", 'r') as fstr:
            line = next(fstr)
            event_time = line.split()[0]
        return event_time

    def _get_time_diff_of_status_files(self, start_event_file, end_event_file):
        # Check for start event file and end event file
        status_dir = f"{self.get_path_to_test()}/{self.test_status_dirname}/{self.get_harness_id()}"

        for targ in [ f"{status_dir}/{start_event_file}", \
                        f"{status_dir}/{end_event_file}" ]:
            if not os.path.exists(f"{targ}"):
                self.logger.doWarningLogging(f"Couldn't find required file for time logging: {targ}")
                return -1
        start_timestamp = ''
        end_timestamp = ''
        with open(f"{status_dir}/{start_event_file}", 'r') as start_fstr:
            line = next(start_fstr)
            start_timestamp = line.split()[0]
        with open(f"{status_dir}/{end_event_file}", 'r') as end_fstr:
            line = next(end_fstr)
            end_timestamp = line.split()[0]
        if len(start_timestamp) <= 1 or len(end_timestamp) <= 1:
            self.logger.doErrorLogging(f"Invalid start or end timestamp: {start_timestamp}, {end_timestamp}")
            return -1
        #start_ts_dt = datetime.fromisoformat(start_timestamp)
        #end_ts_dt = datetime.fromisoformat(end_timestamp)
        start_ts_dt = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        end_ts_dt = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        diff = end_ts_dt - start_ts_dt
        return diff.total_seconds()   # diff in seconds

    def _get_metrics(self):
        """ Parse the metrics.txt file for InfluxDB reporting """
        def is_numeric(s):
            """ Checks if an entry (RHS) is numeric """
            # Local function. s is assumed to be a whitespace-stripped string
            # Return false for empty string
            if len(s) == 0:
                return False
            number_regex = re.compile('^[-]?([0-9]*\.)?[0-9]+([eE]{1}[+-]?[0-9]+)?$')
            if number_regex.match(s):
                return True
            else:
                return False

        metrics = {}
        app_name = self.getNameOfApplication()
        test_name = self.getNameOfSubtest()
        if not os.path.isfile('metrics.txt'):
            self.logger.doWarningLogging(f"File metrics.txt not found")
            return metrics
        with open('metrics.txt', 'r') as metric_f:
            # Each line is in format "metric = value" (space around '=' optional)
            # All whitespace in metric name will be replaced with underscores
            for line in metric_f:
                # Allows comment lines
                if not line[0] == '#':
                    line_splt = line.split('=')
                    if len(line_splt) == 2:
                        # Replace spaces with underscores, and strip whitespace before/after
                        line_splt[0] = line_splt[0].strip().replace(' ', '_')
                        if len(line_splt[0]) == 0:
                            self.logger.doWarningLogging(f"Skipping line with no metric name: {line.strip()}")
                            continue
                        metric_name = f"{app_name}-{test_name}-{line_splt[0]}"
                        # if it's not numeric, replace spaces with underscores and wrap in quotes
                        line_splt[1] = line_splt[1].strip()
                        if len(line_splt[1]) == 0:
                            self.logger.doWarningLogging(f"Skipping metric with no value: {line_splt[0]}")
                            continue
                        # Handle string/integer metrics
                        if is_numeric(line_splt[1]):
                            metrics[metric_name] = line_splt[1]
                        else:
                            line_splt[1] = line_splt[1].replace(' ', '_')
                            # Wrap strings in double quotes to send to Influx
                            metrics[metric_name] = f'"{line_splt[1]}"'
                    else:
                        self.logger.doErrorLogging(f"Found a line in metrics.txt with 0 or >1 equals signs:\n{line.strip()}")
        return metrics

    def _get_node_health(self):
        """ Parse the nodecheck.txt file for InfluxDB reporting """
        node_healths = {}
        node_name_list = []
        app_name = self.getNameOfApplication()
        test_name = self.getNameOfSubtest()

        if not os.path.isfile('nodecheck.txt'):
            self.logger.doInfoLogging(f"File nodecheck.txt not found.")
            return node_healths
        self.logger.doDebugLogging("Processing file nodecheck.txt.")
        # Add additional desired statuses here and in the below for-loop
        status_decoder = {
            'FAILED': ['FAILED', 'FAIL', 'BAD'],
            'SUCCESS': ['OK', 'SUCCESS', 'GOOD', 'PASS', 'PASSED'],
            'HW-FAIL': ['INCORRECT', 'HW-FAIL'],
            'PERF-FAIL': ['PERF', 'PERF-FAIL']
        }
        with open('nodecheck.txt', 'r') as nodes_f:
            # Each line is in format <nodename> <state> <msg>
            for line in nodes_f:
                # Allows comment lines
                if not line[0] == '#':
                    line_splt = line.strip().split()
                    if not len(line_splt) >= 2:
                        self.logger.doErrorLogging(f"Invalid line in nodecheck.txt: {line}. Skipping.")
                        continue
                    node_name = line_splt[0]
                    if node_name in node_name_list:
                        self.logger.doErrorLogging(f"Found node name already present in the node_health results: {node_name}. Overwriting.")
                    else:
                        node_name_list.append(node_name)
                    node_healths[node_name] = {}
                    # Add additional statuses here
                    for status_string in status_decoder.keys():
                        if line_splt[1].upper() in status_decoder[status_string]:
                            node_healths[node_name]['status'] = status_string
                            break
                    if not 'status' in node_healths[node_name]:
                        self.logger.doErrorLogging(f"Could not identify the status given the status string {line_splt[1]}. Skipping {node_name}.")
                        node_healths.pop(node_name)
                    node_healths[node_name]['message'] = ''
                    if len(line_splt) >= 3:
                        node_healths[node_name]['message'] = ' '.join(line_splt[2:])
        return node_healths

    def __name_of_current_function(self):
        classname = self.__class__.__name__
        functionname = sys._getframe(1).f_code.co_name
        my_name = classname + "." + functionname
        return my_name

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods.                                         @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class ApptestImproperInstantiationError(BaseApptestError):
    """Raised when the class subtest is instantiated with improper parameters."""
    def __init__(self,
                 message,
                 args):
        self.__message = message
        self.__args = args
        return

    @property
    def message(self):
        return self.__message

def do_application_tasks(launch_id,
                         app_test_list,
                         tasks,
                         stdout_stderr,
                         separate_build_stdio=False):
    # Returns [#Passed,#Failed]
    ret = [0, 0, []]
    for app_test in app_test_list:
        print(f"Starting tasks for Application.Test: {app_test.getNameOfApplication()}.{app_test.getNameOfSubtest()}: {tasks}")
        # Non-zero exit status is failure
        if app_test.doTasks(launchid=launch_id,
                         tasks=tasks,
                         stdout_stderr=stdout_stderr,
                         separate_build_stdio=separate_build_stdio):
            ret[1] += 1
            ret[2].append(f"{app_test.getNameOfApplication()}.{app_test.getNameOfSubtest()}")
        else:
            ret[0] += 1
    return ret

def wait_for_jobs_to_complete_in_queue(harness_config,
                                       app_test_list,
                                       timeout):
    """ Waits for the list of subtests to complete a subtestb cycle.

    Parameters
    ----------
    app_test_list : subtest
        A list of subtests.

    timeout : int
        The maximum time in minutes to wait for the subtest cycle to complete.

    Returns
    -------
    ???

    """
    for app_test in app_test_list:
        app_test.waitForAllJobsToCompleteQueue(harness_config, timeout)

    return


