#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from base_scheduler import BaseScheduler
import shlex
import subprocess
import re
import os

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

        #print("records = ")
        #print(records)

        #print("Extracting LSF jobID from LSF class")
        jobid_pattern = re.compile('\d+')
        #print("jobid_pattern = ")
        #print(jobid_pattern)
        #print("jobid_pattern.findall = ")
        jobid = jobid_pattern.findall(records[0])[0]
        self.set_job_id(jobid)
        print("LSF jobID = ",self.get_job_id())

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
    print('This is the LSF scheduler class')
