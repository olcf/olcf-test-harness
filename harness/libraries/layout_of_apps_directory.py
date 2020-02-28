#!/usr/bin/env python3

import copy
import os
from string import Template
from libraries.repositories.repository_factory import RepositoryFactory

class  apps_test_directory_layout(object):

    #organization = os.environ["RGT_ORGANIZATION"]
    #machine = os.environ["RGT_MACHINE_NAME"] 
    top_level_applications ="applications"

    app_info_file = "application_info.txt"
    test_info_file = "test_info.txt"
    test_kill_file = ".kill_test"
    test_rc_file = ".testrc"
    test_status_file = "rgt_status.txt"

    directory_structure_template = {
        'application'       : os.path.join("${pdir}","${app}"),
        'application_info'  : os.path.join("${pdir}","${app}",app_info_file),
        'Source'            : os.path.join("${pdir}","${app}","Source"),
        'test'              : os.path.join("${pdir}","${app}","${test}"),
        'test_info'         : os.path.join("${pdir}","${app}","${test}",test_info_file),
        'test_rc'           : os.path.join("${pdir}","${app}","${test}",test_rc_file),
        'Correct_Results'   : os.path.join("${pdir}","${app}","${test}","Correct_Results"),
        'Performance'       : os.path.join("${pdir}","${app}","${test}","Performance"),
        'Run_Archive'       : os.path.join("${pdir}","${app}","${test}","Run_Archive"),
        'Scripts'           : os.path.join("${pdir}","${app}","${test}","Scripts"),
        'kill_file'         : os.path.join("${pdir}","${app}","${test}","Scripts",test_kill_file),
        'Status'            : os.path.join("${pdir}","${app}","${test}","Status"),
        'status_file'       : os.path.join("${pdir}","${app}","${test}","Status",test_status_file)}

    suffix_for_ignored_tests = '.ignore_test'
    suffix_for_ignored_apps  = '.ignore_app'

    #
    # Constructor
    #
    def __init__(self,name_of_application,name_of_subtest,local_path_to_tests):

        self.__name_of_application = name_of_application
        self.__name_of_subtest = name_of_subtest
        self.__local_path_to_tests_wd = local_path_to_tests

        # Set the application and test layout
        self.__appTestDirectoryStructure = copy.deepcopy(apps_test_directory_layout.directory_structure_template)
        self.__local_app_test_directory_structure = copy.deepcopy(apps_test_directory_layout.directory_structure_template)
        self.__setApplicationTestLayout()

        return

    #
    # Debug function.
    #
    def debug_layout(self):
        print( "\n\n")
        print ("================================================================")
        print ("Debugging layout " + self.__name_of_application + self.__name_of_subtest)
        print ("================================================================")
        for key in self.__appTestDirectoryStructure.keys():
            print ("%-20s = %-20s" % (key, self.__appTestDirectoryStructure[key]))
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
    def getPathToApplication(self):
        return self.__appTestDirectoryStructure["application"]

    #
    # Returns the path to the source.
    #
    def getPathToSource(self):
        return self.__appTestDirectoryStructure["Source"]

    #
    # Returns the path to the top level of the test.
    #
    def getPathToTest(self):
        return self.__appTestDirectoryStructure["test"]

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
        return self.__local_app_test_directory_structure["status_file"]


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
    def __setApplicationTestLayout(self):

        app_dict = dict(app=self.__name_of_application,
                        test=self.__name_of_subtest,
                        pdir=RepositoryFactory.get_fully_qualified_url_of_application_parent_directory())

        local_dict = dict(app=self.__name_of_application,
                          test=self.__name_of_subtest,
                          pdir=self.__local_path_to_tests_wd)

        #Setting name of the application and subtest for the directory structure.
        for key in apps_test_directory_layout.directory_structure_template.keys():
            path_template = Template(self.__appTestDirectoryStructure[key])
            self.__appTestDirectoryStructure[key] = path_template.substitute(app_dict)
            self.__local_app_test_directory_structure[key] = path_template.substitute(local_dict)
