#! /usr/bin/env python3

# Python package imports
import unittest
import os
import re
import shutil

# My harness package imports
from bin import runtests  # This imports the olcf harness module runtests.py 
                          # which is the is the fist module called in running
                          # the harness.

from libraries import get_machine_name
 
class Test_MPI_Hello_World(unittest.TestCase):
    """Run the MPI_Hello World Test"""

    TOP_LEVEL=os.getenv("OLCF_HARNESS_DIR")

    UNIT_TESTS_CWD=os.getcwd()

    MACHINE_NAME=get_machine_name.get_registered_unique_name_based_on_hostname()

    if os.environ['HUT_PATH_TO_SSPACE'] != 'NOT_SET':
       SCRATCH_SPACE = os.path.join(os.environ['HUT_PATH_TO_SSPACE'],"MPI_HelloWorld_Scratch_Space")
    else:
        SCRATCH_SPACE=os.path.join(UNIT_TESTS_CWD,"MPI_HelloWorld_Scratch_Space")

    if os.environ['HUT_SCHED_ACCT_ID'] != 'NOT_SET':
        HUT_SCHED_ACCT_ID = os.environ['HUT_SCHED_ACCT_ID']
    else:
        HUT_SCHED_ACCT_ID = 'stf006'


    INPUT_FILES_DIR=os.path.join(UNIT_TESTS_CWD,"MPI_HelloWorld_Input_Files")
    APPLICATION_PATH=os.path.join(UNIT_TESTS_CWD,"MPI_HelloWorld_Applications")

    @classmethod
    def setUpClass(cls): 
        # Create a scratch space directory to run in.
        os.makedirs(cls.SCRATCH_SPACE)

        # Create a directory to store the input files
        os.makedirs(cls.INPUT_FILES_DIR)

        # Create a directory to store the cloned MPI_Hello_World test applications.
        os.makedirs(cls.APPLICATION_PATH)

        # Export to the environment 'UNIT_TESTS_CWD'.
        os.environ["UNIT_TESTS_CWD"] = cls.UNIT_TESTS_CWD
        
    @classmethod
    def tearDownClass(cls): 
        # Export to the environment 'UNIT_TESTS_CWD'.
        os.unsetenv("UNIT_TESTS_CWD")

    def setUp(self):
        print("In test setup.")
        return

    def tearDown(self):
        print("In test teardown.")
        return

    def test_single_node_MPI_Hello_World(self):
        """Runs a MPI Hello World on a single node"""
        
        test_input_files_directory = self.INPUT_FILES_DIR
        (harness_input_file,config_ini_filepath) = \
                self._create_input_files_for_test_single_node_MPI_Hello_World(test_input_files_directory)

        # Run the test.
        rgt = self._start_harness_job(test_input_files_directory,harness_input_file,config_ini_filepath)

        # Set the maximum wait, in minutes, for jobs to leave the queue. Five minutes should
        # be suffcient time for a one node MPI Hello workd job to complete.
        time_to_wait = 20
        rgt.wait_for_completion_in_queue(time_to_wait) 

        tests_status = rgt.didAllTestsPass()

        if tests_status:
            error_message = "No error message."
        else:
            error_message="MPI Hello World on single node failed."

        self.assertTrue(tests_status,msg=error_message)

    @unittest.skip("Test not fully implemented.")
    def test_multiple_nodes(self):
        """Runs a MPI Hello World on multiple nodes"""

        # Create the single node input_file.

        tests_status = False
        if tests_status:
            pass
        else:
            error_message="MPI Hello World on multiple nodes failed. The test is not fully implemented."

        self.assertTrue(tests_status,msg=error_message)

    def _get_harness_input_file_records(self,harness_template_rgt_input_filepath,re_patterns):
        """Returns a list of strings that are the input file records for running the MPI Hello World Test.
       
        Parameters
        ----------
        harness_template_rgt_input_filepath: A string 
            The absolute file path to the template harness input file.

        re_patterns :  A dictionary of with elements of form { compiled regular expression : a string }

        Returns
        -------
        new_input_file_records.
            A list of strings.
        """

        old_input_file_records = []
        with open(harness_template_rgt_input_filepath,"r") as file_obj :
            old_input_file_records = file_obj.readlines()

        new_input_file_records = []
        for a_record in old_input_file_records:
            for (regex, replacement_str) in re_patterns.items(): 
                new_input_file_records.append( regex.sub(replacement_str,a_record) )

        return new_input_file_records


    def _write_input_file_to_disk(self,file_records,filepath):
        """Writes file records to disk.

        The file records, file_records, are written to disk at directory destination_directory with the
        filename file_name.
    
        Parameters
        ----------
        file_records : A list of strings
            The file records to be written to disk.

        filepath : A string
            The absolute file path to write the file records.

        """

        # Now write the records to disk.
        with open(filepath,"w") as file_obj:
            for a_record in file_records:
                file_obj.write(a_record)

    def _start_harness_job(self,destination_dir,filename,ini_file):
        """Starts the OLCF harness job.
       
        Parameters
        ----------
        destination_dir : A string
            The file path where the harness is to be launched.
       
        filename : A string
            The name of the harness input file.

        ini_file : A string
            The fully qualified file path to the config ini file.
        """
        import subprocess
        import shlex

        os.chdir(destination_dir)
        my_arg_str = "--configfile {} --inputfile {} --loglevel DEBUG".format(ini_file,filename)
        rgt = runtests.runtests(my_arg_str)
        os.chdir(self.UNIT_TESTS_CWD)
        
        return rgt

    def _create_input_files_for_test_single_node_MPI_Hello_World(self,destination_dir):
        input_template_filename_suffix="1_node.txt" 

        # We compute the absolute template harness input file path. 
        harness_template_rgt_input_filename = \
                self.MACHINE_NAME + "." + input_template_filename_suffix
        src_directory = \
            os.path.join(self.TOP_LEVEL,"ci_testing_utilities","input_files",self.MACHINE_NAME,"MPI_Hello_World")
        harness_template_rgt_input_filepath = os.path.join(src_directory,harness_template_rgt_input_filename)

        # Get the records of the harness input file.
        re_patterns = { re.compile("__pathtotests__") : self.APPLICATION_PATH }
        harness_input_file_records = \
            self._get_harness_input_file_records(harness_template_rgt_input_filepath,re_patterns)

        # We compute the absolute harness input file path. 
        harness_rgt_input_filename = "{}.{}".format(self.MACHINE_NAME,input_template_filename_suffix)
        harness_rgt_input_filepath = os.path.join(destination_dir,harness_rgt_input_filename)

        # Write the harness input file records to "harness_rgt_input_filepath".
        self._write_input_file_to_disk(harness_input_file_records,harness_rgt_input_filepath)

        # Create the new config ini file. 
        new_config_filepath = self._create_new_ini_file(destination_dir)

        return (harness_rgt_input_filename,new_config_filepath )

    def _create_new_ini_file(self,destination_dir):
        """Creates a new config ini file and returns the absolute path to the ini file. 
        
        Parameters
        ----------
        destination_dir : str
            The directory path to the newly created ini config file.

        Returns
        -------
        str 
            The absolute path to the newly created config ini file.

        """
        import subprocess
        import shlex

        # Get the registerd unique file name for this machine.
        registered_machine_name = get_machine_name.get_registered_unique_name_based_on_hostname()

        # Form the fully qualified path to the old config ini file.
        old_config_file = "{}.ini".format(registered_machine_name)
        old_config_filepath = os.path.join(self.TOP_LEVEL,"configs",old_config_file)

        # Form the fully qualified path to the new config ini file.
        new_config_file = "{}.unit_tests.ini".format(registered_machine_name)
        new_config_filepath = os.path.join(destination_dir,new_config_file)

        # Form the command line arguments for creating a new config ini file.
        command_line_args="--keys {section} {key} {value}".format(value=self.SCRATCH_SPACE,
                                                                section="TestshotDefaults",
                                                                key="path_to_sspace" )

        command_line_args+=" {section} {key} {value}".format(value=self.HUT_SCHED_ACCT_ID,
                                                             section="TestshotDefaults",
                                                             key="acct_id")

        command_line_args+=" -i {}".format(old_config_filepath)
        command_line_args+=" -o {}".format(new_config_filepath)

        # Form the command to generate the new config ini file.
        command1 = "create_alt_config_file.py {args}".format(args=command_line_args)
        command2 = shlex.split(command1)

        # Execute the command.
        p = subprocess.run(command2)

        return new_config_filepath 
