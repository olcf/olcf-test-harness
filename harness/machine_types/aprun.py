#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .base_jobLauncher import BaseJobLauncher

class Aprun(BaseJobLauncher):

    def __init__(self):
        self.__name = 'aprun'
        self.__launchCmd = 'aprun'
        self.__numTasksOpt = '-n'
        self.__numTasksPerNodeOpt = '-N'
        BaseJobLauncher.__init__(self,self.__name,self.__launchCmd,self.__numTasksOpt,self.__numTasksPerNodeOpt)

if __name__ == '__main__':
    print('This is the Aprun job launcher class')
