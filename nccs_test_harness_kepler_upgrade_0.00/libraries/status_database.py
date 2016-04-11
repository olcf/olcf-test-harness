#! /usr/bin/env python
"""
-------------------------------------------------------------------------------
File:   status_database.py
Author: Wayne Joubert (joubert@ornl.gov)
National Center for Computational Sciences, Scientific Computing Group.
Oak Ridge National Laboratory
Copyright (C) 2015 Oak Ridge National Laboratory, UT-Battelle, LLC.
-------------------------------------------------------------------------------
"""

import os
import re
import pprint

from libraries import input_files
from libraries.status_file import StatusFile

#------------------------------------------------------------------------------

class StatusDatabase:
    """Class for accessing status information for runs."""

    def __init__(self):
        """Constructor."""

        self.__input_file = input_files.rgt_input_file()
        self.__path_to_tests = self.__input_file.get_local_path_to_tests()

        self.__data = None

    def load(self):
        """Take a snapshot of the harness data and build database form this."""

        self.__data = {}

        for test in self.__input_file.get_tests():

            app, test, nm_iters = test

            self.__data.setdefault(app, {}).setdefault(test, {})

            dir_status = os.path.join(self.__path_to_tests, app, test, 'Status')

            for dname in os.listdir(dir_status):
                if os.path.isdir(os.path.join(dir_status, dname)):
                    self.__data[app][test][dname] = {}

            for test_id in self.__data[app][test]:
                dir_test_id = os.path.join(dir_status, test_id)

                for i, fname in enumerate(os.listdir(dir_test_id)):
                    if os.path.isfile(os.path.join(dir_test_id, fname)):
                    #if i == 0:
                        key_ = re.sub(r'.txt$', '', fname)
                        file_ = open(os.path.join(dir_test_id, fname), 'r')
                        value_ = file_.read()
                        file_.close()
                        self.__data[app][test][test_id][key_] = value_




        #pprint.pprint(self.__data)

        return self  #---for chaining.










#------------------------------------------------------------------------------
