#!/usr/bin/env python
# 
# Author: Veronica G. Vergara L.
# 
#

from scheduler_factory import SchedulerFactory
from jobLauncher_factory import JobLauncherFactory

class BaseMachine:
    
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
                 numSockets,numCoresPerSocket):
        self.__name = name 
        self.__scheduler = SchedulerFactory.create_scheduler(scheduler_type)
        self.__jobLauncher = JobLauncherFactory.create_jobLauncher(jobLauncher_type)
        self.__numNodes = numNodes
        self.__numSockets = numSockets
        self.__numCoresPerSocket = numCoresPerSocket

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

    def print_jobLauncher_info(self):
        """ Print information about the machine's job launcher."""
        print("Job Launcher Information")
        print(str(self.__jobLauncher))

    def set_numNodes(self,numNodes):
        self.__numNodes = numNodes

if __name__ == "__main__":
    print("This is the BaseMachine class!")
