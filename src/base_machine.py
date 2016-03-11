#!/usr/bin/env python
# 
# Author: Veronica G. Vergara L.
# 
#

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

    def __init__(self,name,scheduler,jobLauncher,numNodes,
                 numSockets,numCoresPerSocket):
        self.__name = name 
        self.__scheduler = scheduler
        self.__jobLauncher = jobLauncher
        self.__numNodes = numNodes
        self.__numSockets = numSockets
        self.__numCoresPerSocket = numCoresPerSocket

    def print_machine_info(self):
        """ Print information about the machine"""
        print("Machine name:\n"+self.get_machine_name())
        self.print_scheduler_info()
        print("Job Launcher info: ")
        self.print_jobLauncher_info()

    def get_machine_name(self):
        """ Return a string with the system's name."""
        return self.__name

    def print_scheduler_info(self):
        """ Print information about the machine's scheduler."""
        print("Scheduler Information")
        print(str(self.__scheduler))

    def print_jobLauncher_info(self):
        """ Print information about the machine's job launcher."""
        print("Job Launcher Information")
        print(str(self.__jobLauncher))

    def set_numNodes(self,numNodes):
        self.__numNodes = numNodes

if __name__ == "__main__":
    print "This is the BaseMachine class!"
