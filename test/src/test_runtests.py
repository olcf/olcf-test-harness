#! /usr/bin/env python3
""" Test class module """

import unittest
import shlex

from bin import runtests

class Test_runtests(unittest.TestCase):
    """ Tests for main program runtests.py """
    
    


    def setUp(self):
        """ Stud doc for setup """
        print("Setting up tests.")
        
    def tearDown(self):
        """ Stud doc for tear down """
        print("Tearing down tests.")

    def test_bad_command_line_args(self):
        argument_string = "--concurrencies bad_argument"
        
        runtests.runtests(argument_string)
        
        self.assertNotEqual(101,100,"Command line arguments bad.")
        
    def test_good_comnand_line_args(self):
        argument_string = "--concurrency serial"
        runtests.runtests(argument_string)
        
        self.assertEqual(100,100,"Command line arguments good.")

if __name__ == "__main__":
    unittest.main()
