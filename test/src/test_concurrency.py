#! /usr/bin/env python3
""" Test class module verifies concurrent running of tests.  """

# System imports
import unittest
import os

# Local imports
from src.Repository_Tests.repository_tests_utility_functions import set_up_HelloWorlds
from src.Repository_Tests.repository_tests_utility_functions import tear_down_HelloWorlds

class Test_concurrency(unittest.TestCase):

    def setUp(self):
        """ Set ups to run a basic harness tests in concurrent mode. """
        
        self.__startingDirectory = os.getcwd()

        set_up_HelloWorlds(self,"Harness_Unit_Testing_Concurrent") 

        return
    
    def tearDown(self):
        """ Stud doc for tear down """
    
        os.chdir(self.__startingDirectory)

        tear_down_HelloWorlds(self,"Harness_Unit_Testing_Concurrent") 

        return
    
    def test_hello_worlds_concurrent_checkout(self):
        error_message = "The test test_hello_worlds_concurrent_checkout failed!"
        self.assertEqual(1,0,error_message)
        return

    def test_hello_worlds_concurrent_runs(self):
        error_message = "The test test_hello_worlds_concurrent_runs failed!"
        self.assertEqual(1,0,error_message)
        return

    def test_hello_worlds_concurrent_stop_tests(self):
        error_message = "The test test_hello_worlds_concurrent_stop_tests failed!"
        self.assertEqual(1,0,error_message)
        return

    def test_hello_worlds_concurrent_status_updates(self):
        error_message = "The test test_hello_worlds_concurrent_updates failed!"
        self.assertEqual(1,0,error_message)
        return

if __name__ == "__main__":
    unittest.main()
