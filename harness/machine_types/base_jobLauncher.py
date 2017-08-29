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
    
    def __init__(self,name,launchCmd):
        self.__name = name
        self.__launchCmd = launchCmd

    def get_jobLauncher_name(self):
        return self.__name

    def build_job_command(self):
        print("Building job command in the base job launcher class")
        return

    def print_jobLauncher_info(self):
        print("--------------------------------------")
        print("Job Launcher = " + str(self.__name))
        print("Job Launcher command = " + str(self.__launchCmd))

if __name__ == "__main__":
    print("This is the BaseJobLauncher class!")
