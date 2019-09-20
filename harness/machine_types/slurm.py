#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

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

    def submit_job(self,batchfilename):
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

        p = subprocess.Popen(args,stdout=submit_stdout,stderr=submit_stderr)
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

    def write_jobid_to_status(self,unique_id):
        #
        # Get the current working directory.
        #
        cwd = os.getcwd()

        #
        # Get the 1 head path in the cwd.
        #
        (dir_head1, dir_tail1) = os.path.split(cwd)

        #
        # Now join dir_head1 to make the path. This path should be unique.
        #
        path1 = os.path.join(dir_head1,"Status",unique_id,"job_id.txt")

        #
        # Write the pbs job id to the file.
        #
        fileobj = open(path1,"w")
        string1 = "%20s\n" % (self.get_job_id())
        fileobj.write(string1)
        fileobj.close()

        return path1

if __name__ == '__main__':
    print('This is the SLURM scheduler class')
