#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from libraries.apptest import subtest
from .scheduler_factory import SchedulerFactory
from .jobLauncher_factory import JobLauncherFactory
from abc import abstractmethod, ABCMeta
from pathlib import Path
import os
import shutil
import subprocess
import shlex

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

    def __init__(self, name, scheduler_type, jobLauncher_type,
                 numNodes, numSockets, numCoresPerSocket,
                 apptest):
        self.__name = name
        self.__scheduler = SchedulerFactory.create_scheduler(scheduler_type)
        self.__jobLauncher = JobLauncherFactory.create_jobLauncher(jobLauncher_type)
        self.__numNodes = numNodes
        self.__numSockets = numSockets
        self.__numCoresPerSocket = numCoresPerSocket
        self.apptest = apptest

    def print_machine_info(self):
        """ Print information about the machine"""
        print("Machine name:\n"+self.get_machine_name())
        self.__scheduler.print_scheduler_info()
        print("Job Launcher info: ")
        self.print_jobLauncher_info()

    def get_machine_name(self):
        """ Return a string with the system's name."""
        return self.__name

    def get_scheduler_type(self):
        """ Return a string with the system's name."""
        return self.__scheduler.get_scheduler_type()

    def get_scheduler_template_file_name(self):
        """ Return a string with the name of the scheduler's template file."""
        return self.__scheduler.get_scheduler_template_file_name()

    def write_jobid_to_status(self):
        """ Write the job id to the appropriate status file """
        jobid_file = self.apptest.get_path_to_job_id_file()
        fileobj = open(jobid_file, "w")
        id_string = "%20s\n" % (self.__scheduler.get_job_id())
        fileobj.write(id_string)
        fileobj.close()

    def submit_to_scheduler(self, batchfilename):
        """ Return the jobID for the submission."""

        # If not already in run archive dir, change working directory
        cwd = os.getcwd()
        ra_dir = self.apptest.get_path_to_runarchive()
        if cwd != ra_dir:
            os.chdir(ra_dir)

        submit_exit_value = self.__scheduler.submit_job(batchfilename)

        if cwd != ra_dir:
            os.chdir(cwd)

        # Record job id
        self.write_jobid_to_status()

        return submit_exit_value

    def build_jobLauncher_command(self,template_dict):
        """ Return the jobLauncher command."""
        return self.__jobLauncher.build_job_command(template_dict)

    def start_build_script(self, buildcmd):
        """ Return the status of the build."""
        path_to_source = self.apptest.get_path_to_source()
        print("Path to Source:", path_to_source)
        path_to_build_directory = self.apptest.get_path_to_workspace_build()
        print("Path to Build Dir:", path_to_build_directory)
        shutil.copytree(src=path_to_source,
                        dst=path_to_build_directory)
        currentdir = os.getcwd()
        os.chdir(path_to_build_directory)
        print("Using build command:", buildcmd)
        args = shlex.split(buildcmd)
        build_outfile = "output_build.txt"
        build_stdout = open(build_outfile,"w")
        p = subprocess.Popen(args, stdout=build_stdout, stderr=subprocess.STDOUT)
        p.wait()
        build_exit_status = p.returncode
        build_stdout.close()
        os.chdir(currentdir)
        return build_exit_status

    def check_results(self, checkcmd):
        """ Run the check script provided by the user and log the result to the status file."""
        cstatus = self.start_check_script(checkcmd)
        self.write_check_exit_status(cstatus)
        return cstatus

    def start_check_script(self, checkcmd):
        """ Check if results are correct. """
        currentdir = os.getcwd()
        print("current directory in base_machine:", currentdir)
        runarchive_dir = self.apptest.get_path_to_runarchive()
        os.chdir(runarchive_dir)
        print("Starting check script in base_machine:", os.getcwd())
        path_to_checkscript = os.path.join(self.apptest.get_path_to_scripts(), checkcmd)
        print("Using check command:", path_to_checkscript)

        args = shlex.split(path_to_checkscript)
        check_outfile = "output_check.txt"
        check_stdout = open(check_outfile, "w")
        p = subprocess.Popen(args, stdout=check_stdout, stderr=subprocess.STDOUT)
        p.wait()
        check_stdout.close()
        check_exit_status = p.returncode
        os.chdir(currentdir)
        return check_exit_status

    def write_check_exit_status(self, cstatus):
        """ Write the status of checking results to the status directory."""
        status_file = self.apptest.get_path_to_job_status_file()
        file1_obj = open(status_file, "w")

        print("Writing check_exit_status =", cstatus, "into", status_file)
        # Set the string to write to the job_status.txt file.
        #if jstatus == 0:
        #    pf = "1"
        #elif jstatus == 1:
        #    pf = "0"
        #elif jstatus >= 2:
        #    pf = "2"
        string1 = "%s\n" % (cstatus)

        file1_obj.write(string1)
        file1_obj.close()

    def start_report_script(self, reportcmd):
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

    def print_jobLauncher_info(self):
        """ Print information about the machine's job launcher."""
        print("Job Launcher Information")
        print(str(self.__jobLauncher))

    def set_numNodes(self,numNodes):
        self.__numNodes = numNodes

    @abstractmethod
    def make_batch_script(self):
        print("Making a batch script in the BaseMachine class")
        return

    @abstractmethod
    def submit_batch_script(self):
        print("Submitting a batch script in the BaseMachine class")
        return


if __name__ == "__main__":
    print("This is the BaseMachine class!")
