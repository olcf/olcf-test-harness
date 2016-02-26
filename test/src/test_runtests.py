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
        my_path_to_sspace = os.path.join(my_member_work,"stf006","Harness_Unit_Testing_Scratch_Space")
        os.putenv("RGT_PATH_TO_SSPACE",my_path_to_sspace)

        # Path to environmental variables file. 
        my_rgt_env_file='/ccs/home/arnoldt/Harness_Unit_Testing/rgt_environmental_variables.bash.x'
        os.putenv("RGT_ENVIRONMENTAL_FILE",my_rgt_env_file)
        print("Setting up tests.")
      
        # Create the input directory along with its input files. 
        self.__createInputDirectory()

    def tearDown(self):
        """ Stud doc for tear down """
        print("Tearing down tests.")

        
    def test_good_comnand_line_args(self):
        argument_string = "--concurrency serial"
        runtests.runtests(argument_string)
        
        self.assertEqual(101,101,"Command line arguments good.")

    def __createInputDirectory(self):
        pass

if __name__ == "__main__":
    unittest.main()
    
