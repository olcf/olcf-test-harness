#! /usr/bin/env python3
import os
import string

#--------------------------------------------#
# Package:  job_status.py                    #
#--------------------------------------------#
# 
# Classes: base_rgt_job_status
#
#--------------------------------------------#


#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#
#--------- Class definitions ----------------#
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#



###############################################################################################################
# Class name: base_rgt_job_status
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
class base_rgt_job_status:
    job_status_file_name = "status.txt"
    fail_job = "Fail"
    pass_job = "Pass"
    inconclusive_job = "Inconclusive"

    #######################################################################################################
    #
    # Function name: __init__
    #
    # Description: Init constructor call.
    #
    # Function arguments:         Name            Description
    #
    #
    #######################################################################################################
    def __init__(self):
        pass
    #######################################################################################################


###############################################################################################################




###############################################################################################################
class new_job_status(base_rgt_job_status):

    #######################################################################################################
    #
    # Function name: __init__
    #
    # Description: Init constructor call.
    #
    # Function arguments:         Name            Description
    #
    #
    #######################################################################################################
    def __init__(self):
        fname = base_rgt_job_status.job_status_file_name

        if not os.path.exists(fname):
            fname_obj = open(fname,"w")
            string1 = "%(it)10s %(jid)20s %(lid)20s %(status)20s\n" % {"it":"Iteration","jid":"Job ID","lid":"Lock ID", "status": "Job Status"}
            fname_obj.write(string1)

            string1 = "%s\n" % (73*"_")
            fname_obj.write(string1)

            fname_obj.close()
    #######################################################################################################


    #######################################################################################################
    #
    # Function name: update_job_status_list
    #
    # Description: Write the state data of the run process
    #
    # Function arguments:         Name            Description
    #
    #
    #######################################################################################################
    def update_job_status_list(self,iteration_no,jid,lid):
    
        fname = base_rgt_job_status.job_status_file_name
        fname_obj = open(fname,"a")
    
        string1 = "%(it)10d %(jid)20s %(lid)20s\n" % {"it":iteration_no, "jid":jid, "lid":lid}
        fname_obj.write(string1)
    
        fname_obj.close()
    #######################################################################################################
    

    #######################################################################################################
    #
    # Function name: modify_job_status
    #
    # Description: Modify the status of the job.
    #
    # Function arguments:         Name            Description
    #
    #
    #######################################################################################################
    def modify_job_status(self,jid=None,jstatus=base_rgt_job_status.inconclusive_job):
    
        fname = base_rgt_job_status.job_status_file_name
        fname_obj = open(fname,"r")
        lines = fname_obj.readlines()
        fname_obj.close()

        if jstatus == "0":
            jobstatus = base_rgt_job_status.fail_job
        elif jstatus == "1":
            jobstatus = base_rgt_job_status.pass_job
        else:
            jobstatus = base_rgt_job_status.inconclusive_job
        
        ip = 0
        for line in lines:
            ip = ip + 1
            if ip >= 3:

                line1 = string.rstrip(line)
                words1 = string.split(line1)
                jid1 = words1[1]
                print "jid :  ",jid
                print "jid1:  ",jid1
                if jid == jid1:
                    print "Modifying lines"
                    lines[ip-1] = "%(line1)s %(pass_fail)20s\n" % {"line1":line1, "pass_fail":jstatus}
                    print lines[ip-1]
            
        fname_obj = open(fname,"w")
        fname_obj.writelines(lines)
        fname_obj.close()
    #######################################################################################################
    


###############################################################################################################

