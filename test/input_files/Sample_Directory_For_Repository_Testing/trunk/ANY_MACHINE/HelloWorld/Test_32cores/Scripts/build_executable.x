#!/usr/bin/env python

import getopt
import sys
import os
import shutil
#import popen2
import subprocess
#
# Author: Arnold Tharrington
# Email: arnoldt@ornl.gov
# National Center of Computational Science, Scientifc Computing Group.
#

#
# This build the simple fortran program.
#

def main():

    #
    # Get the command line arguments.
    #
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hi:p:")

    except getopt.GetoptError:
            usage()
            sys.exit(2)

    #
    # Parse the command line arguments.
    #
    if opts == []:
        usage()
        sys.exit()

    for o, a in opts:
        if o == "-p":
            path_to_workspace = a
        elif o == "-i":
            test_id_string = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()


    #
    # Create the temporary workspace.
    # Save the tempoary workspace for the submit executable.
    #
    create_tmp_workspace(path_to_workspace)

    #
    #--Making the binary.
    #
    make_exit_status = make_binary(path_to_workspace)
    if make_exit_status == 0:
        make_exit_value = 0
    else:
        make_exit_value = 1

    return make_exit_value

def make_binary(path_to_workspace):

    #
    # Get the current working directory.
    #
    cwd = os.getcwd()

    #
    # Get the 2 tail paths in the cwd.
    #
    (dir_head1, dir_tail1) = os.path.split(cwd)
    (dir_head2, dir_tail2) = os.path.split(dir_head1)

    #
    # Get the path to the Source directory for the application.
    #
    path_to_source = os.path.join(dir_head2,"Source")

    #
    # Now make the path to the build directory.
    #
    path_to_build_directory = os.path.join(path_to_workspace,"build_directory")

    #
    #Copy Source to build directory.
    #
#    shutil.copytree(path_to_source,path_to_build_directory)   
    cmd1 = "cp -rf " + path_to_source + " " +  path_to_build_directory
    os.system(cmd1)
    #
    # Change back to build directory.
    #
    os.chdir(path_to_build_directory)

    # Make executable.
    make_command = "make clean  && make all"
    make_exit_status = os.system(make_command)

    return make_exit_status


def usage():
    print("Usage: build_executable.x [-h|--help] -p <path_to_worspace> -i <test_id_string>")
    print("A driver program that the build the binary for the test.")
    print()
    print("-h, --help           Prints usage information.")                              
    print("-p                   The absolute path to the workspace. This path   ")
    print("                     must have the appropiate permissions to permit  ")
    print("                     the user of the test to r,w, and x.             ")
    print("-i                   The test id string. The build program           ")
    print("                     uses this string to make a unique directory     ")
    print("                     within path_to_workspace. We don't want         ")
    print("                     concurrent builds to clobber each other.        ")




def create_tmp_workspace(path1):
    #
    # Fisrt check to see if the path1 does not already exist.
    #
    os.makedirs(path1)

if __name__ == "__main__" :
    main()
