#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#

from .base_machine import BaseMachine
from .rgt_test import RgtTest
import os
import re

class RHELx86(BaseMachine):

    def __init__(self,
                 name='RHEL x86',
                 scheduler=None,
                 jobLauncher=None,
                 numNodes=1,
                 numSocketsPerNode=1,
                 numCoresPerSocket=16,
                 rgt_test_input_file="rgt_test_input.ini",
                 apptest=None):
        BaseMachine.__init__(self,
                             name,
                             scheduler,
                             jobLauncher,
                             numNodes,
                             numSocketsPerNode,
                             numCoresPerSocket,
                             apptest)

        # process test input file
        self.__rgt_test = RgtTest(rgt_test_input_file)
        self.__rgt_test.read_input_file()

        test_params = {}

        # add test parameters needed by the harness
        test_params['results_dir'] = self.apptest.get_path_to_runarchive()
        test_params['working_dir'] = self.apptest.get_path_to_workspace_run()
        test_params['build_dir'] = self.apptest.get_path_to_workspace_build()
        test_params['scripts_dir'] = self.apptest.get_path_to_scripts()
        test_params['harness_id'] = self.apptest.get_harness_id()

        # update the test parameters
        self.__rgt_test.set_test_parameters(test_params.items())

        # is this actually used? if so, it has to come after updating test parameters
        #joblaunch_cmd = self.get_jobLauncher_command()
        #self.__rgt_test.set_user_param("joblaunchcommand", joblaunch_cmd)


    def get_jobLauncher_command(self):
        print("Building jobLauncher command for x86")
        jobLauncher_command = self.build_jobLauncher_command(self.__rgt_test.get_test_parameters())
        return jobLauncher_command

    def make_batch_script(self):
        #print("[LOG] BEGIN: make_batch_script")
        print("Making batch script for a RHEL x86 system using " + self.get_scheduler_template_file_name())

        # Get batch job template lines
        templatefileobj = open(self.get_scheduler_template_file_name(), "r")
        templatelines = templatefileobj.readlines()
        templatefileobj.close()

        # Create test batch job script in run archive directory
        batch_file_path = os.path.join(self.apptest.get_path_to_runarchive(),
                                       self.__rgt_test.get_batch_file())
        batch_job = open(batch_file_path, "w")

        # Replace all the wildcards in the batch job template with the values in
        # the test config
        test_replacements = self.__rgt_test.get_test_replacements()
        for record in templatelines:
            for (replace_key,val) in test_replacements.items():
                re_tmp = re.compile(replace_key)
                record = re_tmp.sub(val, record)
            batch_job.write(record)

        # Close batch job script file
        batch_job.close()
        #print("[LOG] END: make_batch_script")

    def build_executable(self):
        print("Building executable on x86 using build script " + self.__rgt_test.get_build_command())
        return self.start_build_script(self.__rgt_test.get_build_command())

    def submit_batch_script(self):
        # Set environment vars using os.putenv() so that submit subprocess will
        # inherit them
        env_vars = self.__rgt_test.get_test_environment()
        for e in env_vars:
            v = env_vars[e]
            print("Setting env var", e, "=", v)
            os.putenv(e.upper(), v)

        print("Submitting batch script for x86")
        batch_script = self.__rgt_test.get_batch_file()
        submit_exit_value = self.submit_to_scheduler(batch_script)
        print("Submitting " + batch_script + " submit_exit_value = " + str(submit_exit_value))
        return submit_exit_value

    def check_executable(self):
        print("Running check executable script on x86 using check script " + self.__rgt_test.get_check_command())
        return self.check_results(self.__rgt_test.get_check_command())

    def report_executable(self):
        print("Running report executable script on x86 using report script " + self.__rgt_test.get_report_command())
        return self.start_report_script(self.__rgt_test.get_report_command())

if __name__ == "__main__":
    print('This is the RHEL x86 class')
