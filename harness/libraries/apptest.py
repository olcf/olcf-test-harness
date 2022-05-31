#! /usr/bin/env python3

""" The apptest module encapsulates the application-test directory structure layout.

"""

# Python package imports
import subprocess
import shlex
import time
import datetime
import os
import sys
import copy
from types import *

# NCCS Test Harness Package Imports
from libraries.base_apptest import base_apptest
from libraries.base_apptest import BaseApptestError
from libraries.layout_of_apps_directory import apptest_layout
from libraries.status_file import parse_status_file
from libraries.status_file import parse_status_file2
from libraries.status_file import summarize_status_file
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command_return_exitstatus
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command_return_stdout_stderr_exitstatus

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
                                tag)

        # Format of data is [<local_path_to_tests>, <application>, <test>]
        self.__apps_test_checked_out = []
        self.__apps_test_checked_out.append([self.getLocalPathToTests(),
                                             self.getNameOfApplication(),
                                             name_of_subtest])
        self.__number_of_iterations = -1
        self.__myLogger = logger

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

                self.cloneRepository(my_repository,
                                     destination)

                self.doInfoLogging("End of cloning repository")


                if test_checkout_lock:
                    test_checkout_lock.release()

            elif harness_task == Harness.starttest:
                message = "Start of starting test."
                self.doInfoLogging(message)

                self._start_test(launchid, stdout_stderr, separate_build_stdio=separate_build_stdio)

                message = "End of starting test"
                self.doInfoLogging(message)

            elif harness_task == Harness.stoptest:
                self._stop_test()

            elif harness_task == Harness.influx_log:
                self._influx_log_mode()

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
            self.doInfoLogging(string1)
            sys.exit(string1)
        else:
            message = "Cloning of repository passed"
            self.doInfoLogging(message)

        return

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
        startdate = datetime.datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        log_message =  "The startdate is " + startdate.ctime()
        print (log_message)

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime.datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
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
        startdate = datetime.datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                      int(starttimewords[3]),int(starttimewords[4]))
        log_message = "The startdate is " + startdate.ctime()
        print(log_message)

        endtimestring = taskwords[1]
        endtimestring = endtimestring.strip()
        endtimewords = endtimestring.split("_")
        enddate = datetime.datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
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

        if (Harness.influx_log in taskwords1):
            app_tasks1.append(Harness.influx_log)
            taskwords1.remove(Harness.influx_log)

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
        import datetime

        # Set the time counters and other flags for ensuring a maximum
        # wait time while checking completion of the test cycle.
        time_between_checks = 5.0
        timeout_secs = timeout*60.0
        elapsed_time = 0.0

        # Print an informational message on the maximum wait time.
        message  = 'Waiting for all {} : {} tests to complete the testing cycle.\n'.format(self.getNameOfApplication(),self.getNameOfSubtest())
        message += 'The maximum wait time is {}.\n'.format(str(timeout_secs))
        message += 'The time between checks is {}.\n'.format(str(time_between_checks))
        print(message)

        # Instantiate the machine for this computer.
        mymachine = MachineFactory.create_machine(harness_config, self)

        continue_checking = True
        start_time = datetime.datetime.now()
        while continue_checking:
            time.sleep(time_between_checks)
            elapsed_time = datetime.datetime.now() - start_time
            message = 'Checking for subtest cycle completion at {} seconds.\n'.format(str(elapsed_time))
            print(message)

            if mymachine.isTestCycleComplete(self):
               continue_checking = False
               break

            elapsed_time = datetime.datetime.now() - start_time
            if elapsed_time.total_seconds() > timeout_secs:
                continue_checking = False
                message_elapsed_time = 'After {} seconds the testing cycle has exceeded the maximum wait time.\n'.format(str(elapsed_time))
                print(message_elapsed_time)

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
        starttestcomand = f"test_harness_driver.py -r -l {launchid}"
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
            sys.exit(string1)
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

    # Used when --mode influx_log is run after a harness run
    def _influx_log_mode(self):
        """ Logs available tests to InfluxDB, via --mode influx_log """
        currentdir = os.getcwd()
        print(f"In {self.__name_of_current_function()}, cwd: {currentdir}")
        # Run_Archive adds an odd ID on to the end, so this is a portable solution
        testdir = self.get_path_to_test()
        os.chdir(testdir)
        # If Run_Archive exists, continue, else terminate because no tests have been run
        if not os.path.exists('./Run_Archive'):
            os.chdir(currentdir)
            print("Could not find Run_Archive directory in ", testdir)
            print("This is likely caused by no tests being run")
            return
        os.chdir('./Run_Archive')

        # I don't need to worry about extraneous links, like `latest`, because there's no race conditions
        for test_id in os.listdir('.'):
            if not os.path.exists(f"./{test_id}/.influx_logged") and \
                    not os.path.exists(f"./{test_id}/.influx_disabled"):
                print(f"Attempting to log {test_id}")
                if self._log_to_influx(test_id):
                    print(f"Successfully logged {test_id}")
                else:
                    print(f"Unable to log {test_id}")

        os.chdir(currentdir)

    # Logs a single test ID to InfluxDB (when run AFTER a harness run, this class doesn't hold a single test ID)
    def _log_to_influx(self, influx_test_id):
        """ Check if metrics.txt exists, is proper format, and log to influxDB. """
        currentdir = os.getcwd()
        print("current directory in apptest:", currentdir)
        runarchive_dir = f"{self.get_path_to_test()}/Run_Archive/{influx_test_id}"
        os.chdir(runarchive_dir)
        print("Starting influxDB logging in apptest:", os.getcwd())

        if 'RGT_DISABLE_INFLUX' in os.environ:
            if str(os.environ['RGT_DISABLE_INFLUX']) == '1':
                print("InfluxDB logging is explicitly disabled with RGT_DISABLE_INFLUX=1")
                print("Creating .influx_disabled file in Run_Archive")
                print("If this was not intended, remove the .influx_disabled file and run the harness under mode 'influx_log'")
                os.mknod('.influx_disabled')
                os.chdir(currentdir)
                return False
            else:
                print("Unrecognized value of RGT_DISABLE_INFLUX: ", os.environ['RGT_DISABLE_INFLUX'])
        if not 'RGT_INFLUX_URI' in os.environ or not 'RGT_INFLUX_TOKEN' in os.environ:
            print("RGT_INFLUX_URI and RGT_INFLUX_TOKEN required in environment to use InfluxDB")
            os.chdir(currentdir)
            return False

        # Check if influx was disabled for this run
        if os.path.exists('.influx_disabled'):
            print("This harness test explicitly disabled influx logging. If this is by mistake, remove the .influx_disabled file and run again")
            return False
        # Check if the .influx_logged file already exists - it shouldn't, but just in case
        if os.path.exists('.influx_logged'):
            print("The .influx_logged file already exists.")
            return False

        import requests

        influx_url = os.environ['RGT_INFLUX_URI']
        influx_token = os.environ['RGT_INFLUX_TOKEN']

        headers = {
            'Authorization': "Token " + influx_token,
            'Content-Type': "text/plain; charset=utf-8",
            'Accept': "application/json"
        }

        # Inherited from environment or 'unknown'
        # This may be set as `unknown` if run outside of harness job
        influx_runtag = (
            os.environ['RGT_SYSTEM_LOG_TAG']
            if 'RGT_SYSTEM_LOG_TAG' in os.environ else 'unknown')
        # Fields defined by subtest class
        influx_app = self.getNameOfApplication()
        influx_test = self.getNameOfSubtest()
        # Machine name
        if not 'LMOD_SYSTEM_NAME' in os.environ:
            influx_machine_name = subprocess.check_output(['hostname', '--long'])
            print(f"WARNING: LMOD_SYSTEM_NAME not found in os.environ, setting to {self.influx_machine_name}")
        else:
            influx_machine_name = os.environ['LMOD_SYSTEM_NAME']

        metrics = self._get_metrics(influx_machine_name, influx_app, influx_test)

        if len(metrics) == 0:
            print(f"No metrics found to log to influxDB")
            os.chdir(currentdir)
            return False

        influx_event_record_string = f"metrics,job_id={influx_test_id},app={influx_app},test={influx_test}"
        influx_event_record_string += f",runtag={influx_runtag},machine={influx_machine_name}"
        num_metrics_printed = 0
        for k, v in metrics.items():
            if num_metrics_printed == 0:
                influx_event_record_string += f" {k}={v}"
            else:
                influx_event_record_string += f",{k}={v}"
            num_metrics_printed += 1
        try:
            r = requests.post(influx_url, data=influx_event_record_string, headers=headers)
            print(f"Successfully sent {influx_event_record_string} to {influx_url}")
        except:
            print(f"Failed to send {influx_event_record_string} to {influx_url}:")
            print(r.text)
            os.chdir(currentdir)
            return False

        # We're in Run_Archive. The Influx POST request has succeeded, as far as we know,
        # so let's create a .influx_logged file
        os.mknod('.influx_logged')

        os.chdir(currentdir)
        # if we make it to the end, return True
        return True

    def _get_metrics(self, machine_name, app_name, test_name):
        """ Parse the metrics.txt file for InfluxDB reporting """
        def is_numeric(s):
            """ Checks if an entry (RHS) is numeric """
            # Local function. s is assumed to be a whitespace-stripped string
            # checks if a decimal place or preceding negative sign exists, strip/remove as needed
            if s[0] == '-':
                s = s[1:]
            # for decimal places, we split the string on '.', then check if each side is numeric
            s = s.split('.')
            if len(s) == 0 or len(s) > 2:
                return False
            if not s[0].isnumeric():
                return False
            if len(s) == 2 and not s[1].isnumeric():
                return False
            return True

        metrics = {}
        if not os.path.isfile('metrics.txt'):
            print(f"File metrics.txt not found")
            return metrics
        with open('metrics.txt', 'r') as metric_f:
            # Each line is in format "metric = value" (space around '=' optional)
            # All whitespace in metric name will be replaced with underscores
            for line in metric_f:
                # Allows comment lines
                if not line[0] == '#':
                    line = line.split('=')
                    if len(line) == 2:
                        # Replace spaces with underscores, and strip whitespace before/after
                        line[0] = line[0].strip().replace(' ', '_')
                        metric_name = f"{app_name}-{test_name}-{line[0]}"
                        # if it's not numeric, replace spaces with underscores and wrap in quotes
                        line[1] = line[1].strip()
                        if is_numeric(line[1]):
                            metrics[metric_name] = line[1]
                        else:
                            line[1] = line[1].replace(' ', '_')
                            # Wrap strings in double quotes to send to Influx
                            metrics[metric_name] = f'"{line[1]}"'
                    else:
                        print(f"Found a line in metrics.txt with 0 or >1 equals signs:\n{line}")
        return metrics

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
    for app_test in app_test_list:
        print(f"Starting tasks for Application.Test: {app_test.getNameOfApplication()}.{app_test.getNameOfSubtest()}: {tasks}")
        app_test.doTasks(launchid=launch_id,
                         tasks=tasks,
                         stdout_stderr=stdout_stderr,
                         separate_build_stdio=separate_build_stdio)
    return

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


