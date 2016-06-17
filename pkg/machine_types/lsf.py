#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .base_scheduler import BaseScheduler

class LSF(BaseScheduler):

    """ LSF class represents an LSF scheduler. """

    def __init__(self):
        self.__name = 'LSF'
        self.__submitCmd = 'bsub'
        self.__statusCmd = 'bjobs'
        self.__deleteCmd = 'bkill'
        self.__walltimeOpt = '-W'
        self.__numTasksOpt = '-n'
        self.__jobNameOpt = '-N'
        BaseScheduler.__init__(self,self.__name,self.__submitCmd,self.__statusCmd,
                               self.__deleteCmd,self.__walltimeOpt,self.__numTasksOpt,
                               self.__jobNameOpt)

if __name__ == '__main__':
    print('This is the LSF scheduler class')
