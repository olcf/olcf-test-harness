#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .base_jobLauncher import BaseJobLauncher

class Srun(BaseJobLauncher):

    def __init__(self):
        self.__name = 'srun'
        self.__launchCmd = 'srun'
        self.__numProcessesOpt = '-n'
        self.__numCPUsPerTaskOpt = '-c'
        self.__numTasksPerNodeOpt = '-N'
        self.__launchDistributionOpt = '-m'
        self.__numGPUsPerJobstepOpt = '-G'
        self.__memoryPerNodeOpt = '--mem'

        BaseJobLauncher.__init__(self,self.__name,self.__launchCmd)

    def build_job_command(self,template_dict):
        print("Building job command in the Srun class")
        job_launch_command = self.__launchCmd + " "

        ktemp = "total_processes"
        if ktemp in template_dict:
            job_launch_command += self.__numProcessesOpt + " " + template_dict[ktemp] + " "

        ktemp = "num_cpus_per_task"
        if ktemp in template_dict:
            job_launch_command += self.__numCPUsPerTaskOpt + " " + template_dict[ktemp] + " "

        ktemp = "num_tasks_per_node"
        if ktemp in template_dict:
            job_launch_command += self.__numTasksPerNodeOpt + " " + template_dict[ktemp] + " "

        ktemp = "launch_distribution"
        if ktemp in template_dict:
            job_launch_command += self.__launchDistributionOpt + " " + template_dict[ktemp] + " "

        ktemp = "num_gpus_per_jobstep"
        if ktemp in template_dict:
            job_launch_command += self.__numGPUsPerJobstepOpt + " " + template_dict[ktemp] + " "

        ktemp = "memory_per_node"
        if ktemp in template_dict:
            job_launch_command += self.__memoryPerNodeOpt + " " + template_dict[ktemp] + " "

        job_launch_command += template_dict["pathtoexecutable"]

        return job_launch_command

if __name__ == '__main__':
    print('This is the Srun job launcher class')

