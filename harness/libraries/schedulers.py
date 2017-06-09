#! /usr/bin/env python3


#-------------------#
# Import statements #
#-------------------#

import getpass
import pwd
import os
import sys
import re
import string
import computers


#--------------------------------------------#
# Package: schedulers                        #
#--------------------------------------------#
# 
# Classes: 
#
#--------------------------------------------#


#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#
#--------- Class definitions ----------------#
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#



###############################################################################################################
# Class name: base_scheduler
#
# Class documentation:
#
# Inherited classes:
#
# Class variables  :
#
# Public variables :
#
# Public methods   :
#
# Private variables:
#
# Private methods  :
#
###############################################################################################################
class base_scheduler:
    pbs = "pbs"
    loadleveler = "loadlevler"

    def __init__(self,jobname='undefined',jobowner='undefined',jobstate='undefined',jobid='undefined',batchfilename='undefined'):
        self.jobname = jobname
        self.jobowner = jobowner
        self.jobstate = jobstate
        self.jobid = jobid
        self.batchfilename = batchfilename

    def set_jobname(self,name):
        self.jobname = name

    def get_jobname(self):
        return self.jobname

    def set_jobowner(self,name):
        self.jobowner = name

    def get_jobowner(self):
        return self.jobowner

    def set_jobstate(self,state):
        self.jobstate = state

    def get_jobstate(self):
        return self.jobstate

    def set_jobid(self,id):
        self.jobid = id

    def get_jobid(self):
        return self.jobid

    def set_batchfilename(self,name):
        self.batchfilename = name

    def get_batchfilename(self):
        return self.batchfilename

    def is_job_still_in_queue(self):
        print "Stub to check if generic job ", self.get_jobname()," is in queue."

###############################################################################################################
#
# End of class base_scheduler
#
###############################################################################################################

class pbs_scheduler(base_scheduler):

    
    rg_hash = {
           "Job Id"    :  re.compile("Job Id"),
           "Job_Name"  :  re.compile("Job_Name"),
           "job_state" :  re.compile("job_state")
        }

    def __init__(self,pbsjobname='undefined',pbsjobowner='undefined',pbsjobstate='undefined',pbsjobid='undefined',
                 pbsfilename="undefined",pbsprecommand=None):
        base_scheduler.__init__(self)
        self.set_jobname(pbsjobname)
        self.set_jobowner(pbsjobowner)
        self.set_jobstate(pbsjobstate)
        self.set_jobid(pbsjobid)
        self.set_batchfilename(pbsfilename)
	if pbsprecommand:
		self.__submit_command = pbsprecommand + "; qsub -V "
	else:
        	self.__submit_command = "qsub "

    def submit_batch_script(self,batch_file_name):
        commandstring = "qsub " + batch_file_name
        lines = os.popen(commandstring,'r').readlines()
        jobid = string.strip(lines[0])
        return jobid

    def is_job_still_in_queue(self):

        job_in_queue = 0

        pbsfile = "pbsfile" 
        command = "qstat -f > " + pbsfile
        os.system(command)

        # Create file object that contains the output of the "qstat -f" command.
        pbsfileobject = open(pbsfile,'r')
        pbsfile1 = pbsfileobject.readlines()
        pbsfileobject.close()


        name = self.get_jobname()
        reo_jobname = re.compile(name)

        #Check to see if the job is still in the queue. 
        for line in pbsfile1:
            if pbs_scheduler.rg_hash["Job_Name"].search(line):
                if reo_jobname.search(line):
                    job_in_queue = job_in_queue + 1

        return job_in_queue

class pbs_batch_script:

    def __init__(self,pbsbatchfilename,pbstemplatefilename,pbsbatchrunnumber,pbswallclocklimit,
                 pbssize,pbsjobname,pbsbatchqueue,executable,work_dir,starting_dir,results_dir,
                 yodcommand,rg_array):

        #Create an instance of the computer.
        nccs_computer = computers.create_computer()

        #-- Get the home directory of the user --#
        username = getpass.getuser()
        database = pwd.getpwnam(username)
        home_directory = database[5]

        self.__pbsbatchfilename = pbsbatchfilename
        self.__pbstemplatefilename = pbstemplatefilename
        self.__pbsbatchrunnumber = pbsbatchrunnumber
        self.__rg_array = rg_array

        # Path to shell.
        self.__shellpath = "#PBS -S " + nccs_computer.get_cshpath() + "\n"

        #Path to standard output.
        self.__standardout = "#PBS -o " + home_directory + "/.standardout/" + nccs_computer.get_name() + "." + pbsjobname + "." + self.__pbsbatchrunnumber + ".out\n"

        #Path to standard error.
        self.__standarderr = "#PBS -e " + home_directory + "/.standarderr/" + nccs_computer.get_name() + "." + pbsjobname + "." + self.__pbsbatchrunnumber + ".err\n"

        #Wall time
        self.__walltime = "#PBS -l walltime=" + pbswallclocklimit + "\n"

        #PBS job name
        self.__jobname = pbsjobname
        self.__pbsjobname = "#PBS -N " + pbsjobname + "\n"

        #PBS size
        self.__size = pbssize
        self.__pbssize = "#PBS -l size=" + pbssize + "\n"

        #PBS batch
        self.__pbsbatchqueue = "#PBS -q " + pbsbatchqueue + "\n"
      
        #Executable. 
        self.__executable = "set EXECUTABLE = " + executable +"\n"

        #Work dir
        self.__workdir = "set WORK_DIR = " + work_dir + "\n"

        #Starting directory
        self.__startingdirectory = "set STARTINGDIRECTORY = " + starting_dir + "\n"

        #Results directory.
        self.__resultsdir = "set RESULTSDIR = " + results_dir + "\n"

        #The yod command.
        self.__yodcommand = yodcommand

        #Get the pbs account id string.
        self.__pbsaccountid = "#PBS -A " + self.get_pbs_account_id()

    def create_pbs_batch_file(self):
        fileobject = open(self.__pbsbatchfilename,"w")

        #Write the preamble"
        fileobject.write(self.__shellpath)
        fileobject.write(self.__standardout)
        fileobject.write(self.__standarderr)
        fileobject.write(self.__pbsjobname)
        fileobject.write(self.__walltime)
        fileobject.write(self.__pbssize)
        fileobject.write(self.__pbsbatchqueue)
        fileobject.write(self.__pbsaccountid)

        fileobject.write("\n\n\n")
        fileobject.write("#-------------------------------------------\n")
        fileobject.write(self.__executable)
        fileobject.write(self.__workdir)
        fileobject.write(self.__startingdirectory)
        fileobject.write(self.__resultsdir)
        fileobject.write("#-------------------------------------------\n")
        fileobject.write("\n\n\n")

        #Close the file.
        fileobject.close()


        #Read the pbs template file.
        templatefileobject = open("pbs.template.x","r")
        tlines = templatefileobject.readlines()
        templatefileobject.close()

        #---------------------------------------------
        # This section makes the pbs batch script file.
        #----------------------------------------------
        rg_array = [ (re.compile("__yodcommand__"),self.__yodcommand),
                     (re.compile("__jobname__"),self.__jobname),
                   ]
        
        fileobject = open(self.__pbsbatchfilename,"a")
        for record1 in tlines:
            for (regexp,text1) in rg_array:
                record1 = regexp.sub(text1,record1)
            fileobject.write(record1)
        fileobject.close()


        if self.__rg_array:
            fileobject = open(self.__pbsbatchfilename,"r")
            lines = fileobject.readlines()
            fileobject.close()

            rg_array = self.__rg_array
            fileobject = open(self.__pbsbatchfilename,"w")
            for record1 in lines:
                for (regexp,text1) in rg_array:
                    record1 = regexp.sub(text1,record1)
                fileobject.write(record1)
            fileobject.close()
    ###########################################################################


            

    ###########################################################################
    #
    # Function name: get_pbs_account_id
    #
    # Description: Sets the class instance variable "path_to_user_home_directory".
    #
    # Function arguments: Name      Description
    #
    ###########################################################################
    def get_pbs_account_id(self):
        #-- Get the user name --#
        username = getpass.getuser()

        #-- Get the home directory of the user --#
        database = pwd.getpwnam(username)
        home_directory = database[5]

        #make the filename that contains the account id.
        filename = os.path.join(home_directory,".pbsaccountid") 
    

        #Read and return the pbs account id.
        fileobject = open(filename,"r")
        accountid = fileobject.read()
        fileobject.close()

        return accountid
    ###########################################################################

