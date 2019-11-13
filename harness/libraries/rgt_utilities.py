#! /usr/bin/env python3

import datetime
import os
import sys
from libraries import computers_1

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

import time
#
# The package provides utilities for the regression test harness.
#


class unique_text_string_generator:
    def __init__(self):
        self.__unique_text_string = None

        #
        #Generate the unique text string.
        #
        self.generate_unique_text_string()

    ########################################################################
    #
    # Returns the value of the unique text string.
    #
    ########################################################################
    def get_unique_text_string(self):
        return self.__unique_text_string
    ########################################################################


    ########################################################################
    #
    # Generate the unique text string
    #
    ########################################################################
    def generate_unique_text_string(self):
        self.__unique_text_string = str(time.time())
    ########################################################################



class work_space_generator:
    def __init__(self):
        self.__workspace = None

        #
        # Generate a place to do the work.
        #
        self.generate_work_space()

    ########################################################################
    #
    # Returns the value of the workspace.
    #
    ########################################################################
    def get_work_space(self):
        return self.__workspace
    ########################################################################


    ########################################################################
    #
    # Generate the unique text string
    #
    ########################################################################
    def generate_work_space(self):
        #
        # Get the environmental variable "RGT_PATH_TO_SSPACE".
        #
        ws = os.getenv('RGT_PATH_TO_SSPACE')
        if ws == None:
            sys.exit("HARNESS ERROR: Please set RGT_PATH_TO_SSPACE in the environment!")

        #
        # Assign workspace.
        #
        self.__workspace = ws

        return 

    ########################################################################



########################################################################
# Returns a unique text string.
########################################################################
def unique_text_string():

    # Instantate a string generator.
    string_generator = unique_text_string_generator()

    # Return its value
    return string_generator.get_unique_text_string()


########################################################################
# Returns a workspace for the test.
########################################################################
def test_work_space():

    work_space = work_space_generator()

    # Return its value
    return work_space.get_work_space()


def return_my_computer_with_events_record(taskwords):
    starttimestring = taskwords[0]
    starttimestring = starttimestring.strip()
    starttimewords = starttimestring.split("_")
    startdate = datetime.datetime(int(starttimewords[0]),int(starttimewords[1]),int(starttimewords[2]),
                                  int(starttimewords[3]),int(starttimewords[4]))

    endtimestring = taskwords[1]
    endtimestring = endtimestring.strip()
    endtimewords = endtimestring.split("_")
    enddate = datetime.datetime(int(endtimewords[0]),int(endtimewords[1]),int(endtimewords[2]),
                                  int(endtimewords[3]),int(endtimewords[4]))

    mycomputer = computers_1.create_computer()

    mycomputer.get_event_records(startdate,enddate)

    return mycomputer


########################################################################
# Attempt to create symlink, skip if not possible.
########################################################################
def try_symlink(source, link_name):
    try:
        if not os.path.lexists(link_name):
            os.symlink(source, link_name)
    except KeyboardInterrupt:
        # Allow interrupt from command line.
        raise
    except:
        print(f'HARNESS ERROR: Failed to create symlink {link_name} to {source}.')
