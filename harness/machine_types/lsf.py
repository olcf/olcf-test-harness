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


class LSF(BaseScheduler):

    """ LSF class represents an LSF scheduler. """

    def __init__(self, logger):
        self.__name = 'LSF'
        self.__submitCmd = 'bsub'
        self.__statusCmd = 'bjobs'
        self.__deleteCmd = 'bkill'
        self.__walltimeOpt = '-W'
        self.__numTasksOpt = '-n'
        self.__jobNameOpt = '-N'
        self.__templateFile = 'lsf.template.x'
        self.__logger = logger
        BaseScheduler.__init__(self, self.__name,
                               self.__submitCmd, self.__statusCmd, self.__deleteCmd,
                               self.__walltimeOpt, self.__numTasksOpt, self.__jobNameOpt,
                               self.__templateFile)

    def submit_job(self, batchfilename):
        self.__logger.doInfoLogging(f"Submitting job from LSF class using batchfilename {batchfilename}")

        qargs = ""
        if 'RGT_SUBMIT_QUEUE' in os.environ:
            qargs += " -q " + os.environ.get('RGT_SUBMIT_QUEUE')
        elif 'RGT_BATCH_QUEUE' in os.environ:
            qargs += " -q " + os.environ.get('RGT_BATCH_QUEUE')

        if 'RGT_SUBMIT_ARGS' in os.environ:
            qargs += " " + os.environ.get('RGT_SUBMIT_ARGS')

        if 'RGT_SUBMIT_ACCT' in os.environ:
            qargs += " -P " + os.environ.get('RGT_SUBMIT_ACCT')
        elif 'RGT_PROJECT_ID' in os.environ:
            qargs += " -P " + os.environ.get('RGT_PROJECT_ID')

        qcommand = self.__submitCmd + " " + qargs + " " + batchfilename
        self.__logger.doInfoLogging(f"{qcommand}")

        args = shlex.split(qcommand)
        temp_stdout = "submit.out"
        temp_stderr = "submit.err"

        submit_stdout = open(temp_stdout,"w")
        submit_stderr = open(temp_stderr,"w")

        if 'RGT_LSF_SUBMIT_AS_STDIN' in os.environ and \
                str(os.environ['RGT_LSF_SUBMIT_AS_STDIN']) == '0':
            p = subprocess.Popen(args,stdout=submit_stdout,stderr=submit_stderr)
            p.wait()
        else:
            with open(batchfilename,"r") as jobfileobj:
                p = subprocess.Popen(args,stdout=submit_stdout,stderr=submit_stderr,stdin=jobfileobj)
                p.wait()

        submit_stdout.close()
        submit_stderr.close()

        submit_stdout = open(temp_stdout,"r")
        records = submit_stdout.readlines()
        submit_stdout.close()

        if p.returncode == 0:
            jobid_pattern = re.compile(r'\d+')
            jobid = jobid_pattern.findall(records[0])[0]
            self.set_job_id(jobid)
            self.__logger.doErrorLogging(f"LSF jobID = {self.get_job_id()}")
        else:
            with open(temp_stderr,"r") as submit_stderr:
                self.__logger.doCriticalLogging(f"{submit_stderr.read()}")

        return p.returncode

    def set_job_id_from_environ(self):
        self.__logger.doInfoLogging("Setting job id from environment in LSF class")
        jobvar = 'LSB_JOBID'
        if jobvar in os.environ:
            self.set_job_id(os.environ[jobvar])
        else:
            self.__logger.doErrorLogging(f'{jobvar} not set in environment!')
        return

if __name__ == '__main__':
    print('This is the LSF scheduler class')
