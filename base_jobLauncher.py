#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

class BaseJobLauncher:
    
    """ BaseJobLauncher represents a job launcher and has the following
        properties:

    Attributes:
        name: string representing the job launcher's name

    Methods:
        get_jobLauncher_name:
        print_jobLauncher_info:
    """
    
    def __init__(self,name,launchCmd,numTasksOpt,numTasksPerNodeOpt):
        self.__name = name
        self.__launchCmd = launchCmd
        self.__numTasksOpt = numTasksOpt
        self.__numTasksPerNodeOpt = numTasksPerNodeOpt

    def get_jobLauncher_name(self):
        return self.__name

    def build_job_command(self,total_processes,processes_per_node,processes_per_socket,executable):
        print("Building job command in the base job launcher class")
        return

    def print_jobLauncher_info(self):
        print("--------------------------------------")
        print("Job Launcher = " + str(self.__name))
        print("Job Launcher command = " + str(self.__launchCmd))
        print("Number of tasks Option = " + str(self.__numTasksOpt))
        print("Number of tasks per node Option = " + str(self.__numTasksPerNodeOpt))
        print("--------------------------------------")

if __name__ == "__main__":
    print("This is the BaseJobLauncher class!")
