#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

import os
import shlex
import subprocess
import re

from .base_scheduler import BaseScheduler

class PBS(BaseScheduler):

    def __init__(self):
        self.__name = 'PBS'
        self.__submitCmd = 'qsub'
        self.__statusCmd = 'qstat'
        self.__deleteCmd = 'qdel'
        self.__walltimeOpt = '-l walltime='
        self.__numTasksOpt = '-l nodes='
        self.__jobNameOpt = '-N'
        self.__templateFile = 'pbs.template.x'
        BaseScheduler.__init__(self, self.__name,
                               self.__submitCmd, self.__statusCmd, self.__deleteCmd,
                               self.__walltimeOpt, self.__numTasksOpt, self.__jobNameOpt,
                               self.__templateFile)

    def submit_job(self, batchfilename):
        print("Submitting job from PBS class using batchfilename " + batchfilename)

        qargs = ""
        if 'RGT_SUBMIT_QUEUE' in os.environ:
            qargs += " -q " + os.environ.get('RGT_SUBMIT_QUEUE')
        elif 'RGT_BATCH_QUEUE' in os.environ:
            qargs += " -q " + os.environ.get('RGT_BATCH_QUEUE')

        if 'RGT_SUBMIT_ARGS' in os.environ:
            qargs += " " + os.environ.get('RGT_SUBMIT_ARGS')

        if 'RGT_SUBMIT_ACCT' in os.environ:
            qargs += " -A " + os.environ.get('RGT_SUBMIT_ACCT')
        elif 'RGT_PROJECT_ID' in os.environ:
            qargs += " -A " + os.environ.get('RGT_PROJECT_ID')

        qcommand = self.__submitCmd + " " + qargs + " " + batchfilename
        print(qcommand)

        args = shlex.split(qcommand)
        temp_stdout = "submit.out"
        temp_stderr = "submit.err"

        submit_stdout = open(temp_stdout,"w")
        submit_stderr = open(temp_stderr,"w")

        p = subprocess.Popen(args,stdout=submit_stdout,stderr=submit_stderr)
        p.wait()

        submit_stdout.close()
        submit_stderr.close()

        submit_stdout = open(temp_stdout,"r")
        records = submit_stdout.readlines()
        submit_stdout.close()

        if p.returncode == 0:
            jobid_pattern = re.compile('\d+')
            jobid = jobid_pattern.findall(records[0])[0]
            self.set_job_id(jobid)
            print("PBS jobID = ",self.get_job_id())
        else:
            with open(temp_stderr,"r") as submit_stderr:
                print(submit_stderr.read())

        return p.returncode

    def set_job_id_from_environ(self):
        print("Setting job id from environment in PBS class")
        jobvar = 'PBS_JOBID'
        if jobvar in os.environ:
            self.set_job_id(os.environ[jobvar])
        else:
            print(f'{jobvar} not set in environment!')

if __name__ == '__main__':
    print('This is the PBS scheduler class')
