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
        jobLauncher: an object of the BaseJobLauncher class

    Methods:
        print_scheduler_info:
        print_job_launcher_info:
        get_scheduler_name:
    """
    
    def __init__(self,name,jobLauncher):
        self.__name = name
        self.__jobLauncher = jobLauncher

    def print_scheduler_info(self):
        print(str(self.__jobLauncher))

if __name__ == "__main__":
    print "This is the BaseScheduler class!"
