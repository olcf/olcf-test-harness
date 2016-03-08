#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from base_machine import BaseMachine

class IBMpower8(BaseMachine):
    
    def __init__(self,name='IBM Power8',scheduler=None):
        BaseMachine.__init__(self,name)
        self.__scheduler = scheduler

    def print_scheduler_info(self):
        print(str(self.__scheduler))

if __name__ == "__main__":
    print 'This is the IBM Power8 class'
