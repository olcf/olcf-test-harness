#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

class BaseScheduler:
    
    """ BaseScheduler represents a batch scheduler and has the following
        properties:
    Attributes:
        name: string representing the scheduler's name
    Methods:
        get_scheduler_type:
        print_scheduler_info:
    """
    
    def __init__(self,type,submitCmd,statusCmd,deleteCmd,
                 walltimeOpt,numTasksOpt,jobNameOpt):
        self.__type = type
        self.__submitCmd = submitCmd
        self.__statusCmd = statusCmd
        self.__deleteCmd = deleteCmd
        self.__walltimeOpt = walltimeOpt
        self.__numTasksOpt = numTasksOpt
        self.__jobNameOpt = jobNameOpt

    def get_scheduler_type(self):
        return self.__type

    def print_scheduler_info(self):
        print("--------------------------------------")
        print("Scheduler = " + self.__type)
        print("Submit command = " + self.__submitCmd)
        print("Status command = " + self.__statusCmd)
        print("Delete command = " + self.__deleteCmd)
        print("Walltime Option = " + self.__walltimeOpt)
        print("Number of tasks Option = " + self.__numTasksOpt)
        print("Job Name Option = " + self.__jobNameOpt)
        print("--------------------------------------")

if __name__ == "__main__":
    print("This is the BaseScheduler class!")
