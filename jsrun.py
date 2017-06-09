#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .base_jobLauncher import BaseJobLauncher

class Jsrun(BaseJobLauncher):

    def __init__(self):
        self.__name = 'jsrun'
        self.__launchCmd = 'jsrun'
        self.__numTasksOpt = '-p'
        self.__numTasksPerNodeOpt = '-c'
        BaseJobLauncher.__init__(self,self.__name,self.__launchCmd,self.__numTasksOpt,self.__numTasksPerNodeOpt)

if __name__ == '__main__':
    print('This is the Jsrun job launcher class')
