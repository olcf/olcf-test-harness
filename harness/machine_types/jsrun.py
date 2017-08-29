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
        self.__numProcessesOpt = '-p'
        self.__numCPUsPerResourceOpt = '-c'
        self.__launchDistributionOpt = '-d'
        self.__numGPUsPerResourceOpt = '-g'
        self.__latencyPriorityOpt = '-l'
        self.__memoryPerResourceOpt = '-m'
        self.__numResourcesOpt = '-n'
        self.__numResourcesPerHostOpt = '-r'
        self.__stdioModeOpt = '-e'
        self.__appfileOpt = '-f'
        self.__stderrOpt = '-k'
        self.__stdoutOpt = '-o'
        self.__stdinOpt = '-t'
        self.__chdirOpt = '-h'
        self.__debugSymbolsOpt = '-u'
        self.__immediateReturnOpt = '-i'
        self.__exitOnErrorOpt = '-X'
        self.__environmentSettingOpt = '-E'

        #BaseJobLauncher.__init__(self,self.__name,self.__launchCmd,self.__numProcessesOpt,self.__numCPUsPerResourceOpt,self.__launchDistributionOpt,self.__numGPUsPerResourceOpt,
        #                        self.__latencyPriorityOpt,self.__memoryPerResourceOpt,self.__numResourcesOpt,self.__numResourcesPerHostOpt,self.__stdioModeOpt,self.__appfileOpt,
        #                        self.__stderrOpt,self.__stdoutOpt,self.__stdinOpt,self.__chdirOpt,self.__debugSymbolsOpt,self.__immediateReturnOpt,self.__exitOnErrorOpt,
        #                        self.__environmentSettingOpt)

        BaseJobLauncher.__init__(self,self.__name,self.__launchCmd)

    def build_job_command(self,template_dict):
        print("Building job command in the Jsrun class")
        job_launch_command = self.__launchCmd + " "

        ktemp = "total_processes"
        if ktemp in template_dict:
            job_launch_command += self.__numProcessesOpt + " " + template_dict[ktemp] + " "

        ktemp = "num_cpus_per_resource"
        if ktemp in template_dict:
            job_launch_command += self.__numCPUsPerResourceOpt + " " + template_dict[ktemp] + " "

        ktemp = "launch_distribution"
        if ktemp in template_dict:
            job_launch_command += self.__launchDistributionOpt + " " + template_dict[ktemp] + " "

        ktemp = "num_gpus_per_resource"
        if ktemp in template_dict:
            job_launch_command += self.__numGPUsPerResourceOpt + " " + template_dict[ktemp] + " "

        ktemp = "latency_priority"
        if ktemp in template_dict:
            job_launch_command += self.__latencyPriorityOpt + " " + template_dict[ktemp] + " "

        ktemp = "memory_per_resource"
        if ktemp in template_dict:
            job_launch_command += self.__memoryPerResourceOpt + " " + template_dict[ktemp] + " "

        ktemp = "num_resources"
        if ktemp in template_dict:
            job_launch_command += self.__numResourcesOpt + " " + template_dict[ktemp] + " "

        ktemp = "num_resources_per_host"
        if ktemp in template_dict:
            job_launch_command += self.__numResourcesPerHostOpt + " " + template_dict[ktemp] + " "

        ktemp = "stdio_mode"
        if ktemp in template_dict:
            job_launch_command += self.__stdioModeOpt + " " + template_dict[ktemp] + " "

        ktemp = "app_file"
        if ktemp in template_dict:
            job_launch_command += self.__appfileOpt + " " + template_dict[ktemp] + " "

        ktemp = "stderr"
        if ktemp in template_dict:
            job_launch_command += self.__stderrOpt + " " + template_dict[ktemp] + " "

        ktemp = "stdout"
        if ktemp in template_dict:
            job_launch_command += self.__stdoutOpt + " " + template_dict[ktemp] + " "

        ktemp = "stdin"
        if ktemp in template_dict:
            job_launch_command += self.__stdinOpt + " " + template_dict[ktemp] + " "

        ktemp = "chdir"
        if ktemp in template_dict:
            job_launch_command += self.__chdirOpt + " " + template_dict[ktemp] + " "

        ktemp = "debug_symbols"
        if ktemp in template_dict:
            job_launch_command += self.__debugSymbolsOpt + " " + template_dict[ktemp] + " "

        ktemp = "immediate_return"
        if ktemp in template_dict:
            job_launch_command += self.__immediateReturnOpt + " " + template_dict[ktemp] + " "

        ktemp = "exit_on_error"
        if ktemp in template_dict:
            job_launch_command += self.__exitOnErrorOpt + " " + template_dict[ktemp] + " "

        ktemp = "environment_setting"
        if ktemp in template_dict:
            job_launch_command += self.__environmentSettingOpt + " " + template_dict[ktemp] + " "

        job_launch_command += template_dict["pathtoexecutable"]

        return job_launch_command

if __name__ == '__main__':
    print('This is the Jsrun job launcher class')

