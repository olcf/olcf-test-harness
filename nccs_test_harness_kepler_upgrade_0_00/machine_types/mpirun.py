#!/usr/bin/env python3
#
# Author: Mark Berrill
#
#

from .base_jobLauncher import BaseJobLauncher

class Mpirun(BaseJobLauncher):

    def __init__(self):
        self.__name = 'mpirun'
        self.__launchCmd = 'mpirun'
        self.__numTasksOpt = '-n'
        self.__numTasksPerNodeOpt = '-N'
        BaseJobLauncher.__init__(self,self.__name,self.__launchCmd,self.__numTasksOpt,self.__numTasksPerNodeOpt)

    def build_job_command(self,total_processes,processes_per_node,processes_per_socket,executable):
        print("Building job command in the mpirun class")
        job_launch_command = self.__launchCmd + " " + executable + " 1> stdout.txt 2> stderr.txt"
        return job_launch_command

if __name__ == '__main__':
    print('This is the Mpirun job launcher class')
