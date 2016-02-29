#! /usr/bin/env python3
""" Test class module runs a basic hello world test.  """

import unittest
import shlex
import os

from bin import runtests

class Test_runtests(unittest.TestCase):
    """ Tests for main program runtests.py """
    
    def setUp(self):
        """ Set ups to run a basic harness tests. """

        #
        # Set environmental variables for the harness.
        #

        # PBS account id.
        os.putenv("RGT_PBS_JOB_ACCNT_ID",'STF006')

        # Scratch space for running unit tests.
        my_member_work = os.getenv("MEMBERWORK")
        my_path_to_sspace = os.path.join(my_member_work,"Harness_Unit_Testing_Scratch_Space")
        os.putenv("RGT_PATH_TO_SSPACE",my_path_to_sspace)

        # Path to environmental variables file. 
        my_user_name = os.getenv("USER")
        my_home_directory = os.getenv("HOME")

        # Path to my input file directory.
        my_rgt_input_directory = os.path.join(my_home_directory,"Harness_Unit_Testing_Input")

        # File name of rgt input file.
        my_rgt_input_file_name = "rgt.input"
     
        # The path to the rgt module file
        my_rgt_module_file = os.getenv("RGT_NCCS_TEST_HARNESS_MODULE")

        # Create the input directory along with the input files. 
        self.__createInputDirectoryAndFiles(my_path_to_sspace,
                                            my_rgt_input_directory,
                                            my_rgt_input_file_name,
                                            my_rgt_module_file)

    def tearDown(self):
        """ Stud doc for tear down """

        
    def test_good_comnand_line_args(self):
        """ Test main program for checking validity of command line arguments. """

        argument_string = "--concurrency serial"
        runtests.runtests(argument_string)
        
        self.assertEqual(101,101,"Command line arguments good.")

    def __createInputDirectoryAndFiles(
        self,
        path_to_scratch_space,
        path_to_input_directory,
        rgt_input_file_name,
        path_to_module_file):
        
        # Create the input directory.
        if not os.path.isdir(path_to_input_directory):
            os.makedirs(path_to_input_directory)

        # Create the rgt environmental file.
        self.__createRgtEnvFile(path_to_input_directory,
                                path_to_scratch_space,
                                path_to_module_file)

        # Create the rgt input file.
        self.__createRgtInputFile(path_to_input_directory)

    def __createRgtEnvFile(
        self,
        path_to_input_directory,
        path_to_scratch_space,
        path_to_module_file):

        # Define the path to the rgt environmental variables
        # file that will be in the input directory.
        rgt_env_file_name = "rgt.environmental_variables.sh"
        test_rgt_env_file_path = os.path.join(path_to_input_directory,
                                              rgt_env_file_name)

        # Define a comment format 
        comment_frmt =  "#---------------------------------------------------------------\n"
        comment_frmt += "# {rgt_comment:<60}"
        comment_frmt += "{rgt_space:<1}-\n"
        comment_frmt += "#---------------------------------------------------------------\n"

        #Define a export environmental variable format.
        export_frmt =  "{rgt_variable}={rgt_variable_value}\n"
        export_frmt += "export {rgt_variable}\n\n"
        
        # Open file for writing.
        rgt_file_obj = open(test_rgt_env_file_path,"w")

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

        # Write the path to module to load.
        module_comment = comment_frmt.format(rgt_comment="Name of test harness module to load",
                                             rgt_space=" ")

        rgt_file_obj.write(module_comment)

        module_env = export_frmt.format(rgt_variable="RGT_NCCS_TEST_HARNESS_MODULE",
                                        rgt_variable_value="'" + path_to_module_file + "'")

        rgt_file_obj.write(module_env)

        # Close file.
        rgt_file_obj.close()


    def __createRgtInputFile(
        self,
        path_to_input_directory):

        rgt_input_file_name = "rgt.input"
        test_rgt_input_file_path = os.path.join(path_to_input_directory,
                                                rgt_input_file_name )

        rgt_file_obj = open(test_rgt_input_file_path,"w")
        rgt_file_obj.write("Stud for writing rgt input file data.")
        rgt_file_obj.close()

if __name__ == "__main__":
    unittest.main()
    
