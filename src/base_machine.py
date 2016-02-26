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
        scheduler: an object of the baseScheduler class

    Methods:
        print_machine_info:
        print_scheduler_info: 
        get_machine_name:
    """

    def __init__(self,name):
        self.__name = name 
        self.__scheduler = scheduler

    def get_machine_name(self):
        """ Return a string with the system's name."""
        return self.__name

    def print_scheduler_info(self):
        print(str(self.__scheduler))

if __name__ == "__main__":
    print "This is the BaseMachine class!"
