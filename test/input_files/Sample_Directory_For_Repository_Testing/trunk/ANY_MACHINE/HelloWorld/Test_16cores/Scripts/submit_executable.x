#!/usr/bin/env python

import os
import getopt
import sys
import re
#import popen2
import time
import subprocess
import shlex

from libraries.layout_of_apps_directory import apptest_layout

#
# Author: Arnold Tharrington
# Email: arnoldt@ornl.gov
# National Center of Computational Science, Scientifc Computing Group.
#


def main():
    #
    # Get the command line arguments.
    #
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hi:p:r")

    except getopt.GetoptError:
            usage()
            sys.exit(2)

    #
    # Parse the command line arguments.
    #
    if opts == []:
        usage()
        sys.exit()

    #
    # Initialize some variables.
    #
    batch_recursive_mode = "1"

    for o, a in opts:
        if o == "-p":
            path_to_workspace = a
        elif o == "-i":
            test_id_string = a
        elif o == "-r":
            batch_recursive_mode = "0"
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()

    #
    # Make the batch script.
    #
    batchfilename = make_batch_script(batch_recursive_mode,path_to_workspace,test_id_string)

    #
    # Submit the batch file to the scheduler.
    #
    pbs_job_id = send_to_scheduler(batchfilename)
    print ("Job id =" + str(pbs_job_id))


    #
    #Write pbs job id to job_id.txt in the Status dir.
    #
    write_job_id_to_status(pbs_job_id,test_id_string)


def make_batch_script(batch_recursive_mode,path_to_workspace,test_id_string):
    #
    # Define the batch file names.
    #
    batchtemplatefilename = "pbs.template.x"
    batchfilename = "hw.batch.x"

    #
    # Define the parse definitons and the regular expressions.
    #
    nccstestharnessmodule = os.environ["RGT_NCCS_TEST_HARNESS_MODULE"]
    rgtenvironmentalfile = os.environ["RGT_ENVIRONMENTAL_FILE"]
    jobname = "hellotest"
    walltime = "00:05:00"
    size = "16"
    batchqueue = "batch"
    pbsaccountid = os.environ["RGT_PBS_JOB_ACCNT_ID"]
    pathtoexecutable = os.path.join(path_to_workspace, apptest_layout.test_build_dirname, "helloworld.x")
    startingdirectory = os.getcwd()
    resultsdir = get_path_to_results_dir(test_id_string)
    workdir = os.path.join(path_to_workspace, apptest_layout.test_run_dirname)
    resubmitme = batch_recursive_mode
    joblaunchcommand = "aprun -n 16 $EXECUTABLE 1> std.out.txt 2> std.err.txt"

    rg_array = [
                (re.compile("__jobname__"),jobname),
                (re.compile("__walltime__"),walltime),
                (re.compile("__size__"),size),
                (re.compile("__nccstestharnessmodule__"),nccstestharnessmodule),
                (re.compile("__rgtenvironmentalfile__"),rgtenvironmentalfile),
                (re.compile("__batchqueue__"),batchqueue),
                (re.compile("__pbsaccountid__"),pbsaccountid),
                (re.compile("__pathtoexecutable__"),pathtoexecutable),
                (re.compile("__startingdirectory__"),startingdirectory),
                (re.compile("__resultsdir__"),resultsdir),
                (re.compile("__workdir__"),workdir),
                (re.compile("__joblaunchcommand__"),joblaunchcommand),
                (re.compile("__resubmitme__"),resubmitme),
                (re.compile("__unique_id_string__"),test_id_string),
                (re.compile("__batchfilename__"),batchfilename),
               ]

    #
    # Read the lines of the batch template file.
    #
    templatefileobject = open(batchtemplatefilename,"r")
    tlines = templatefileobject.readlines()
    templatefileobject.close()

    #
    # Here is where we actually make the pbs batch file from pbs.template.x.
    #
    fileobject = open(batchfilename,"w")
    for record1 in tlines:
        for (regexp,text1) in rg_array:
            record1 = regexp.sub(text1,record1)
        fileobject.write(record1)
    fileobject.close()

    return batchfilename


def get_path_to_results_dir(test_id_string):
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
    path1 = os.path.join(dir_head1, apptest_layout.test_run_archive_dirname, test_id_string)

    return path1

def write_job_id_to_status(pbs_job_id,test_id_string):
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
    path1 = os.path.join(dir_head1, apptest_layout.test_status_dirname, test_id_string, apptest_layout.job_id_filename)

    #
    # Write the pbs job id to the file.
    #
    fileobj = open(path1,"w")
    string1 = "%20s\n" % (pbs_job_id)
    fileobj.write(string1)
    fileobj.close()

    return path1


def send_to_scheduler(batchfilename):
    qcommand = "qsub " + batchfilename

#    b = popen2.Popen3(qcommand)
#    jobid_array = qjob.fromchild.readlines()
#    jobid = jobid_array[0]

    t1="t1.out"
    t2="t1.err"

    my_stdout = open(t1,"w")
    my_stderr = open(t2,"w")
    args = shlex.split(qcommand)
    p = subprocess.Popen(args,stdout=my_stdout,stderr=my_stderr)
    p.wait()

    my_stdout.close()
    my_stderr.close()

    my_stdout = open(t1,"r")
    records = my_stdout.readlines()
    jobid = records[0].strip()
    my_stdout.close()

#    args = shlex.split(qcommand)
#    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    p.wait()
#    records = p.stdout.readlines()
#    jobid = records[0].strip()

    return jobid



def usage():
    print("Usage: submit_executable.x [-h|--help] -p <path_to_worspace> -i <test_id_string>")
    print("")
    print("A driver program that the submits the binary thru batch for the testing.")
    print("The submit program also writes the job id of the submitted batch job to the file")
    print("'Status/<test_id_string>/job_id.txt'. The only line in job_id.txt is the job id.")
    print()
    print("-h, --help           Prints usage information.")
    print("-p                   The absolute path to the workspace. This path   ")
    print("                     must have the appropiate permissions to permit  ")
    print("                     the user of the test to r,w, and x.             ")
    print("-i                   The test id string. The build program           ")
    print("                     uses this string to make a unique directory     ")
    print("                     within path_to_workspace. We don't want         ")
    print("                     concurrent builds to clobber each other.        ")
    print("                     The submit program uses this string to write the")
    print("                     job schedule id to 'Status/<test_id_string>/job_id.txt.")
    print("-r                   The batch script will resubmit itself, otherwise")
    print("                     only 1 instance will be submitted               ")


if __name__ == "__main__" :
    main()
