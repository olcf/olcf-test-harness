#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .scheduler_factory import SchedulerFactory
from .jobLauncher_factory import JobLauncherFactory
from abc import abstractmethod, ABCMeta
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

    def __init__(self,name,scheduler_type,jobLauncher_type,numNodes,
                 numSockets,numCoresPerSocket,rgt_test_input_file,workspace,
                 harness_id,scripts_dir):
        self.__name = name
        self.__scheduler = SchedulerFactory.create_scheduler(scheduler_type)
        self.__jobLauncher = JobLauncherFactory.create_jobLauncher(jobLauncher_type)
        self.__numNodes = numNodes
        self.__numSockets = numSockets
        self.__numCoresPerSocket = numCoresPerSocket
        self.__rgt_test_input_file = rgt_test_input_file
        self.__rgt_workspace = workspace
        self.__rgt_harness_id = harness_id
        self.__rgt_scripts_dir = scripts_dir
        self.set_rgt_results_dir()

    def print_machine_info(self):
        """ Print information about the machine"""
        print("Machine name:\n"+self.get_machine_name())
        self.__scheduler.print_scheduler_info()
        print("Job Launcher info: ")
        self.print_jobLauncher_info()

    def get_machine_name(self):
        """ Return a string with the system's name."""
        return self.__name

    def get_rgt_workspace(self):
        """ Return a string with the path to the workspace."""
        return self.__rgt_workspace

    def create_rgt_workspace(self):
        """ Create a workspace for this test instance."""
        os.makedirs(self.get_rgt_workspace(), exist_ok=True)
        return

    def get_rgt_input_file_name(self):
        """ Return a string with the test input file name."""
        return self.__rgt_test_input_file

    def get_scheduler_type(self):
        """ Return a string with the system's name."""
        return self.__scheduler.get_scheduler_type()

    def get_scheduler_template_file_name(self):
        """ Return a string with the name of the scheduler's template file."""
        return self.__scheduler.get_scheduler_template_file_name()

    def submit_to_scheduler(self,batchfilename,unique_id):
        """ Return the jobID for the submission."""
        submit_exit_value = self.__scheduler.submit_job(batchfilename)
        self.__scheduler.write_jobid_to_status(unique_id)
        return submit_exit_value

    def build_jobLauncher_command(self,template_dict):
        """ Return the jobLauncher command."""
        return self.__jobLauncher.build_job_command(template_dict)

    def start_build_script(self,buildcmd):
        """ Return the status of the build."""
        os.chdir(self.get_rgt_scripts_dir())
        currentdir = os.getcwd()
        print("current directory in base_machine: ",currentdir)
        (dir_head1, dir_tail1) = os.path.split(currentdir)
        (dir_head2, dir_tail2) = os.path.split(dir_head1)
        path_to_source = os.path.join(dir_head2,"Source")
        print("Path to Source: ",path_to_source)
        self.create_rgt_workspace()
        path_to_build_directory = os.path.join(self.get_rgt_workspace(),"build_directory")
        print("Path to Build Dir: ", path_to_build_directory)
        shutil.copytree(path_to_source,path_to_build_directory)
        os.chdir(path_to_build_directory)
        print("Starting build in directory: " + path_to_build_directory + " using " + buildcmd)
        args = shlex.split(buildcmd)
        build_outfile = "output_build.txt"
        build_stdout = open(build_outfile,"w")
        p = subprocess.Popen(args,stdout=build_stdout,stderr=subprocess.STDOUT)
        p.wait()
        build_stdout.close()

        build_exit_status = p.returncode
        os.chdir(currentdir)
        return build_exit_status

    def check_results(self,checkcmd):
        """ Run the check script provided by the user and log the result to the status file."""
        jstatus = self.start_check_script(checkcmd)
        self.write_check_exit_status(jstatus)
        return jstatus

    def start_check_script(self,checkcmd):
        """ Check if results are correct. """
        currentdir = os.getcwd()
        print("current directory in base_machine: ",currentdir)
        os.chdir(self.get_rgt_results_dir())
        print("Starting check script in base_machine: ",os.getcwd())
        path_to_checkscript = os.path.join(self.get_rgt_scripts_dir(),checkcmd)
        print("Using check script: ",path_to_checkscript)

        args = shlex.split(path_to_checkscript)
        check_outfile = "output_check.txt"
        check_stdout = open(check_outfile, "w")
        p = subprocess.Popen(args,stdout=check_stdout,stderr=subprocess.STDOUT)
        p.wait()
        check_stdout.close()
        check_exit_status = p.returncode
        os.chdir(currentdir)
        return check_exit_status

    def write_check_exit_status(self,jstatus):
        """ Write the status of checking results to the status directory."""
        (dir_head1, dir_tail1) = os.path.split(self.get_rgt_results_dir())
        (dir_head2, dir_tail2) = os.path.split(dir_head1)

        file1 = os.path.join(dir_head2,"Status",dir_tail1,"job_status.txt")
        file1_obj = open(file1,"w")

        print("Writing check_exit_status = ",jstatus," into ",file1)
        # Set the string to write to the job_status.txt file.
        #if jstatus == 0:
        #    pf = "1"
        #elif jstatus == 1:
        #    pf = "0"
        #elif jstatus >= 2:
        #    pf = "2"
        string1 = "%s\n" % (jstatus)

        file1_obj.write(string1)
        file1_obj.close()

    def start_report_script(self,reportcmd):
        """ Check if results are correct. """
        os.chdir(self.get_rgt_scripts_dir())
        currentdir = os.getcwd()
        print("current directory in base_machine: ",currentdir)
        os.chdir(self.get_rgt_results_dir())
        print("Starting check script in base_machine: ",os.getcwd())
        path_to_reportscript = os.path.join(self.get_rgt_scripts_dir(),reportcmd)
        print("Using report script: ",path_to_reportscript)

        args = shlex.split(path_to_reportscript)
        report_outfile = "output_report.txt"
        report_stdout = open(report_outfile, "w")
        p = subprocess.Popen(args,stdout=report_stdout,stderr=subprocess.STDOUT)
        p.wait()
        report_stdout.close()
        report_exit_status = p.returncode
        os.chdir(currentdir)
        return report_exit_status

    def get_rgt_harness_id(self):
        """ Return the string with the Harness ID for this test instance."""
        return self.__rgt_harness_id

    def set_rgt_results_dir(self):
        """ Return the string with the path to the Run_Archive/Harness ID directory."""
        os.chdir(self.get_rgt_scripts_dir())
        currentdir = os.getcwd()
        (dir_head1, dir_tail1) = os.path.split(currentdir)
        self.__rgt_results_dir = os.path.join(dir_head1,"Run_Archive",self.get_rgt_harness_id())
        return

    def get_rgt_results_dir(self):
        """ Return the string corresponding to the path to the Run_Archive directory."""
        return self.__rgt_results_dir

    def get_rgt_scripts_dir(self):
        return self.__rgt_scripts_dir

    def get_rgt_workdir(self):
        """ Return the string with the path to the Run_Archive/Harness ID directory."""
        return os.path.join(self.get_rgt_workspace(),"workdir")

    def print_jobLauncher_info(self):
        """ Print information about the machine's job launcher."""
        print("Job Launcher Information")
        print(str(self.__jobLauncher))

    def set_numNodes(self,numNodes):
        self.__numNodes = numNodes

    @abstractmethod
    def read_rgt_test_input(self):
        if os.path.isfile(self.get_rgt_input_file_name()):
            print("Reading input file")
        else:
            print("No input found. Provide your own scripts")

    @abstractmethod
    def make_batch_script(self):
        print("I'm making a batch script in the base class")
        return

    @abstractmethod
    def submit_batch_script(self):
        print("I'm submitting a batch script in the base class")
        return


if __name__ == "__main__":
    print("This is the BaseMachine class!")
