#!/usr/bin/env python3

# %Authors%

# Python imports.
import sys
import os
import shlex
import subprocess
import time
import re

# Local imports.
from machine_types.base_machine import BaseMachine
from libraries.rgt_test import RgtTest

class Linux_x86_64(BaseMachine):

    def __init__(self,
                 name='Linux x86_64',
                 scheduler=None,
                 numNodes=1,
                 numSocketsPerNode=1,
                 numCoresPerSocket=1,
                 apptest=None,
                 separate_build_stdio=False):

        # process test input file. The subtest knows the path to the
        # the test input file.
        path_to_test_input_file = apptest.path_of_test_input_file_ini
        using_yaml = False
        # if ini does not exist, try yaml
        if not os.path.isfile(path_to_test_input_file):
            path_to_test_input_file = apptest.path_of_test_input_file_yaml
            using_yaml = True

        # Now tell the base machine if it needs a jinja template or not
        BaseMachine.__init__(self,
                             name=name,
                             scheduler_type=scheduler,
                             numNodes=numNodes,
                             numSockets=numSocketsPerNode,
                             numCoresPerSocket=numCoresPerSocket,
                             apptest=apptest,
                             separate_build_stdio=separate_build_stdio,
                             use_jinja2=using_yaml)

        self._rgt_test = RgtTest(path_to_test_input_file,logger=self.logger)
        self._rgt_test.read_input_file()

        # Add test parameters needed by the harness
        harness_parameters = {}
        harness_parameters['results_dir'] = self.apptest.get_path_to_runarchive()
        harness_parameters['working_dir'] = self.apptest.get_path_to_workspace_run()
        harness_parameters['build_dir'] = self.apptest.get_path_to_workspace_build()
        harness_parameters['scripts_dir'] = self.apptest.get_path_to_scripts()
        harness_parameters['harness_id'] = self.apptest.get_harness_id()
        self._rgt_test.harness_parameters.update(harness_parameters)

    @property
    def build_runtime_environment_command_file(self):
        return self.test_config.build_runtime_environment_command_file

    @property
    def submit_runtime_environment_command_file(self):
        return self.test_config.submit_runtime_environment_command_file

    @property
    def check_runtime_environment_command_file(self):
        return self.test_config.check_runtime_environment_command_file

    @property
    def test_config(self):
        return self._rgt_test

    #-----------------------------------------------------
    #                                                    -
    # Private methods                                    -
    #                                                    -
    #-----------------------------------------------------

if __name__ == "__main__":
    print('This is the Linux x86_64 class')
