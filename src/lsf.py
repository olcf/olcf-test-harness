#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from base_scheduler import BaseScheduler

class LSF(BaseScheduler):

    def __init__(self,name='LSF',jobLauncher=None):
        BaseScheduler.__init__(self,name)
        self.__jobLauncher = jobLauncher

    def print_jobLauncher(self):
        print(str(self.__jobLauncher))

if __name__ == '__main__':
    print 'This is the LSF scheduler class'
