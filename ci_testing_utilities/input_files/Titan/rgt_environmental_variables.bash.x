# This file defines and sets user specific environmental variables for
# running the harness unit tests.


# Add or modify as needed to suit your environment.

    #---------------------------------------------------------------
    # PBS job account id.                                          -
    #---------------------------------------------------------------
    RGT_PBS_JOB_ACCNT_ID='STF006'
    export RGT_PBS_JOB_ACCNT_ID

    #-----------------------------------------------------
    # Path to my work directory.                         -
    #                                                    -
    #-----------------------------------------------------
    MY_MEMBER_WORK=${MEMBERWORK}/stf006
    export MY_MEMBER_WORK
    
    #-----------------------------------------------------
    # Path to harness module file.                       -
    #                                                    -
    #-----------------------------------------------------
    #MY_RGT_MODULE_FILE="/ccs/proj/scgs/NCCS_Test_Harness_Workspace/acceptance-test-harness/test/input_files/Titan/unit_testing/1.0"
    #export MY_RGT_MODULE_FILE

    #---------------------------------------------------------------
    # Path to the harness top level.                               -
    #---------------------------------------------------------------
    PATH_TO_HARNESS_TOP_LEVEL="/ccs/proj/scgs/NCCS_Test_Harness_Workspace/acceptance-test-harness"
    export PATH_TO_HARNESS_TOP_LEVEL

    #-----------------------------------------------------
    # URL to svn repository of acceptance test harness   -
    # applications.                                      -
    #-----------------------------------------------------
    MY_APP_REPO="file:///ccs/sys/adm/data/svn-acceptance/acceptance_project/trunk"
    export MY_APP_REPO


