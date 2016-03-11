#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from base_scheduler import BaseScheduler

class PBS(BaseScheduler):

    def __init__(self):
        self.__name = 'PBS'
        self.__submitCmd = 'qsub'
        self.__statusCmd = 'qstat'
        self.__deleteCmd = 'qdel'
        self.__walltimeOpt = '-l walltime='
        self.__numTasksOpt = '-l nodes='
        self.__jobNameOpt = '-N'
        BaseScheduler.__init__(self,self.__name,self.__submitCmd,self.__statusCmd,
                               self.__deleteCmd,self.__walltimeOpt,self.__numTasksOpt,
                               self.__jobNameOpt)

if __name__ == '__main__':
    print 'This is the PBS scheduler class'
