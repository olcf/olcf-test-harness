#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from abc import abstractmethod, ABCMeta

class BaseScheduler(metaclass=ABCMeta):
    
    """ BaseScheduler represents a batch scheduler and has the following
        properties:
    Attributes:
        name: string representing the scheduler's name
    Methods:
        get_scheduler_type:
        print_scheduler_info:
    """
    
    def __init__(self, type, submitCmd, statusCmd, deleteCmd,
                 walltimeOpt, numTasksOpt, jobNameOpt, templateFile):
        self.__type = type
        self.__submitCmd = submitCmd
        self.__statusCmd = statusCmd
        self.__deleteCmd = deleteCmd
        self.__walltimeOpt = walltimeOpt
        self.__numTasksOpt = numTasksOpt
        self.__jobNameOpt = jobNameOpt
        self.__templateFile = templateFile
        self.__job_id = None

    def get_scheduler_type(self):
        return self.__type

    def get_job_id(self):
        return self.__job_id

    def set_job_id(self,jobid):
        self.__job_id = jobid
        return

    @abstractmethod
    def set_job_id_from_environ(self):
        print("Setting job id from environment in BaseScheduler class")
        return

    def get_scheduler_template_file_name(self):
        return self.__templateFile

    def print_scheduler_info(self):
        print("--------------------------------------")
        print("Scheduler = " + self.__type)
        print("Submit command = " + self.__submitCmd)
        print("Status command = " + self.__statusCmd)
        print("Delete command = " + self.__deleteCmd)
        print("Walltime Option = " + self.__walltimeOpt)
        print("Number of tasks Option = " + self.__numTasksOpt)
        print("Job Name Option = " + self.__jobNameOpt)
        print("Template File = " + self.__templateFile)
        print("--------------------------------------")

if __name__ == "__main__":
    print("This is the BaseScheduler class!")
