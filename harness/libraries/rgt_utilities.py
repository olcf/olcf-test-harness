#! /usr/bin/env python3

import os
import sys
import time

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

#
# The package provides utilities for the regression test harness.
#

########################################################################
# Returns a unique harnesss id string.
########################################################################
def unique_harness_id():
    # Return a unique id based on current time
    return str(time.time())


class work_space_generator:
    def __init__(self):
        self.__workspace = None

        ws = os.getenv('RGT_PATH_TO_SSPACE')
        if ws == None:
            sys.exit("HARNESS ERROR: Please set RGT_PATH_TO_SSPACE in the environment!")

        # Create workspace if necessary.
        self.__workspace = ws
        os.makedirs(ws, exist_ok=True)

    ########################################################################
    #
    # Returns the value of the workspace.
    #
    ########################################################################
    def get_work_space(self):
        return self.__workspace
    ########################################################################


########################################################################
# Returns a workspace for the harness.
########################################################################
def harness_work_space():
    work_space = work_space_generator()
    return work_space.get_work_space()


########################################################################
# Attempt to create symlink, skip if not possible.
########################################################################
def try_symlink(target, link_name):
    try:
        if not os.path.lexists(link_name):
            os.symlink(target, link_name)
    except KeyboardInterrupt:
        # Allow interrupt from command line.
        raise
    except:
        print(f'HARNESS ERROR: Failed to create symlink {link_name} to {target}.')

########################################################################
# Set environment variables that control harness behavior.
########################################################################
def set_harness_environment(env_vars, override=False):
    for k in env_vars:
        envk = rgt_variable_name_modification(k)
        v = env_vars[k]
        if envk in os.environ and not override:
            print(envk + " is already set. Skipping.")
        else:
            os.environ[envk] = v

def rgt_variable_name_modification(variable_name):
    """Transforms the variable name.

    Parameters
    ----------
    variable_name : str
        The name of the variable to be transformed.

    Returns
    -------
    str:
        The transformed variable name.
    """
    new_var_name = "RGT_" + str.upper(variable_name)
    return new_var_name

