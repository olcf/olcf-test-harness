#! /usr/bin/env python3
""" Test class module runs a basic hello world test.  """

import unittest
import shlex
import os

from bin import runtests
from fundamental_types.rgt_state import RgtState

class Test_runtests(unittest.TestCase):
    """ Tests for main program runtests.py """
  
    def setUp(self):
        """ Set ups to run a basic harness tests. """

        #
        # Set environmental variables for the harness.
        #

        # Define the fully qualified name to the harness top level.
        my_path_to_harness_top_level = os.getenv("PATH_TO_HARNESS_TOP_LEVEL")

        # PBS account id.
        my_job_account_id = os.getenv("my_job_account_id")
        os.putenv("RGT_PBS_JOB_ACCNT_ID",my_job_account_id)

        # Scratch space for running unit tests.
        my_member_work = os.getenv("path_to_member_work")
        my_path_to_sspace = os.path.join(my_member_work,"Harness_Unit_Testing_Scratch_Space")
        os.environ["RGT_PATH_TO_SSPACE"] = my_path_to_sspace
        
        # The path to the rgt module file
        my_rgt_module_file = os.getenv("MY_RGT_MODULE_FILE")
        os.putenv("RGT_NCCS_TEST_HARNESS_MODULE",my_rgt_module_file)

        # Path to environmental variables file. 
        my_home_directory = os.getenv("HOME")

        # Path to my input file directory.
        my_rgt_input_directory = os.path.join(my_home_directory,"Harness_Unit_Testing_Input")

        # File name of rgt input file.
        my_rgt_input_file_name = "rgt.input"
     
        # Define the fully qualified name to the rgt environmental variables
        # file that will be in the input directory, and export to environmental variables.
        fqpn_rgt_env_file_path = self.__fqpn_of_rgt_env_file(my_rgt_input_directory)
        self.__export_to_environment("RGT_ENVIRONMENTAL_FILE",fqpn_rgt_env_file_path )

        # Define the fully qualified domain name to the application repo.
        my_fqdn_to_app_repo = os.getenv("MY_APP_REPO")

        # The tests to run
        my_tests = [ {"Application" : "HelloWorld", "Test" : "Test_16cores"} ]
        my_harness_tasks = ["check_out_tests",
                            "start_tests"]

        # Create the input directory along with the input files. 
        self.__createInputDirectoryAndFiles(my_path_to_sspace,
                                            my_rgt_input_directory,
                                            my_rgt_input_file_name,
                                            my_rgt_module_file,
                                            my_path_to_harness_top_level,
                                            my_fqdn_to_app_repo,
                                            my_tests,
                                            my_member_work,
                                            my_harness_tasks)

        self.__startingDirectory = os.getcwd()
        self.__inputDirectory = my_rgt_input_directory 

        os.chdir(self.__inputDirectory)

    def tearDown(self):
        """ Stud doc for tear down """
        os.chdir(self.__startingDirectory)

        
    def test_hello_world(self):
        """ Test of harness if it can launch a MPI hello world on 1 node. """ 

        argument_string = "--concurrency serial"
        my_rgt_test = runtests.runtests(argument_string)

        # Get the state of my_rgt_test
        state_of_rgt = my_rgt_test.getState()

        # The state of my_rgt_test should be "ALL_TASKS_COMPLETED".
        correct_state = RgtState.ALL_TASKS_COMPLETED
        
        # Compare results.
        error_message = "Hello world program did not complete all tasks."
        self.assertEqual(state_of_rgt,correct_state,error_message)

    def __createInputDirectoryAndFiles(
        self,
        path_to_scratch_space,
        path_to_input_directory,
        rgt_input_file_name,
        path_to_module_file,
        path_to_harness_top_level,
        fqdn_to_app_repo,
        harness_tests,
        my_member_work,
        harness_tasks):
        
        # Create the input directory.
        if not os.path.isdir(path_to_input_directory):
            os.makedirs(path_to_input_directory)

        # Create the rgt environmental file.
        self.__createRgtEnvFile(path_to_input_directory,
                                path_to_scratch_space,
                                path_to_module_file,
                                path_to_harness_top_level,
                                my_member_work,
                                fqdn_to_app_repo)

        # Create the rgt input file.
        self.__createRgtInputFile(path_to_input_directory,
                                  harness_tests,
                                  harness_tasks)

    def __createRgtEnvFile(
        self,
        path_to_input_directory,
        path_to_scratch_space,
        path_to_module_file,
        path_to_harness_top_level,
        my_member_work,
        fqdn_to_app_repo):

        # Define the path to the rgt environmental variables
        # file that will be in the input directory.
        fqpn_rgt_env_file_path = self.__fqpn_of_rgt_env_file(path_to_input_directory)

        # Define a comment format 
        comment_frmt =  "#---------------------------------------------------------------\n"
        comment_frmt += "# {rgt_comment:<60}"
        comment_frmt += "{rgt_space:<1}-\n"
        comment_frmt += "#---------------------------------------------------------------\n"

        #Define a export environmental variable format.
        export_frmt =  "{rgt_variable}={rgt_variable_value}\n"
        export_frmt += "export {rgt_variable}\n\n"
        
        # Open file for writing.
        rgt_file_obj = open(fqpn_rgt_env_file_path,"w")

        # Write the PBS job account id export lines to file.
        pbs_job_comment = comment_frmt.format(rgt_comment="JOB ACCOUNT ID",
                                              rgt_space=" ")
        rgt_file_obj.write(pbs_job_comment)

        pbs_env = export_frmt.format(rgt_variable="RGT_PBS_JOB_ACCNT_ID",
                                     rgt_variable_value="'STF006'")
        rgt_file_obj.write(pbs_env)

        # Write the path to scratch space to file.
        scratch_space_comment = comment_frmt.format(rgt_comment="Absolute path to scratch space",
                                                    rgt_space=" ")
        rgt_file_obj.write(scratch_space_comment)

        scratch_space_env = export_frmt.format(rgt_variable="RGT_PATH_TO_SSPACE",
                                               rgt_variable_value="'" + path_to_scratch_space + "'")

        rgt_file_obj.write(scratch_space_env)


        # Write path to my member work directory.
        member_work_comment = comment_frmt.format(rgt_comment="Absolute path to member work directory.",
                                                  rgt_space=" ")
        
        rgt_file_obj.write(member_work_comment)

        member_work_env = export_frmt.format(rgt_variable="MY_MEMBER_WORK",
                                               rgt_variable_value="'" + my_member_work + "'")
        
        rgt_file_obj.write(member_work_env)


        # Write the path to module to load.
        module_comment = comment_frmt.format(rgt_comment="Name of test harness module to load",
                                             rgt_space=" ")

        rgt_file_obj.write(module_comment)

        module_env = export_frmt.format(rgt_variable="RGT_NCCS_TEST_HARNESS_MODULE",
                                        rgt_variable_value="'" + path_to_module_file + "'")

        rgt_file_obj.write(module_env)

        # Write the path to the rgt environmental variable file.
        rgt_path_comment = comment_frmt.format(rgt_comment="Absolute path to this file.",
                                               rgt_space=" ")

        rgt_path_env = export_frmt.format(rgt_variable="RGT_ENVIRONMENTAL_FILE",
                                          rgt_variable_value="'" + fqpn_rgt_env_file_path + "'")

        rgt_file_obj.write(rgt_path_comment)
        rgt_file_obj.write(rgt_path_env)


        #Write the path to the top level of the harness 
        rgt_path_top_level_comment = comment_frmt.format(rgt_comment="Fully qualified path to harness top level.",
                                                         rgt_space=" ")

        rgt_file_obj.write(rgt_path_top_level_comment)

        rgt_path_top_level_env = export_frmt.format(rgt_variable="PATH_TO_HARNESS_TOP_LEVEL",
                                                    rgt_variable_value="'" + path_to_harness_top_level + "'")

        rgt_file_obj.write(rgt_path_top_level_env)

        #Write the path to the Application repository.
        rgt_path_top_app = comment_frmt.format(rgt_comment="Fully qualified applications path.",
                                               rgt_space=" ")

        rgt_file_obj.write(rgt_path_top_app)


        rgt_path_top_app_env =  export_frmt.format(rgt_variable="MY_APP_REPO",
                                                   rgt_variable_value="'" + fqdn_to_app_repo + "'")

        rgt_file_obj.write(rgt_path_top_app_env)

        # Close file.
        rgt_file_obj.close()


    def __createRgtInputFile(
        self,
        path_to_input_directory,
        harness_tests,
        harness_tasks):

        # Define a comment format 
        comment_frmt =  "#---------------------------------------------------------------\n"
        comment_frmt += "# {rgt_comment:<60}"
        comment_frmt += "{rgt_space:<1}-\n"
        comment_frmt += "#---------------------------------------------------------------\n"

        #Define a ??? format.
        top_level_frmt = "Path_to_tests = {}\n\n"

        #Define a test format.
        test_frmt =  "Test = {Application} {test}\n"
        
        #Define a task format.
        task_frmt =  "Harness_task = {harness_task}\n"

        rgt_input_file_name = "rgt.input"
        test_rgt_input_file_path = os.path.join(path_to_input_directory,
                                                rgt_input_file_name )

        rgt_file_obj = open(test_rgt_input_file_path,"w")
        path_to_tests_comment = comment_frmt.format(rgt_comment="Set the path to the top level of the application directory.",
                                                    rgt_space=" ")

        # Write to file  the top level path to tests.
        rgt_file_obj.write(path_to_tests_comment)

        my_top_level_path_to_tests = os.path.join(path_to_input_directory,"Applications")
        path_to_tests = top_level_frmt.format(my_top_level_path_to_tests) 
        rgt_file_obj.write(path_to_tests)

        # Write to file tests to be run.
        my_tests = ""
        for a_test in harness_tests:
            my_tests += test_frmt.format(Application = a_test["Application"],
                                         test = a_test["Test"])
        rgt_file_obj.write(my_tests)

        #Write to file the harness tasks.
        harness_task_comments = comment_frmt.format(rgt_comment="Harness tasks",
                                                    rgt_space=" ")
        rgt_file_obj.write("\n" + harness_task_comments)


        my_harness_tasks = ""
        for a_task in harness_tasks:
            my_harness_tasks += task_frmt.format(harness_task=a_task)
        rgt_file_obj.write(my_harness_tasks + "\n" + "\n")


        rgt_file_obj.close()

    def __fqpn_of_rgt_env_file(
        self,
        path_to_rgt_input_directory=None):
        
        rgt_env_file_name = "rgt.environmental_variables.sh"
        fqpn_rgt_env_file_path = os.path.join(path_to_rgt_input_directory,
                                              rgt_env_file_name)
        return fqpn_rgt_env_file_path

    def __export_to_environment(
            self,
            key,
            value):
        os.environ[key] = value

        pass

if __name__ == "__main__":
    unittest.main()
    
