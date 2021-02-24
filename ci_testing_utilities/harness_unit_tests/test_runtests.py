#! /usr/bin/env python3

# Python package imports
import unittest
import argparse
import shlex

# My harness package imports
from bin import runtests  # This imports the olcf harness module runtests.py 
                          # which is the is the fist module called in running
                          # the harness.

class Test_command_line_arguments(unittest.TestCase):
    """ Tests for main program runtests.py """
  
    def setUp(self):
        """  Stud documentation of runtests.py """
        return

    def test_mode_option_short(self):
        """Tests the short option for the harness mode."""
      
        # The error message for a failed command line short option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness mode short option:\n"
                        "\tcommand line: {}\n")

        # We loop over each valid harness mode, form the appropiate short
        # option command line, and verify that the stored mode is permitted
        # and is actually that value.
        for task in runtests.PERMITTED_HARNESS_TASKS:
            command_line_arguments ="-m {}".format(task) 
            argv = shlex.split(command_line_arguments)
            harness_arguments = runtests.parse_commandline_argv(argv)
            error_message=frmt_message.format(command_line_arguments)
            self.assertEqual(harness_arguments.runmode[0],task,msg=error_message)

    def test_mode_option_long(self):
        """Tests the long option for the harness mode."""
      
        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness mode long option:\n"
                        "\tcommand line: {}\n")

        # We loop over each valid harness mode, form the appropiate long
        # option command line, and verify that the stored mode is permitted
        # and is actually that value.
        for task in runtests.PERMITTED_HARNESS_TASKS:
            command_line_arguments ="--mode {}".format(task) 
            argv = shlex.split(command_line_arguments)
            harness_arguments = runtests.parse_commandline_argv(argv)
            error_message=frmt_message.format(command_line_arguments)
            self.assertEqual(harness_arguments.runmode[0],task,msg=error_message)

    def test_mode_option_short_with_multiple_values(self):
        """Tests the short option for the harness mode with multiple values."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness mode short option:\n"
                        "\tcommand line: {}\n")

        # Test the short option for multiple harness tasks.
        command_line_arguments ="-m "
        for task in runtests.PERMITTED_HARNESS_TASKS:
            command_line_arguments += "{} ".format(task)
            argv = shlex.split(command_line_arguments)
            harness_arguments = runtests.parse_commandline_argv(argv)
            error_message=frmt_message.format(command_line_arguments)
            for ip in range(len(harness_arguments.runmode)):
                self.assertEqual(harness_arguments.runmode[ip],
                                 runtests.PERMITTED_HARNESS_TASKS[ip],
                                 msg=error_message)
      
    def test_mode_option_long_with_multiple_values(self):
        """Tests the long option for the harness mode with multiple values."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness mode long option:\n"
                        "\tcommand line: {}\n")

        # Test the short option for multiple harness tasks.
        command_line_arguments ="--mode "
        for task in runtests.PERMITTED_HARNESS_TASKS:
            command_line_arguments += "{} ".format(task)
            argv = shlex.split(command_line_arguments)
            harness_arguments = runtests.parse_commandline_argv(argv)
            error_message=frmt_message.format(command_line_arguments)
            for ip in range(len(harness_arguments.runmode)):
                self.assertEqual(harness_arguments.runmode[ip],
                                 runtests.PERMITTED_HARNESS_TASKS[ip],
                                 msg=error_message)

    def test_mode_option_default_value(self):
        """Tests the defult of for mode option values."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness mode default value:\n"
                        "\tcommand line: {}\n")

        command_line_arguments = ""
        argv = shlex.split(command_line_arguments)
        harness_arguments = runtests.parse_commandline_argv(argv)
        error_message=frmt_message.format(command_line_arguments)
        self.assertEqual(harness_arguments.runmode[0],
                         runtests.DEFAULT_HARNESS_TASK,
                         msg=error_message)

    def test_input_file_option_short(self):
        """Tests the short option for the input file."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness input file short option:\n"
                        "\tcommand line: {}\n")

        # Test the short option for the input file. 
        filename = "rgt.dummy.input"
        command_line_arguments ="-i " + filename
        error_message = frmt_message.format(command_line_arguments)
        argv = shlex.split(command_line_arguments)
        harness_arguments = runtests.parse_commandline_argv(argv)
        self.assertEqual(harness_arguments.inputfile,filename,msg=error_message)

    def test_input_file_option_long(self):
        """Tests the long option for the input file."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness input file long option:\n"
                        "\tcommand line: {}\n")

        # Test the long option for the input file. 
        filename = "rgt.dummy.input"
        command_line_arguments ="--inputfile " + filename
        error_message = frmt_message.format(command_line_arguments)
        argv = shlex.split(command_line_arguments)
        harness_arguments = runtests.parse_commandline_argv(argv)
        self.assertEqual(harness_arguments.inputfile,filename,msg=error_message)

    def test_input_file_option_default(self):
        """Tests the default option for the input file."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness input file default option:\n"
                        "\tcommand line: {}\n")

        command_line_arguments = ""
        error_message = frmt_message.format(command_line_arguments)
        argv = shlex.split(command_line_arguments)
        harness_arguments = runtests.parse_commandline_argv(argv)
        self.assertEqual(harness_arguments.inputfile,
                         runtests.DEFAULT_INPUT_FILE,
                         msg=error_message)

    def test_configfile_option_long(self):
        """Tests the long option for the config file option."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness  config file long option:\n"
                        "\tcommand line: {}\n")

        config_filename = "DummyMachine.ini"
        command_line_arguments = "--configfile {}".format(config_filename)
        error_message=frmt_message.format(command_line_arguments) 
        argv = shlex.split(command_line_arguments)
        harness_arguments = runtests.parse_commandline_argv(argv)
        self.assertEqual(harness_arguments.configfile,config_filename,msg=error_message)

    def test_loglevel_option(self):
        """Tests the log level option."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness  log level option:\n"
                        "\tcommand line: {}\n")

        for loglevel in runtests.PERMITTED_LOG_LEVELS:
            command_line_arguments="--loglevel {}".format(loglevel)
            error_message = frmt_message.format(command_line_arguments)
            argv = shlex.split(command_line_arguments)
            harness_arguments = runtests.parse_commandline_argv(argv)
            self.assertEqual(harness_arguments.loglevel,loglevel,msg=error_message)

    def test_loglevel_default_option(self):
        """Tests the log level default option."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness log level default option:\n"
                        "\tcommand line: {}\n")

        # Test the default option for loglevel
        command_line_arguments = ""
        error_message = frmt_message.format(command_line_arguments)
        argv = shlex.split(command_line_arguments)
        harness_arguments = runtests.parse_commandline_argv(argv)
        self.assertEqual(harness_arguments.loglevel,runtests.DEFAULT_LOG_LEVEL,msg=error_message)

    def test_loglevel_option_incorrect_value(self):
        """Tests for an invalid log level."""

        # The error message for a failed command line option.
        frmt_message = ("\n\nError Details\n"
                        "\tFailure in harness log level with an invalid level:\n"
                        "\tcommand line: {}\n")

        # Test an incorrect choice for loglevel. This test will fail.
        invalid_loglevel = "INVALID_LOG_LEVEL"
        command_line_arguments="--loglevel {}".format(invalid_loglevel)
        error_message = frmt_message.format(command_line_arguments)
        argv = shlex.split(command_line_arguments)
        self.assertRaises(SystemExit,runtests.parse_commandline_argv,argv)

    def tearDown(self):
        """ Stud doc for tear down """
        return
    
if __name__ == "__main__":
    unittest.main()
    

