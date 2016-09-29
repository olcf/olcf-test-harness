#! /usr/bin/env python


#-------------------#
# Import statements #
#-------------------#
import os
import socket
import schedulers 
import string
import re
import time
import datetime
from Locks.rgt_locks import *
from Data_Files.report_files import *

#--------------------------------------------#
# Package:  computers.py                     #
#--------------------------------------------#
# 
# Classes: base_computer
#          rizzo_computer
#--------------------------------------------#


#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#
#--------- Class definitions ----------------#
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#



###############################################################################################################
# Class name: base_computer
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
class base_computer:

    list_of_computers = ["ram","jaguar","phoenix","robin","rizzo"]

    #######################################################################
    #
    # Function name: __init__
    #
    # Description: Init constructor call.
    #
    # Function arguments:         Name            Description
    #
    #
    ########################################################################
    def __init__(self):
       self.name = "none"
       self.scratchspace_location = "/tmp"
       self.batch_scheduler_name = "none"
       self.batch_scheduler = "none"
       self.submitted_batch_jobs = []
       self.cshpath = "/usr/bin/csh"
    ########################################################################



    ########################################################################
    #
    # Function name: get_job_id
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def get_job_id(self):
        return "Stub id\n"
    ########################################################################



    ########################################################################
    #
    # Function name: set_name
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def set_name(self,name):
        self.name = name
    ########################################################################



    ########################################################################
    #
    # Function name: get_name
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def get_name(self):
        return self.name
    ########################################################################



    ########################################################################
    #
    # Function name: set_scratchspace_location
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def set_scratchspace_location(self,name):
        self.scratchspace_location = name
    ########################################################################



    ########################################################################
    #
    # Function name: get_scratchspace_location
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def get_scratchspace_location(self):
        return self.scratchspace_location
    ########################################################################



    ########################################################################
    #
    # Function name: set_batchschdeuler_name
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def set_batchschdeuler_name(self,name):
        self.batch_scheduler_name = name
    ########################################################################



    ########################################################################
    #
    # Function name: get_batchschdeuler_name
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def get_batchschdeuler_name(self):
        return self.batch_scheduler_name
    ########################################################################



    ########################################################################
    #
    # Function name: make_executable
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def make_software_bin(self,make_binary_path,history_file_path,lock_location_id,iteration_no=0):

        #print "\n\n\n"
        #print "//////////////////////////////////"
        #print "Start of make_software_bin"
        #print "//////////////////////////////////"
        #Get the current working directory
        starting_directory = os.getcwd()

        # Get the name of the binary and the parent path.
        parent_make_binary_path = os.path.dirname(make_binary_path)
        binary = "nohup " + os.path.basename(make_binary_path)
        binary = binary + " " + history_file_path + " " + lock_location_id[0] + " " + str(lock_location_id[1])  +  " " + str(iteration_no) + " &"

        #Change to the directory of the parent path.
        os.chdir(parent_make_binary_path)

        # Execute make script
        #print "Full command line: ", binary
        os.system(binary)

        #Change back to the starting directory.
        os.chdir(starting_directory)

        #print "//////////////////////////////////"
        #print "//////////////////////////////////"
    ########################################################################



    ########################################################################
    #
    # Function name: run_software_bin
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def run_software_bin(self,run_binary_path,path_to_binary,history_file_path,
                         results_dir,scratch_dir,path_to_standard_results,lock_location_id,
                         iteration_number=0):

        # Get the name and location of the script that make the
        # the pbs file that which runs our test.
        parent_run_binary_path = os.path.dirname(run_binary_path)
        script1 = os.path.basename(run_binary_path)

        #print "\n\n\n"
        #print "//////////////////////////////////"
        #print "Start of run_software_bin"
        #print "//////////////////////////////////"

        #print "In run_software_bin"
        #print "starting_directory ", os.getcwd()
        #print "run_binary_path :",run_binary_path
        #print "path_to_binary  :",path_to_binary
        #print "history_file_path :",history_file_path
        #print "results_dir :",results_dir
        #print "scratch_dir :",scratch_dir

        # Make the command line arguments.
        argument1 = "--scratchdir=" + scratch_dir
        argument2 = "--history_file_path=" + history_file_path
        argument3 = "--results_dir=" + results_dir
        argument4 = "--starting_dir=" + parent_run_binary_path
        argument5 = "--pathtobinary=" + path_to_binary
        argument6 = "--pathtostandardresults=" + path_to_standard_results
        argument7 = "--pathtolock=" +  lock_location_id[0]
        argument8 = "--lockid=" +  str(lock_location_id[1])
        argument9 = "--iteration_number=" + str(iteration_number)

        # Make the full command line.
        fullcommand = "nohup " + script1 + " " + argument1 + " " + argument2 + " " + argument3 
        fullcommand = fullcommand + " " + argument4 + " " + argument5 + " " + argument6 
        fullcommand = fullcommand + " " + argument7 + " " + argument8 + " " + argument9 + " &"
        #print "Full command line: ", fullcommand

        #Get the current working directory
        primary_directory = os.getcwd()

        #Change to the directory of the parent path.
        os.chdir(parent_run_binary_path)

        # Execute run script
        os.system(fullcommand)

        #Change back to the starting directory.
        os.chdir(primary_directory)

        #print "//////////////////////////////////"
        #print "//////////////////////////////////"

    ########################################################################



    ########################################################################
    #
    # Function name: launch_stability_job
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def launch_stability_job(self,spack,iteration_no=0):
        lock_mr = self.__st_make_and_run_executable(spack,iteration_no=iteration_no)

        return lock_mr
    ########################################################################
    

    ########################################################################
    #
    # Function name: __make_and_run_executable
    #
    # Description: 
    #
    # Function arguments: Name                Description
    #
    #                     self
    ########################################################################
    def __st_make_and_run_executable(self,spack,iteration_no=0):
        #print "\n\n\n"
        #print "==============================="
        #print "In __st_make_and_run_executable"
        #print "==============================="
        #The time to wait between making and running the job.
        sleeptime = 5.00

        # Get the main lock id.
        main_lock_id = spack.get_main_lock_id()

        # Create the lock for making and running.
        lock_path = spack.subtest_path()
        unique_id = spack.get_lock_id() 
        lock_mr = make_and_run_lock(lock_id=unique_id,lock_location=lock_path)
 
        # Load the main stability report file.
        rgt_report = load_report_file(main_lock_id)
        rgt_report.modify(unique_id,
                          spack.get_name_of_st_software(),
                          spack.get_name_of_st_subtest())
        

        # Make the binary
        make_binary_path = spack.make_only_path()
        history_file_path = spack.history_text_path()
        lock_location_id =lock_mr.path_id()

        #print "lock_mr lock path: ",lock_location_id[0]
        #print "lock_mr lock id : ",lock_location_id[1]
        #print "history_file_path : ", history_file_path
        #print "make_binary_path : ", make_binary_path
        self.make_software_bin(make_binary_path,history_file_path,lock_location_id,iteration_no)

        #Sleep for a moment.
        time.sleep(sleeptime)

        # Run the binary.
        run_only_script_location = spack.run_only_path()
        history_text_location = spack.history_text_path()
        results_directory = spack.get_results_dir()
        scratch_directory = spack.get_scratchspace_location()
        binpath1 = spack.get_path_to_binary()
        pathtostandardresults1 = spack.path_to_standard_results()

        #print "run_only_script_location : ", run_only_script_location
        #print "history_text_location : ", history_text_location
        #print "results_directory : ", results_directory 
        #print "scratch_directory : ",scratch_directory  
        #print "binpath1 : ",binpath1 
        #print "pathtostandardresults1 : ",pathtostandardresults1 

        self.run_software_bin(run_binary_path=run_only_script_location,
                              path_to_binary=binpath1,
                              history_file_path=history_text_location,
                              results_dir=results_directory,
                              scratch_dir=scratch_directory,
                              path_to_standard_results=pathtostandardresults1,
                              lock_location_id=lock_mr.path_id(),
                              iteration_number=iteration_no)

        return lock_mr
        #print "==============================="
    ########################################################################




###############################################################################################################
#
# End of class base_computer
#
###############################################################################################################



###############################################################################################################
# Class name: rizzo_computer
#
# Inherited classes: base_computer
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
class rizzo_computer (base_computer):

    #######################################################################
    #
    # Default initialization method.
    #
    #######################################################################
    def __init__(self):
        base_computer.__init__(self)
        self.set_name("rizzo")
        self.set_scratchspace_location("/lustre/scratch")
        self.set_batchschdeuler_name(schedulers.base_scheduler.pbs)
        self.__batchscheduler = schedulers.pbs_scheduler()
        self.cshpath = "/usr/bin/csh"
    #######################################################################


    ########################################################################
    #
    # Function name: set_batchschdeuler
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def set_batchschdeuler(self,scheduler):
        self.__batchscheduler = scheduler
    ########################################################################


    ########################################################################
    #
    # Function name: get_cshpath
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def get_cshpath(self):
        return self.cshpath
    ########################################################################


    ########################################################################
    #
    # Function name: submit_batch_script
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def submit_batch_script(self,batch_file_name):
        jobid = self.__batchscheduler.submit_batch_script(batch_file_name)
        return jobid
    ########################################################################


    ########################################################################
    #
    # Function name: numbercoresoption
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def numbercoresoption(self,numberofnodes,mode):
            nmcores = str(numberofnodes*1) + "-SN" 

            if mode == "SingleCore":
                nmcores = str(numberofnodes*1) + " -SN"
            elif mode == "DualCore":
                nmcores = str(numberofnodes*2) + " -VN"

            return nmcores
    ########################################################################


    ########################################################################
    #
    # Function name: numbercoremultiplier
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def numbercoremultiplier(self,mode):

            multiplier = 1

            if mode == "SingleCore":
                multiplier = 1
            elif mode == "DualCore":
                multiplier = 2
            elif mode == "QuadCore":
                multiplier = 4

            return multiplier
    ########################################################################


    ########################################################################
    #
    # Function name: programming_environment
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def programming_environment_command(self):
        return "/opt/modules/3.1.6/bin/modulecmd tcsh list"

    ########################################################################


###############################################################################################################
#
# End of class rizzo computer
#
###############################################################################################################




###############################################################################################################
# Class name: ram_computer
#
# Inherited classes: base_computer
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
class ram_computer (base_computer):

    #######################################################################
    #
    # Default initialization method.
    #
    #######################################################################
    def __init__(self):
        base_computer.__init__(self)
        self.set_name("ram")
        self.set_scratchspace_location("/tmp/work")
        self.set_batchschdeuler_name(schedulers.base_scheduler.pbs)
    #######################################################################


###############################################################################################################
#
# End of class ram computer
#
###############################################################################################################



###############################################################################################################
# Class name: jaguar_computer
#
# Inherited classes: base_computer
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
class jaguar_computer (base_computer):

    #######################################################################
    #
    # Default initialization method.
    #
    #######################################################################
    def __init__(self):
        base_computer.__init__(self)
        self.set_name("jaguar")
        self.set_scratchspace_location("/lustre/scratch")
        self.set_batchschdeuler_name(schedulers.base_scheduler.pbs)
        self.__batchscheduler = schedulers.pbs_scheduler()
        self.cshpath = "/usr/bin/csh"
    #######################################################################


    ########################################################################
    #
    # Function name: set_batchschdeuler
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def set_batchschdeuler(self,scheduler):
        self.__batchscheduler = scheduler
    ########################################################################


    ########################################################################
    #
    # Function name: get_cshpath
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    #                     self
    ########################################################################
    def get_cshpath(self):
        return self.cshpath
    ########################################################################


    ########################################################################
    #
    # Function name: submit_batch_script
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def submit_batch_script(self,batch_file_name=None,batch_job=None):
        if batch_file_name:
            jobid = self.__batchscheduler.submit_batch_script(batch_file_name)
            return jobid

        elif batch_job:
            batchfilename = batch_job.get_batchfilename()
            jobid = self.__batchscheduler.submit_batch_script(batchfilename)
            batch_job.set_jobid(jobid)
            self.submitted_batch_jobs = self.submitted_batch_jobs + [batch_job]
    ########################################################################


    ########################################################################
    #
    # Function name: numbercoresoption
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def numbercoresoption(self,numberofnodes,mode):
            nmcores = str(numberofnodes*1) + "-SN" 

            if mode == "SingleCore":
                nmcores = str(numberofnodes*1) + " -SN"
            elif mode == "DualCore":
                nmcores = str(numberofnodes*2) + " -VN"

            return nmcores
    ########################################################################


    ########################################################################
    #
    # Function name: numbercoremultiplier
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def numbercoremultiplier(self,mode):

            multiplier = 1

            if mode == "SingleCore":
                multiplier = 1
            elif mode == "DualCore":
                multiplier = 2
            elif mode == "QuadCore":
                multiplier = 4

            return multiplier
    ########################################################################


    ########################################################################
    #
    # Function name: programming_environment
    #
    # Description: 
    #
    # Function arguments: Name        Description
    #
    ########################################################################
    def programming_environment_command(self):
        return "/opt/modules/3.1.6/bin/modulecmd tcsh list"

    ########################################################################




###############################################################################################################
#
# End of class jaguar computer
#
###############################################################################################################



########################################################################
#
# Function name: create_computer
#
# Description: 
#
# Function arguments: Name        Description
#
########################################################################
def create_computer():
    hostname =  gethostname()

    ram_regep = re.compile("^ram",re.I)
    rizzo_regep = re.compile("^rizzo",re.I)
    jaguar_regep = re.compile("^jaguar",re.I)
    yodjaguar_regep = re.compile("^yodjag",re.I)

    #--Are we on rizzo?
    if  rizzo_regep.match(hostname):
        return rizzo_computer()
    #--Are we on ram?
    elif ram_regep.match(hostname):
        return ram_computer()
    #--Are we on jaguar?
    elif jaguar_regep.match(hostname):
        return jaguar_computer()
    #--Are we on a jaguar yod node?
    elif yodjaguar_regep.match(hostname):
        return jaguar_computer()
    else:
        string1 =  "Computer " + hostname + " not defined."
        print string1
########################################################################



########################################################################
#
########################################################################
def getdnsnames(name):
    d = socket.gethostbyaddr(name)
    names = [ d[0] ] + d[1] + d[2]
    return names
########################################################################



########################################################################
#
########################################################################
def resolve(name):
    names = getdnsnames(name)
    for dnsname in names:
        if '.' in dnsname:
            fullname = dnsname
            break
    else:
        fullname = name
    return fullname
########################################################################



########################################################################
#
########################################################################
def gethostname():
    fullname = socket.gethostname()
    if '.' not in fullname:
        fullname = resolve(fullname)

    return fullname
########################################################################
