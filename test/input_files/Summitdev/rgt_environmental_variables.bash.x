# This file defines and sets user specific environmental variables for
# running the harness unit tests.


# Add or modify as needed to suit your environment.

#---------------------------------------------------------------
# PBS job account id.                                          -
#---------------------------------------------------------------
RGT_PBS_JOB_ACCNT_ID='STF006ACCEPT'
export RGT_PBS_JOB_ACCNT_ID

#-----------------------------------------------------
# Path to my work directory.                         -
#                                                    -
#-----------------------------------------------------
MY_MEMBER_WORK=/lustre/atlas1/stf006/scratch/arnoldt
export MY_MEMBER_WORK

#-----------------------------------------------------
# Set the test harness module to use.                -
#                                                    -
#-----------------------------------------------------
MY_RGT_MODULE_FILE="my_unit_testing/summitdev_unit_testing"
export MY_RGT_MODULE_FILE

#---------------------------------------------------------------
# Path to the harness top level.                               -
#---------------------------------------------------------------
PATH_TO_HARNESS_TOP_LEVEL="/ccs/proj/scgs/NCCS_Test_Harness_Workspace/acceptance-test-harness"
export PATH_TO_HARNESS_TOP_LEVEL

#-----------------------------------------------------
# URL to svn repository of acceptance test harness   -
# applications.                                      -
#-----------------------------------------------------
MY_APP_REPO='gitlab@gitlab.ccs.ornl.gov/olcf-acceptance/olcf4-acceptance-tests.git'
export MY_APP_REPO

#-----------------------------------------------------
# Rum the module commands to load the test harness   -
# module.                                            -
#-----------------------------------------------------
module use /ccs/proj/ccsstaff/olcf4_acceptance/modulefiles
module load my_unit_testing/summitdev_unit_testing

