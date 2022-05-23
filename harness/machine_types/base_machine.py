#!/usr/bin/env python3
#
# Author: Veronica G. Vergara L.
#
"""The base class for all machine classes """


# Python imports
from abc import abstractmethod, ABCMeta
from pathlib import Path
import os
import shutil
import subprocess
import shlex

# Harness imports
from libraries.apptest import subtest
from .scheduler_factory import SchedulerFactory
from .jobLauncher_factory import JobLauncherFactory
from machine_types import linux_utilities

class BaseMachine(metaclass=ABCMeta):

    """ BaseMachine represents a compute resource and has the following
        properties:

    Attributes:
        name: string representing the system's name
        scheduler: an object of the BaseScheduler class
        jobLauncher: an object of the BaseJobLauncher class

    Methods:
        get_machine_name:
        print_machine_info:
        print_scheduler_info:
        print_jobLauncher_info:
        set_numNodes:
    """

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # The constructor of class base_machine.
    def __init__(self, name, scheduler_type, jobLauncher_type,
                 numNodes, numSockets, numCoresPerSocket,
                 apptest, separate_build_stdio=False):

        self.__name = name

        self.__scheduler = SchedulerFactory.create_scheduler(scheduler_type)
        """An object of type BaseScheduler : This object is the job resource scheduler. See the
           classs SchedulerFactory for more details."""

        self.__jobLauncher = JobLauncherFactory.create_jobLauncher(jobLauncher_type)
        self.__numNodes = numNodes
        self.__numSockets = numSockets
        self.__numCoresPerSocket = numCoresPerSocket
        self.__apptest = apptest
        self.__separate_build_stdio = separate_build_stdio

        runarchive_dir = self.apptest.get_path_to_runarchive()
        log_filepath = os.path.join(runarchive_dir,self.__class__.__module__)

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
    def scheduler(self):
        """Returns the scheduler. """
        return self.__scheduler

    @property
    def apptest(self):
        """ Object of type subtest : The object subtest for the application-test."""
        return self.__apptest

    @property
    def logger(self):
        return self.__apptest.logger

    @property
    def machine_name(self):
        """str: The name of the machine."""
        return self.__name

    @property
    def separate_build_stdio(self):
        """bool: If true, separate build into stdout and stderr"""
        return self.__separate_build_stdio

    @property
    def check_command(self):
        """Returns the check command string. If no check command string then returns None."""
        return self.test_config.get_check_command()

    @property
    @abstractmethod
    def test_config(self):
        return

    @property
    @abstractmethod
    def build_runtime_environment_command_file(self):
        return

    @property
    @abstractmethod
    def submit_runtime_environment_command_file(self):
        return

    @property
    @abstractmethod
    def check_runtime_environment_command_file(self):
        return

    def isTestCycleComplete(self,stest):
        """Checks if the subtest has completed its cycle.
        Parameters
        ----------
        stest : A subtest object
            The subtest instance is used to check if the testing cycle is complete.

        Returns
        -------
        bool
            If the bool is True, then the subtest cycle is complete. Otherwise
            the cycle in progress.
        """
        return linux_utilities.isTestCycleComplete(stest)

    def did_all_tests_pass(self,stest):
        """Checks if the subtest has passed all of its tests.
        Parameters
        ----------
        stest : A subtest object
            The subtest instance is used to check if the all tests have passed.

        Returns
        -------
        bool
            If the bool is True, then the all tests have passed.
        """

        return linux_utilities.is_all_tests_passed(stest)

    def print_machine_info(self):
        """ Print information about the machine"""
        print("Machine name:\n"+self.get_machine_name())
        self.scheduler.print_scheduler_info()
        print("Job Launcher info: ")
        self.print_jobLauncher_info()

    def get_machine_name(self):
        """ Return a string with the system's name."""
        return self.__name

    def get_scheduler_type(self):
        """ Return a string with the system's name."""
        return self.scheduler.get_scheduler_type()

    def get_scheduler_template_file_name(self):
        """ Return a string with the name of the scheduler's template file."""
        return self.scheduler.get_scheduler_template_file_name()

    def get_jobLauncher_command(self):
        message = "Building jobLauncher command for machine {}.".format(self.machine_name)
        print(message)
        jobLauncher_command = self._build_jobLauncher_command(self.test_config.test_parameters)
        return jobLauncher_command

    def print_jobLauncher_info(self):
        """ Print information about the machine's job launcher."""
        print("Job Launcher Information")
        print(str(self.__jobLauncher))

    def set_numNodes(self,numNodes):
        self.__numNodes = numNodes

    def submit_batch_script(self):
        """Submits the batch script to the job resource manager of scheduler.
        
        Returns
        -------
        int
            The exit status of submitting the batch script to the scheduler. An
            exit_status of 0 indicates success, other wise failure. 
        """
        messloc = "In function {functionname}:".format(functionname=self._name_of_current_function()) 

        message = f"{messloc} Submitting a batch script."
        self.logger.doInfoLogging(message)

        currentdir = os.getcwd()
        message = f"The initial directory is {currentdir}"
        self.logger.doInfoLogging(message)

        # Get the environment using the submit runtime environment file.
        new_env = None
        filename = self.submit_runtime_environment_command_file

        try:
            if filename != "":
                message = f"{messloc} The submit runtime environmental file is {filename}."
                self.logger.doInfoLogging(message)
                new_env = linux_utilities.get_new_environment(self,filename)
        except SetBuildRTEError as error: 
            message = f"{messloc} Unable to set the submit runtime environment."
            self.logger.doCriticalLogging(message)

        exit_status = linux_utilities.submit_batch_script(self,new_env)

        if exit_status != 0:
            message = f"{messloc} Unsuccessful batch script submission with exit status of {exit_status}."
            self.logger.doCriticalLogging(message)
        else:
            message = f"{messloc} Successful batch script submission with exit status of {exit_status}."
            self.logger.doInfoLogging(message)

        return exit_status

    def submit_to_scheduler(self, batchfilename):
        """ Return the jobID for the submission."""

        # If not already in run archive dir, change working directory
        cwd = os.getcwd()
        ra_dir = self.apptest.get_path_to_runarchive()
        if cwd != ra_dir:
            os.chdir(ra_dir)

        submit_exit_value = self.scheduler.submit_job(batchfilename)

        if cwd != ra_dir:
            os.chdir(cwd)

        # Record job id
        self.write_jobid_to_status()

        return submit_exit_value

    def write_jobid_to_status(self):
        """ Write the job id to the appropriate status file """
        jobid_file = self.apptest.get_path_to_job_id_file()
        fileobj = open(jobid_file, "w")
        id_string = "%20s\n" % (self.scheduler.get_job_id())
        fileobj.write(id_string)
        fileobj.close()

    def make_batch_script(self):
        """Creates the batch script for running the test.
        
        We use the template strategy pattern for creating the batch script.
        This method serves as the interface and each machine will implement its
        private method to make the batch script - i.e., every subclass of
        BaseMachine must implement the method _make_batch_script.

        Returns
        -------
        bool
            True if successful creation of batch file.
        """
        self.logger.doInfoLogging("Start of making a batch script.")

        currentdir = os.getcwd()
        message = f"The initial directory is {currentdir}"
        self.logger.doInfoLogging(message)

        bstatus = self._make_batch_script()

        self.logger.doInfoLogging("End of making a batch script.")
        return bstatus
    
    def build_executable(self):
        """ Executes the build command and returns the exit status of the build command.

        Returns
        -------
        int
            The exit status of the build command.

        """
        messloc = "In function {functionname}:".format(functionname=self._name_of_current_function()) 

        message = f"{messloc} Start of buiding executable.\n"
        self.logger.doInfoLogging(message)

        currentdir = os.getcwd()
        message = f"The initial directory is {currentdir}"
        self.logger.doInfoLogging(message)

        path_to_build_directory = self.apptest.get_path_to_workspace_build()
        message = f"The build directory is {path_to_build_directory}"
        self.logger.doInfoLogging(message)

        # Copy the source to the build directory.
        self._copy_source_to_build_directory()

        message = f"{messloc} Copied source to build directory.\n"
        self.logger.doInfoLogging(message)

        # Get the environment using the build runtime environment file.
        new_env = None
        filename = self.build_runtime_environment_command_file

        if filename != "":
            message = f"{messloc} The build runtime environmental file is {filename}."
            self.logger.doInfoLogging(message)
            new_env = linux_utilities.get_new_environment(self,filename)
            message = f"{messloc} The new build environment is as follows:\n"
            message += str(new_env)
            self.logger.doInfoLogging(message)

        # We now change directories to the build directory.
        os.chdir(path_to_build_directory)

        message = f"{messloc} Changed to  build directory {path_to_build_directory}. Commencing build ..."
        self.logger.doInfoLogging(message)

        # We run the build command.
        exit_status = self._build_executable(new_env)

        message = f"{messloc} The build exit status is {exit_status}."
        if exit_status == 0:
            self.logger.doInfoLogging(message)
        else:
            self.logger.doCriticalLogging(message)

        # We now change back to starting directory.
        os.chdir(currentdir)

        message = f"{messloc} Changed back to Scripts directory {currentdir}."
        self.logger.doInfoLogging(message)

        message = f"{messloc} End of buiding executable."
        self.logger.doInfoLogging(message)

        return exit_status

    def check_executable(self):
        """Checks the results of the test and returns pass-failure status of the test.
       
        Returns
        -------
        int :
            The exist status of the check command.
        """

        messloc = "In function {functionname}:".format(functionname=self._name_of_current_function()) 

        currentdir = os.getcwd()
        runarchive_dir = self.apptest.get_path_to_runarchive()

        # Get the environment using the check runtime environment file.
        new_env = None
        filename = self.check_runtime_environment_command_file
        try:
            if filename != "":
                message = f"{messloc} The check runtime environmental file is {filename}."
                new_env = linux_utilities.get_new_environment(self,filename)
        except SetBuildRTEError as error: 
            message = f"{messloc} Unable to set the check runtime environment."
            self.logger.doCriticalLogging(message)

        # We now change to the runarchive directory.
        os.chdir(runarchive_dir)

        message = f"{messloc} The current working directory is {runarchive_dir} "
        self.logger.doInfoLogging(message)

        # We now run the check command.
        check_status = linux_utilities.check_executable(self,new_env)

        self._write_check_exit_status(check_status)

        # We now change back to starting directory.
        os.chdir(currentdir)

        message = f"{messloc} The current working directory is {currentdir} "
        self.logger.doInfoLogging(message)

        return check_status

    def start_report_executable(self):
        """Starts the report executable command.
        
        Return
        ------
        int : The exit status of executing the report command.
        """
        report_command_str = self.test_config.get_report_command()

        messloc = "In function {functionname}: ".format(functionname=self._name_of_current_function()) 
        message = f"{messloc} Running report executable script report script {report_command_str }."

        print(message)
        self.logger.doInfoLogging(message)
        
        exit_status = self._start_report_script(self.test_config.get_report_command())
        return exit_status

    def log_to_influx(self):
        """Logs the results to influx if able
        
        Return
        ------
        bool: Success (True), otherwise, not logged to influxDB
        """
        messloc = "In function {functionname}: ".format(functionname=self._name_of_current_function()) 
        message = f"{messloc} attempting to log to influxDB."

        print(message)
        self.logger.doInfoLogging(message)
        
        exit_status = self._log_to_influx()
        return exit_status

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

    def _build_executable(self,new_env):
        exit_status=linux_utilities.build_executable(self,new_env)
        return exit_status

    def _make_batch_script(self):
        bstatus = linux_utilities.make_batch_script_for_linux(self)
        return bstatus
   
    def _submit_batch_script(self,new_env):
        exit_status = linux_utilities.submit_batch_script(self,new_env)
        return exit_status
    
    def _copy_source_to_build_directory(self):
        messloc = "In function {functionname}:".format(functionname=self._name_of_current_function()) 

        path_to_source = self.apptest.get_path_to_source()
        message = f"{messloc} Path to Source: {path_to_source}"
        print("Path to Source:", path_to_source)
        self.logger.doInfoLogging(message)

        path_to_build_directory = self.apptest.get_path_to_workspace_build()
        message = f"{messloc} Path to build directory: {path_to_build_directory}"
        self.logger.doInfoLogging(message)
        print("Path to Build Dir:", path_to_build_directory)

        shutil.copytree(src=path_to_source,
                        dst=path_to_build_directory,
                        symlinks=True)

    def _write_check_exit_status(self, cstatus):
        """ Write the status of checking results to the status directory."""
        messloc = "In function {functionname}:".format(functionname=self._name_of_current_function()) 

        status_file = self.apptest.get_path_to_job_status_file()
        with open(status_file, "w")  as file_obj:
            message = f"{messloc}  Writing check_exit_status {cstatus} into {status_file}"
            self.logger.doInfoLogging(message)
            file_obj.write(str(cstatus))
        return

    def _name_of_current_function(self):
        import sys
        classname = self.__class__.__name__
        functionname = sys._getframe(1).f_code.co_name
        my_name = classname + "." + functionname
        return my_name

    def _start_report_script(self, reportcmd):
        """ Check if results are correct. """
        currentdir = os.getcwd()
        print("current directory in base_machine:", currentdir)
        runarchive_dir = self.apptest.get_path_to_runarchive()
        os.chdir(runarchive_dir)
        print("Starting report script in base_machine:", os.getcwd())
        path_to_reportscript = os.path.join(self.apptest.get_path_to_scripts(), reportcmd)
        print("Using report script:", path_to_reportscript)

        args = shlex.split(path_to_reportscript)
        report_outfile = "output_report.txt"
        report_stdout = open(report_outfile, "w")
        p = subprocess.Popen(args, stdout=report_stdout, stderr=subprocess.STDOUT)
        p.wait()
        report_stdout.close()
        report_exit_status = p.returncode
        os.chdir(currentdir)
        return report_exit_status

    def _log_to_influx(self):
        """ Check if metrics.txt exists, is proper format, and log to influxDB. """
        currentdir = os.getcwd()
        print("current directory in base_machine:", currentdir)
        runarchive_dir = self.apptest.get_path_to_runarchive()
        os.chdir(runarchive_dir)
        print("Starting influxDB logging in base_machine:", os.getcwd())

        if not 'RGT_INFLUX_URI' in os.environ or not 'RGT_INFLUX_TOKEN' in os.environ:
            print("RGT_INFLUX_URI and RGT_INFLUX_TOKEN required in environment to use InfluxDB")
            os.chdir(currentdir)
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
        influx_app = self.apptest.getNameOfApplication()
        influx_test = self.apptest.getNameOfSubtest()
        # Fields defined from apptest_layout class inherited in subtest
        influx_test_id = self.apptest.get_harness_id()
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

    def _build_jobLauncher_command(self,template_dict):
        """ Return the jobLauncher command."""
        return self.__jobLauncher.build_job_command(template_dict)

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods.                                         @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class BaseMachineError(Exception):
    """Base class for exceptions in this module"""
    pass

class SetBuildRTEError(BaseMachineError):
    """Exception raised for errors in setting the build runtime environment."""
    def __init__(self,message):
        """The class constructor

        Parameters
        ----------
        message : string
            The error message for this exception.
        """
        self._message = message
    
    @property
    def message(self):
        """str: The error message."""
        return self._message

if __name__ == "__main__":
    print("This is the BaseMachine class!")
