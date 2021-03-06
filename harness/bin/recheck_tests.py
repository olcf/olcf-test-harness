#! /usr/bin/env python3


import argparse
import os
import sys
import subprocess

from libraries.layout_of_apps_directory import apptest_layout

def main():

    parser = argparse.ArgumentParser(description='Calculate the mean of the metric..')


    parser.add_argument("--testnames",
                         nargs='+',
                         required=True,
                         help="The name of the test to check"
                        )

    args = parser.parse_args()
    for test in args.testnames:
        doReTest(test)

def doReTest(test_name):
    #-----------------------------------------------------
    #                                                    -
    #                                                    -
    #-----------------------------------------------------
    cwd = os.getcwd()

    #-----------------------------------------------------
    # Get the path to the Scripts directory.             -
    #                                                    -
    #-----------------------------------------------------
    path_to_scripts_dir = os.path.join(cwd, test_name, apptest_layout.test_scripts_dirname)

    #-----------------------------------------------------
    # Get the unique id of test instances.               -
    #                                                    -
    #-----------------------------------------------------
    path_to_run_archive_dir = os.path.join(cwd, test_name, apptest_layout.test_run_archive_dirname)
    unique_ids =  os.listdir(path_to_run_archive_dir)

    stdoutfile = "recheck.stdout.txt"
    stderrfile = "recheck.stderr.txt"
    header =  "#\n"
    header += "#Test: {}\n".format(test_name)
    header += "#\n"
    print(header)
    for id in unique_ids:
        path_to_results = os.path.join(path_to_run_archive_dir, id)
        os.chdir(path_to_scripts_dir)
        unix_command = "check_executable_driver.py -p {} -i {}".format(path_to_results, id)
        message = "Checking test instance: {}\n".format(str(id))
        print(message)
        with open(stdoutfile,"w") as out:
            with open(stderrfile,"w") as err:
                subprocess.check_call(unix_command,shell=True,stdout=out,stderr=err)

        message = "    {}".format("standard output:")
        print(message)
        print("    ----------------")
        file_obj = open(stdoutfile,"r")
        records = file_obj.readlines()
        for tmp_record in records:
            message = "    {}".format(tmp_record.strip())
            print (message)
        file_obj.close()
        print


        message = "    {}".format("standard error:")
        print(message)
        print("    ----------------")
        file_obj = open(stderrfile,"r")
        records = file_obj.readlines()
        for tmp_record in records:
            message = "    {}".format(tmp_record.strip())
            print (message)
        file_obj.close()
        print

        os.chdir(initial_dir)


    print
if __name__ == "__main__":
    main()
