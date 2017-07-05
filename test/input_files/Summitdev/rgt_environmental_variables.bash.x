# This file defines and sets user specific environmental variables for
# running the harness unit tests.


# Add or modify as needed to suit your environment.

#-----------------------------------------------------
# Define the location to run the harness tests.      -
#                                                    -
#                                                    -
#-----------------------------------------------------
MY_RGT_TEST_DIRECTORY=${HOME}/Harness_Unit_Testing_Input
export MY_RGT_TEST_DIRECTORY

#-----------------------------------------------------
# Define the location of the harness master          -
# environmental file.                                -
#                                                    -
#-----------------------------------------------------
MY_RGT_MASTER_ENVIRONMENTAL_FILE=${MY_RGT_TEST_DIRECTORY}/rgt.environmental_variables.sh
export MY_RGT_MASTER_ENVIRONMENTAL_FILE

#---------------------------------------------------------------
# PBS job account id.                                          -
#---------------------------------------------------------------
RGT_PBS_JOB_ACCNT_ID='STF006'
export RGT_PBS_JOB_ACCNT_ID

MY_RGT_PROJECTID='STF006'
export MY_RGT_PROJECTID

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
MY_APP_REPO='gitlab@gitlab.ccs.ornl.gov:olcf-acceptance/olcf4-acceptance-tests.git'
export MY_APP_REPO

#-----------------------------------------------------
# Set the branch of the repository.                  -
#                                                    -
#-----------------------------------------------------
MY_APP_REPO_BRANCH="summitdev_hello_world_branch"
export MY_APP_REPO_BRANCH

#-----------------------------------------------------
# Rum the module commands to load the test harness   -
# module.                                            -
#-----------------------------------------------------
module load ${MY_RGT_MODULE_FILE}

#-----------------------------------------------------
# Define the path to the scratch space.              -
#                                                    -
#-----------------------------------------------------
RGT_PATH_TO_SSPACE='/lustre/atlas1/stf006/scratch/arnoldt/Harness_Unit_Testing_Scratch_Space'
export RGT_PATH_TO_SSPACE

#-----------------------------------------------------
# Define the path to the unit test git repo.         -
#                                                    -
#-----------------------------------------------------
PATH_TO_TEST_GIT_REPOSITORY=${HOME}/MY_HARNESS_TEST_REPO
export PATH_TO_TEST_GIT_REPOSITORY

#-----------------------------------------------------
# Define the internal path to the unit test git      -
# applications.                                      -
#                                                    -
#                                                    -
#-----------------------------------------------------
PATH_RELATIVE_PATH_TO_APPS_WRT_TEST_GIT_REPOSITORY=trunk/ANY_MACHINE
export PATH_RELATIVE_PATH_TO_APPS_WRT_TEST_GIT_REPOSITORY

