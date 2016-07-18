#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .base_scheduler import BaseScheduler
import shlex
import subprocess
import re

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
        self.__templateFile = 'lsf.template.x'
        BaseScheduler.__init__(self,self.__name,self.__submitCmd,self.__statusCmd,
                               self.__deleteCmd,self.__walltimeOpt,self.__numTasksOpt,
                               self.__jobNameOpt,self.__templateFile)

    def submit_job(self,batchfilename):
        print("Submitting job from LSF class using batchfilename " + batchfilename)
        qcommand = self.__submitCmd
        args = shlex.split(qcommand)
        temp_stdout = "t1.out"
        temp_stderr = "t1.err"

        submit_stdout = open(temp_stdout,"w")
        submit_stderr = open(temp_stderr,"w")
        jobfileobj = open(batchfilename,"r")
        p = subprocess.Popen(args,stdout=submit_stdout,stderr=submit_stderr,stdin=jobfileobj)
        jobfileobj.close()

        p.wait()

        submit_stdout.close()
        submit_stderr.close()

        submit_stdout = open(temp_stdout,"r")
        records = submit_stdout.readlines()
        submit_stdout.close()

        print("records = ")
        print(records)

        print("Extracting LSF jobID from LSF class")
        jobid_pattern = re.compile('\d+')
        print("jobid_pattern = ")
        print(jobid_pattern)
        print("jobid_pattern.findall = ")
        jobid = jobid_pattern.findall(records[0])[0]
        print(jobid)

        return jobid

if __name__ == '__main__':
    print('This is the LSF scheduler class')
