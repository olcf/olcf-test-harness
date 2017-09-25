#! /usr/bin/env python3

# Python package imports
import shlex
import argparse
import sys
import string

# My harness package imports
from libraries import input_files
from libraries import regression_test

#
# Authors: Arnold Tharrington, Wayne Joubert, Veronica Vergera, and Mark Berrill
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

def create_a_parser():
    """Parses the command line arguments.

    Arguments:
    None

    Returns:
    An ArgParser object that contains the information of the 
    command line arguments.

    """
    parser = argparse.ArgumentParser(description="Runs the harness tasks of the selected Application and tests",
                                     add_help=True)
        
    parser.add_argument("--concurrency", 
                        required=False,
                        choices=["serial","parallel"],
                        default="serial",
                        help="The manner of concurrency to run. Serial performs each Application/Subtest in sequence. Parallel is concurrency over the Application/Subtest.")

    parser.add_argument("--inputfile",
                        required=False,
                        default="rgt.input",
                        help="Optional argument to pass an input with a name other than rgt.input.")
    
    parser.add_argument("--loglevel",
                         required=False,
                         choices=["DEBUG","INFO","WARNING", "ERROR", "CRITICAL"],
                         default="INFO",
                         help="Optional argument for logging level")


    help_message =  "This argument controls where stdout and stderr of the submit_executable and build_executable go to. "
    help_message += "The destination can be to the screen, '--stdout_and_stderr==screen', or to logfile(s), '--stdout_and_stderr==logfile'." 
    help_message += "If the concurrency is set to serial, '--concurrency=serial', then stdout and stderr will default to the screen " 
    help_message += "unless '--stdout_and_stderr==logfile'. If concurrency is set to parallel, '--concurrency=parallel', then stdout and stderr " 
    help_message += "will default to logfile(s) unless '--stdout_and_stderr==screen'."
    parser.add_argument("--stdout_and_stderr",
                        required=False,
                        choices=["logfile","screen"],
                        default="screen",
                        help=help_message)
    return parser

def runtests(my_arg_string=None):
    argv = None
    if my_arg_string == None:
        argv = sys.argv[1:]
    else:
        argv = shlex.split(my_arg_string)
       

    #
    # Parse command line arguments
    #
    parser = create_a_parser()
    Vargs = parser.parse_args(argv)
    concurrency = Vargs.concurrency
    inputfile = Vargs.inputfile
    loglevel=Vargs.loglevel
    stdout_stderr=Vargs.stdout_and_stderr

    # Print the effective command line to stdout.
    command_options = "The effective command line is : \n" 
    command_options += "runtests.py "
    command_options += "--concurrency {my_concurrency} " 
    command_options += "--inputfile {my_inputfile} "
    command_options += "--loglevel {my_loglevel} "
    command_options += "--stdout_and_stderr {my_stdouterr}"
    my_effective_command_line = command_options.format(my_concurrency=concurrency,  
                                                       my_inputfile = inputfile,
                                                       my_loglevel = loglevel,
                                                       my_stdouterr = stdout_stderr)
    print(my_effective_command_line)

    # Warn user if running in parallel mode and stdout, stderr is written to screen.
    warning_message = None
    if (concurrency == "parallel") and ( stdout_stderr == "screen") :
        warning_message  = "Warning! You have chosen to run the harness in concurrency mode of parallel \n"
        warning_message += "and writing stdout and stderr of the applications build and submit scripts \n"
        warning_message += "to screen. This may result in the interleaving of the applications stdout and \n"
        warning_message += "stderr which may result in incomprehesible output. It is highly advised to \n"
        warning_message += "to write stderr and stdout to logfiles when running in parallel mode.\n"
        warning_message += "Run 'runtests.py --help' for usage\n\n"
        print(warning_message)
    
    #
    # Read the input
    #    
    ifile = input_files.rgt_input_file(inputfilename=inputfile)
    
    rgt = regression_test.Harness(ifile,
                                  concurrency)
    if concurrency == "serial":
        nm_workers = 1
    elif concurrency == "parallel":
        nm_workers = 2

    rgt.run_me(log_level=loglevel,
               my_effective_command_line=my_effective_command_line,
               my_warning_messages=warning_message,
               nm_workers=nm_workers)

    return rgt
    
if __name__ == "__main__":
    runtests()

