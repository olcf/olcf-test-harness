# 
# 
# 
# 

# /usr/bin/env bash

#-----------------------------------------------------
# This program runs the harness unit tests.          -
#                                                    -
# Prerequisites:                                     -
#   The olcf harness test harness must be properly   -
#   initialized or this program will fail            - 
#   with fail in an indeterminate manner.            -
#                                                    -
#-----------------------------------------------------

#-----------------------------------------------------
# Function:                                          -
#    declare_global_variabes                         -
#                                                    -
# Synopsis:                                          -
#   Declares global variables used in this bash      -
#   script.                                          -
#                                                    -
# Positional parameters:                             -
#                                                    -
#-----------------------------------------------------
function declare_global_variabes () {
    # Define some global variables.
    declare -gr PROGNAME=$(basename ${0})

    # Boolean variable for flagging if to perform
    # generic harness unit tests.
    declare -g do_generic_tests=false

    # Boolean variable for flagging if to perform
    # machine specific harness unit tests.
    declare -g do_machine_specific_tests=false
}

#-----------------------------------------------------
# Function:                                          -
#    error_exit                                      -
#                                                    -
# Synopsis:                                          -
#   An error handling function.                      -
#                                                    -
# Positional parameters:                             -
#   ${1} A string containing descriptive error       -
#        message                                     -
#                                                    -
#-----------------------------------------------------
function error_exit {
    echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
    exit 1
}

#-----------------------------------------------------
# function usage() :                                 -
#                                                    -
# Synopsis:                                          -
#   Prints the usage of this bash script.            -
#                                                    -
#-----------------------------------------------------
function usage () {
    column_width=50
    let separator_line_with=2*column_width+1
    help_frmt1="%-${column_width}s %-${column_width}s\n"
    printf "Description:\n"
    printf "\tThis program performs the harness unit tests.\n"
    printf "\tThere are two types of tests:\n\n"
    printf "\t\t- Tests that are independent of the machine you are on\n" 
    printf "\t\t- Tests that are dependent on the machine you are on\n"
    printf "\n"
    printf "\tTo run this program the OLCF harness runtime environment must be properly initialized.\n"
    printf "\tNote that the environment variables :\n\n"
    printf "\t\t - HUT_CONFIG_TAG\n"
    printf "\t\t - HUT_MACHINE_NAME\n"
    printf "\t\t - HUT_PATH_TO_SSPACE\n"
    printf "\t\t - HUT_SCHED_ACCT_ID\n\n"
    printf "\tmust be defined.\n"

    printf "\n"
    printf "Usage:\n"
    printf "\tharness_test_driver.sh [ -h | --help ] [--generic-tests] [ --machine-specific-tests ] \n\n"
    printf "${help_frmt1}" "Option" "Description"
    for ((ip=0; ip < ${separator_line_with}; ip++));do
        printf "%s" "-"
    done
    printf "\n"
    printf "${help_frmt1}" "-h | --help" "Prints the help message"
    printf "${help_frmt1}" "--generic-tests" "Performs generic harness unit tests."
    printf "${help_frmt1}" "--machine-specific-tests" "Performs machine specific harness unit tests."
}


#-----------------------------------------------------
# Function:                                          -
#    check_hut_variables                             -
#                                                    -
# Synopsis:                                          -
#   Checks that the HUT environmental variables are  -
#   set.                                             -
#                                                    -
# Positional parameters:                             -
#                                                    -
#-----------------------------------------------------
function check_hut_variables {
    if [ -z ${HUT_CONFIG_TAG} ];then
        error_exit "The environmental variable HUT_CONFIG_TAG is not set."
    fi

    if [ -z ${HUT_MACHINE_NAME} ];then
        error_exit "The environmental variable HUT_MACHINE_NAME is not set."
    fi

    if [ -z ${HUT_PATH_TO_SSPACE} ];then
        error_exit "The environmental variable HUT_PATH_TO_SSPACE is not set."
    fi

    # Make sure HUT_PATH_TO_SSPACE is not the users ${HOME} directory.
    if [[ ${HUT_PATH_TO_SSPACE} -ef ${HOME}  ]];then
         error_message="The environmental variable HUT_PATH_TO_SSPACE points to your home directory: ${HOME}.\n"
         error_message+="Change HUT_PATH_TO_SSPACE to point to another directory so as to not inadvertly erase any important files.\n"
         error_exit "${error_message}"
    fi 

    if [ -z ${HUT_SCHED_ACCT_ID} ];then
        printf "The environmental variable HUT_SCHED_ACCT_ID is not set."
        exit 1
    fi
}

#-----------------------------------------------------
# Process the arguments to this bash script.         -
#                                                    -
#-----------------------------------------------------
function parse_command_line {
    eval set -- $@
    while true;do
        case ${1} in
            -h | --help) 
                usage
                shift
                exit 0;;

            --generic-tests )
                do_generic_tests=true
                shift;;

            --machine-specific-tests )
                do_machine_specific_tests=true
                shift;;

            -- ) 
                shift
                break;;

            * ) 
                echo "Internal parsing error!"
                usage
                exit 1;;
        esac
    done
}


#-----------------------------------------------------
#                                                    -
# Start of main body of bash script.                 -
#                                                    -
#-----------------------------------------------------
function main () {
    declare_global_variabes

    # Validate and parse the command line options.
    long_options=help,generic-tests,machine-specific-tests
    short_options=h
    OPTS=$(getopt --options ${short_options} --long ${long_options} --name "${PROGNAME}" -- "$@")
    if [ $? != 0 ]; then
         error_exit "The function get_opt failed ... exiting"
    fi

    parse_command_line ${OPTS}
    if [ $? != 0 ]; then
         error_exit "The function parse_command_line failed ... exiting."
    fi

    if [[ ${do_generic_tests} ]];then
        echo "Performing generic tests.\n"
        run_generic_unit_tests.py
    fi

    if [[ ${do_machine_specific_tests} ]];then
        # Verify that the HUT environmental variables are set.
        check_hut_variables
        if [ $? != 0 ];then
            error_exit "The function check_hut_variables failed ... exiting."
        fi

        # Remove the prior scratch space.
        if [[ -d "${HUT_PATH_TO_SSPACE}" ]];then
            rm -rf ${HUT_PATH_TO_SSPACE}/* 
        fi

        # Remove all prior test runs.
        rm -rf MPI_HelloWorld_*/
        rm -f main.log

        echo "Performing machine specific tests."
        run_machine_specific_unit_tests.py  --machine ${HUT_MACHINE_NAME} --harness-config-tag $HUT_CONFIG_TAG
    fi
}
#-----------------------------------------------------
#                                                    -
# End of main body of bash script.                   -
#                                                    -
#-----------------------------------------------------

main $@
