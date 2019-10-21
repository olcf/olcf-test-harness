#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#

from .base_machine import BaseMachine
from .rgt_test import RgtTest
import os
import re
import configparser

class RHELx86(BaseMachine):
    
    def __init__(self,
                 name='RHEL x86',
                 scheduler=None,
                 jobLauncher=None,
                 numNodes=1,
                 numSocketsPerNode=1,
                 numCoresPerSocket=16,
                 rgt_test_input_file="rgt_test_input.txt",
                 rgt_test_config_file="rgt_test_input.ini",
                 workspace=None,
                 harness_id=None,
                 scripts_dir=None):
        BaseMachine.__init__(self,
                             name,
                             scheduler,
                             jobLauncher,
                             numNodes,
                             numSocketsPerNode,
                             numCoresPerSocket,
                             rgt_test_input_file,
                             workspace,harness_id,
                             scripts_dir)

        self.__rgt_test_config_file = rgt_test_config_file
        self.__rgt_test = RgtTest()

        #self.read_rgt_test_input()
        #self.read_custom_rgt_test_input()
        self.read_rgt_test_config()

    def read_rgt_test_input():
        print("This is not implemented for RHELx86")
        return

    def get_rgt_test_config_filename(self):
        return self.__rgt_test_config_file


    def read_rgt_test_config(self):

        print("[LOG] BEGIN: read_rgt_test_config")
        rgt_test_config_filename = self.get_rgt_test_config_filename()

        if os.path.isfile(rgt_test_config_filename):
            print("reading test config from x86 input")

            rgt_test_config = configparser.ConfigParser()
            rgt_test_config.read(rgt_test_config_filename)

            replace = rgt_test_config['Replacements']
            env_vars = rgt_test_config['EnvVars']

            # variables needed by the harness
            replace["rgtenvironmentalfile"] = os.environ["RGT_ENVIRONMENTAL_FILE"]
            replace["nccstestharnessmodule"] = os.environ["RGT_NCCS_TEST_HARNESS_MODULE"]
            replace["resultsdir"] = self.get_rgt_results_dir()
            replace["workdir"] = self.get_rgt_workdir()
            replace["startingdirectory"] = self.get_rgt_scripts_dir()
            replace["unique_id_string"] = self.get_rgt_harness_id()

            self.__rgt_test.set_test_config_parameters(replace)
            self.__rgt_test.set_test_config_env_vars(env_vars)
            

        print("[LOG] END: read_rgt_test_config")

    def read_custom_rgt_test_input(self):

        template_dict = {}

        if os.path.isfile(self.get_rgt_input_file_name()):
            print("reading custom key-value pairs from x86 input")

            # read the custom parameters from rgt test input
            delimiter = "="

            fileobj = open(self.get_rgt_input_file_name())
            filerecords = fileobj.readlines()
            fileobj.close()

            for record in filerecords:
                if not record.strip() or record.strip()[0] == '#':
                  continue
                (k,v) = record.split('=')
                template_dict[k.strip().lower()] = v.strip()

        # variables needed by the harness
        template_dict["rgtenvironmentalfile"] = os.environ["rgt_environmental_file"]
        template_dict["nccstestharnessmodule"] = os.environ["rgt_nccs_test_harness_module"]
        template_dict["resultsdir"] = self.get_rgt_results_dir()
        template_dict["workdir"] = self.get_rgt_workdir()
        template_dict["startingdirectory"] = self.get_rgt_scripts_dir()
        template_dict["unique_id_string"] = self.get_rgt_harness_id()

        print(template_dict)

        self.__rgt_test.set_custom_test_parameters(template_dict)
        self.__rgt_test.print_custom_test_parameters()
        self.__rgt_test.check_builtin_parameters()

        self.__rgt_test.append_to_template_dict("pathtoexecutable",os.path.join(self.get_rgt_workspace(),"build_directory/bin",self.__rgt_test.get_executablename()))
        self.__rgt_test.append_to_template_dict("joblaunchcommand",self.get_joblauncher_command(self.__rgt_test.get_value_from_template_dict("pathtoexecutable")))

    def get_jobLauncher_command(self,path_to_executable):
        print("Building jobLauncher command for x86")
        jobLauncher_command = self.build_jobLauncher_command(self.__rgt_test.get_template_dict())
        return jobLauncher_command

    def make_custom_batch_script(self):
        print("[LOG] BEGIN: make_custom_batch_script")
        print("Creating a batch script for a RHEL x86 system using " + self.get_scheduler_template_file_name())

        templatefileobj = open(self.get_scheduler_template_file_name(),"r")
        templatelines = templatefileobj.readlines()
        templatefileobj.close()

        # Open file for the test batch job script
        batch_job = open(self.__rgt_test.get_batchfilename(),"w")

        # Replace all the wildcards in the batch job template with the values in
        # the test config
        test_replacements = self.__rgt_test.get_replacements()
        for record in templatelines:
            for key in test_replacements:
                print(key, test_replacements[key])
                re_tmp = re.compile('__' + key + '__')
                record = re_tmp.sub(test_replacements[key],record)
            batch_job.write(record)

        # Close batch job script file
        batch_job.close()

        print("Replacements:")
        print(test_replacements)
        print("[LOG] END: make_custom_batch_script")

    def make_batch_script(self):
        print("Not implemented for RHEL x86")

    def build_executable(self):
        print("Building executable on x86 using build script " + self.__rgt_test.get_buildscriptname())
        return self.start_build_script(self.__rgt_test.get_buildscriptname())

    def submit_batch_script(self):
        print("Submitting batch script for x86")
        submit_exit_value = self.submit_to_scheduler(self.__rgt_test.get_batchfilename(),self.get_rgt_harness_id())
        print("Submitting " + self.__rgt_test.get_batchfilename() + " submit_exit_value = " + str(submit_exit_value))
        return submit_exit_value

    def check_executable(self):
        print("Running check executable script on x86 using check script " + self.__rgt_test.get_checkscriptname())
        return self.check_results(self.__rgt_test.get_checkscriptname())

    def report_executable(self):
        print("Running report executable script on x86 using report script " + self.__rgt_test.get_reportscriptname())
        return self.start_report_script(self.__rgt_test.get_reportscriptname())

if __name__ == "__main__":
    print('This is the RHEL x86 class')
