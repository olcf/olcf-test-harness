#! /usr/bin/env python3
import unittest

class Test_configFile(unittest.TestCase):
    """ Tests for main program runtests.py """
  
    def setUp(self):
        """  Stud documentation of HelloWorld test on Ascent."""
        return

    def test_machine_name(self):
        message="The machine name for Ascent in the config is not correct."
        self.assertEqual("Ascent","NotAscent",msg=message)
        return

    def tearDown(self):
        """ Stud doc for tear down """
        return
    



if __name__ == "__main__":
    unittest.main()
    
