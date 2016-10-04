#! /usr/bin/env python3
import glob
import os

"""
SYNOPSIS

    	lists_tests.py 

DESCRIPTION

        The program creates a rgt.input template file. The 
        user sets the variable "HARNESS_APPLICATION_PATH" to point to the
        location of the svn checked out applications directory. This program
        will form a skeletal template of the applications and tests at location
        set by "HARNESS_APPLICATION_PATH".

"""

#
# The path to the application directory level.
#
HARNESS_APPLICATION_PATH = "/lustre/widow/scratch/pfaccept/Titan_Acceptance_2012/Stability_12_Dec_2012/Applications/*"

def main():     
        #
        # Ensure the path stored in "HARNESS_APPLICATION_PATH" exists.
        #
        if not  os.path.exists(HARNESS_APPLICATION_PATH):
                tmp_string = "The path {0} does not exist.".format(HARNESS_APPLICATION_PATH)
                print tmp_string

        #
        # A List of directories and file to ignore that are at the Application/Test level.
        #
        directories_to_ignore = [ "Source",
                                  "application_info.txt",
                                  "totalruns.dat",
                                  "README.txt",
                                  "tar_results.sh",
                                  "build_notes.txt",
                                  "totalruns_cpu1.dat",
                                  "totalruns_cpu16.dat",
                                  "totalruns_gpu1.dat",
                                  "totalruns_gpu16.dat"
                                ]

        #
        # Form a list of directories at the application directory level.
        #
        app_dir_list = glob.glob(HARNESS_APPLICATION_PATH)

        #
        # For each application make a list of all tests.
        #
        app_test = []
        for application in app_dir_list:
                application_path = application + "/*"
                apptests = glob.glob(application_path)
                for test in apptests:
                        (head,tail) = os.path.split(test)

                        if (tail not in directories_to_ignore):
                                test = tail
                                (dummy_string,app) = os.path.split(head)
                                app_test = app_test + [[app,test]]


        #
        # Create a skeletal rgt.input file with all the tests.
        #
        rgt_template_file = "rgt_input_template.txt"
        file_obj = open(rgt_template_file,"w")
        for tmp_app_test in app_test:
                tmp_string = "Test = {0} {1}\n".format(tmp_app_test[0], tmp_app_test[1])
                file_obj.write(tmp_string)


if __name__ == "__main__":
        main()
