#!/usr/bin/env python

import copy
import os

class  apps_test_directory_layout(object):

    path_to_svn_repository = os.environ["RGT_PATH_TO_SVN_REPS"]
    organization = os.environ["RGT_ORGANIZATION"] 
    machine = os.environ["RGT_MACHINE_NAME"] 
    top_level_applications ="applications"
    kill_file = "kill_test"
    rc_file = ".testrc"

    directory_structure = {
                            "application"                          : ["__application__"],
                            "application_info.txt"                 : ["__application__","application_info.txt"],
                            "test"                                 : ["__application__","__test__"],
                            "Performance"                          : ["__application__","__test__","Performance"],
                            "Source"                               : ["__application__","Source"],
                            "Scripts"                              : ["__application__","__test__","Scripts"],
                            "kill_file"                            : ["__application__","__test__","Scripts",kill_file],
                            "Status"                               : ["__application__","__test__","Status"],
                            "status.txt"                           : ["__application__","__test__","Status","rgt_status.txt"],
                            "Correct_Results"                      : ["__application__","__test__","Correct_Results"],
                            "Run_Archive"                          : ["__application__","__test__","Run_Archive"],
                            "test_info.txt"                        : ["__application__","__test__","test_info.txt"],
                            ".testrc"                              : ["__application__","__test__",".testrc"],
                           }


    suffix_for_ignored_tests = '.ignore_test'
    suffix_for_ignored_apps = '.ignore_app'

    #
    # Constructor
    #
    def __init__(self,name_of_application,name_of_subtest,local_path_to_tests):

        self.__name_of_application = name_of_application
        self.__name_of_subtest = name_of_subtest
        self.__local_path_to_tests_wd = local_path_to_tests

        # Make deep copes of directory_structure 
        self.__svn_app_test_directory_structure = copy.deepcopy(apps_test_directory_layout.directory_structure)
        self.__local_app_test_directory_structure = copy.deepcopy(apps_test_directory_layout.directory_structure)

        # Set the application and test layout.
        self.__set_svn_application_test_layout(name_of_application,name_of_subtest)

    #
    # Debug function.
    #
    def debug_layout(self):
        print( "\n\n")
        print ("================================================================")
        print ("Debugging svn layout " + self.__name_of_application + self.__name_of_subtest)
        print ("================================================================")
        for key in self.__svn_app_test_directory_structure.keys():
            print ("%-20s = %-20s" % (key, self.__svn_app_test_directory_structure[key]))
        print ("================================================================\n\n")

        print ("\n\n")
        print ("================================================================")
        print ("Debugging local layout " + self.__name_of_application + self.__name_of_subtest)
        print ("================================================================")
        for key in self.__local_app_test_directory_structure.keys():
            print ("%-20s = %-20s" % (key, self.__local_app_test_directory_structure[key]))
        print ("================================================================\n\n")
    #
    # Returns the path to the top level of the application
    #
    def get_svn_path_to_application(self):
        return self.__svn_app_test_directory_structure["application"]

    #
    # Returns the path to the source.
    #
    def get_svn_path_to_source(self):
        return self.__svn_app_test_directory_structure["Source"]

    #
    # Returns the path to the top level of the test.
    #
    def get_svn_path_to_test(self):
        return self.__svn_app_test_directory_structure["test"]

    #
    # Returns the local path to the top level of the Application directory.
    #
    def get_local_path_to_application(self):
        return self.__local_app_test_directory_structure["application"]

    #
    # Returns the local path to the top level of the Scripts directory.
    #
    def get_local_path_to_scripts(self):
        return self.__local_app_test_directory_structure["Scripts"]

    #
    # Returns the local path to the top level of the Tests.
    #
    def get_local_path_to_tests_wd(self):
        return self.__local_path_to_tests_wd

    #
    # Returns the local path to kill file
    #
    def get_local_path_to_kill_file(self):
        return self.__local_app_test_directory_structure["kill_file"]

    #
    # Returns the path to the status file.
    #
    def get_path_to_status_file(self):
        return self.__local_app_test_directory_structure["status.txt"]


    def get_local_path_to_performance_dir(self):
        return self.__local_app_test_directory_structure["Performance"]

    def get_local_path_to_start_binary_time(self,uniqueid):
        path = None 
        tmppath = os.path.join(self.__local_app_test_directory_structure["Status"],
                               uniqueid,
                               "start_binary_execution_timestamp.txt")

        if os.path.exists(tmppath):
           path = tmppath 

        return path

    def get_local_path_to_end_binary_time(self,uniqueid):
        path = None 
        tmppath = os.path.join(self.__local_app_test_directory_structure["Status"],
                               uniqueid,
                               "final_binary_execution_timestamp.txt")

        if os.path.exists(tmppath):
           path = tmppath 

        return path
    #
    # Sets the application and test directory structure.
    #
    def __set_svn_application_test_layout(self,application,name_of_subtest):

        #Setting name of the application and subtest for the directory structure.
        for key in self.__svn_app_test_directory_structure.keys():
            tmpstringarray = self.__svn_app_test_directory_structure[key]
            ip = -1
            for string1 in self.__svn_app_test_directory_structure[key]:
                ip = ip + 1
                if string1 == "__application__":
                    self.__svn_app_test_directory_structure[key][ip] = application
    
                if string1 == "__test__":
                    self.__svn_app_test_directory_structure[key][ip] = name_of_subtest


        #Setting local directory structure.
        self.__local_app_test_directory_structure = copy.deepcopy(self.__svn_app_test_directory_structure)
        path_a = os.path.join(self.__local_path_to_tests_wd,application)
        for key in self.__local_app_test_directory_structure.keys():
            pathb = path_a
            ip = 0
            for string1 in self.__local_app_test_directory_structure[key]:
                if ip > 0:
                    pathb = os.path.join(pathb,string1)
                ip = ip + 1
            self.__local_app_test_directory_structure[key] = pathb


        #Now join names to make the fully qualified path names to svn repository..
        path_1 = os.path.join(apps_test_directory_layout.path_to_svn_repository)
        path_1 = os.path.join(path_1,apps_test_directory_layout.top_level_applications)
        path_1 = os.path.join(path_1,apps_test_directory_layout.organization)
        path_1 = os.path.join(path_1,apps_test_directory_layout.machine)
        
        for key in self.__svn_app_test_directory_structure.keys():
            path_2 = path_1
            for string1 in self.__svn_app_test_directory_structure[key]:
                path_2 = os.path.join(path_2,string1)
            self.__svn_app_test_directory_structure[key] = path_2


       



