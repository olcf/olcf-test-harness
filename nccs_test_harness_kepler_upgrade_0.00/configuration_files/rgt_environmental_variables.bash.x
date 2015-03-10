#! /usr/bin/env bash

#
# Author: Arnold Tharrington
# Email: arnoldt@ornl.gov
# National Center of Computational Science, Scientifc Computing Group.
#

#
# This file defines and sets user specific environmental variables for the test 
# harness.
#


# Add or modify as needed to suit your environment.

    #---------------------------------------------------------------
    # Absoulte path to scratch space location.                     -
    #---------------------------------------------------------------
    RGT_PATH_TO_SSPACE='/tmp/work/arnoldt/pbs_path_workspace'
    export RGT_PATH_TO_SSPACE

    #---------------------------------------------------------------
    # PBS job account id.                                          -
    #---------------------------------------------------------------
    RGT_PBS_JOB_ACCNT_ID='stf006bf'
    export RGT_PBS_JOB_ACCNT_ID

    #---------------------------------------------------------------
    # Set the path to this file                                    -
    #---------------------------------------------------------------
    RGT_ENVIRONMENTAL_FILE='/spin/home/arnoldt/XT4_WORK_FIX_SCRIPTS/IMB_work/rgt_environmental_variables.bash.x'
    export RGT_ENVIRONMENTAL_FILE

    #---------------------------------------------------------------
    # Name of nccs test harness module to load                     -
    #---------------------------------------------------------------
    RGT_NCCS_TEST_HARNESS_MODULE='nccs_test_harness/0.2'
    export RGT_NCCS_TEST_HARNESS_MODULE
