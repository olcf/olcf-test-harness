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

class SLURM(BaseScheduler):

    """ SLURM class represents an SLURM scheduler. """

    def __init__(self, logger):
        self.__name = 'SLURM'
        self.__submitCmd = 'sbatch'
        self.__statusCmd = 'squeue'
        self.__deleteCmd = 'scancel'
        self.__walltimeOpt = '-t'
        self.__numTasksOpt = '-n'
        self.__jobNameOpt = '-J'
        self.__templateFile = 'slurm.template.x'
        self.__logger = logger
        BaseScheduler.__init__(self, self.__name,
                               self.__submitCmd, self.__statusCmd, self.__deleteCmd,
                               self.__walltimeOpt, self.__numTasksOpt, self.__jobNameOpt,
                               self.__templateFile)

    def submit_job(self, batchfilename):
        self.__logger.doInfoLogging(f"Submitting job from SLURM class using batchfilename {batchfilename}")

        qargs = ""
        if 'RGT_SUBMIT_QUEUE' in os.environ:
            qargs += " -p " + os.environ.get('RGT_SUBMIT_QUEUE')
        elif 'RGT_BATCH_QUEUE' in os.environ:
            qargs += " -p " + os.environ.get('RGT_BATCH_QUEUE')

        if 'RGT_SUBMIT_ARGS' in os.environ:
            qargs += " " + os.environ.get('RGT_SUBMIT_ARGS')

        if 'RGT_SUBMIT_ACCT' in os.environ:
            qargs += " -A " + os.environ.get('RGT_SUBMIT_ACCT')
        elif 'RGT_PROJECT_ID' in os.environ:
            qargs += " -A " + os.environ.get('RGT_PROJECT_ID')

        # Fix issue #181 -- reset SHLVL to 1 every time we submit
        # Since this is not an interactive session, SHLVL is functionally useless
        if 'SHLVL' in os.environ:
            os.environ['SHLVL'] = "1"

        qcommand = self.__submitCmd + " " + qargs + " " + batchfilename
        self.__logger.doInfoLogging(f"{qcommand}")

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

        if p.returncode == 0:
            jobid_pattern = re.compile('\d+')
            jobid = jobid_pattern.findall(records[0])[0]
            self.set_job_id(jobid)
            self.__logger.doErrorLogging(f"SLURM jobID = {self.get_job_id()}")
        else:
            with open(temp_stderr,"r") as submit_stderr:
                self.__logger.doCriticalLogging(f"{submit_stderr.read()}")

        return p.returncode

    def set_job_id_from_environ(self):
        self.__logger.doInfoLogging("Setting job id from environment in SLURM class")
        jobvar = 'SLURM_JOB_ID'
        if jobvar in os.environ:
            self.set_job_id(os.environ[jobvar])
        else:
            self.__logger.doErrorLogging(f'{jobvar} not set in environment!')


if __name__ == '__main__':
    print('This is the SLURM scheduler class')
