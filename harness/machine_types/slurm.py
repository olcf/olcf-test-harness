#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from libraries.layout_of_apps_directory import apptest_layout
from .base_scheduler import BaseScheduler
import shlex
import subprocess
import re
import os

class SLURM(BaseScheduler):

    """ SLURM class represents an SLURM scheduler. """

    def __init__(self):
        self.__name = 'SLURM'
        self.__submitCmd = 'sbatch'
        self.__statusCmd = 'squeue'
        self.__deleteCmd = 'scancel'
        self.__walltimeOpt = '-t'
        self.__numTasksOpt = '-n'
        self.__jobNameOpt = '-J'
        self.__templateFile = 'slurm.template.x'
        BaseScheduler.__init__(self,self.__name,self.__submitCmd,self.__statusCmd,
                               self.__deleteCmd,self.__walltimeOpt,self.__numTasksOpt,
                               self.__jobNameOpt,self.__templateFile)

    def submit_job(self, batchfilename):
        print("Submitting job from SLURM class using batchfilename " + batchfilename)

        qargs = ""
        if "RGT_SUBMIT_QUEUE" in os.environ:
            qargs = " -p " + os.environ.get('RGT_SUBMIT_QUEUE')

        if "RGT_SUBMIT_ARGS" in os.environ:
            qargs = qargs + os.environ.get('RGT_SUBMIT_ARGS')

        qcommand = self.__submitCmd + " " + qargs + " " + batchfilename
        print(qcommand)

        args = shlex.split(qcommand)
        temp_stdout = "submit.out"
        temp_stderr = "submit.err"

        submit_stdout = open(temp_stdout,"w")
        submit_stderr = open(temp_stderr,"w")

        p = subprocess.Popen(args, stdout=submit_stdout, stderr=submit_stderr)
        p.wait()

        submit_stdout.close()
        submit_stderr.close()

        submit_stdout = open(temp_stdout,"r")
        records = submit_stdout.readlines()
        submit_stdout.close()

        #print("records = ")
        #print(records)

        #print("Extracting SLURM jobID from SLURM class")
        jobid_pattern = re.compile('\d+')
        #print("jobid_pattern = ")
        #print(jobid_pattern)
        #print("jobid_pattern.findall = ")
        jobid = jobid_pattern.findall(records[0])[0]
        self.set_job_id(jobid)
        print("SLURM jobID = ",self.get_job_id())

        return p.returncode


if __name__ == '__main__':
    print('This is the SLURM scheduler class')
