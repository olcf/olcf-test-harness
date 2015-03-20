#! /usr/bin/env python
import os
import getopt
import sys
import re
import time

def main ():

    #
    # Get the command line arguments.
    #
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hi:p:c:")

    except getopt.GetoptError:
            usage()
            sys.exit(2)

    #
    # Parse the command line arguments.
    #
    for o, a in opts:
        if o == "-p":
            path_to_lock_file = a
        elif o == "-i":
            test_id_string = a
        elif o == "-c":
            lockcommand = a
        elif o == ("-h", "--help"):
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()

    if lockcommand == "lock":
        try_again = 1
        while (try_again):
            lock_file_exists = os.path.lexists(path_to_lock_file)

            if lock_file_exists:
                pass
            else:
                file_object = open(path_to_lock_file,"w")
                file_object.write(test_id_string)
                file_object.close()
                try_again = 0

    elif lockcommand == "unlock":
        try_again = 1
        test_id_regexp = re.compile(test_id_string)
        while (try_again):
            lock_file_exists = os.path.lexists(path_to_lock_file)

            if lock_file_exists:
                file_object = open(path_to_lock_file,"r")
                lines =  file_object.readlines()
                file_object.close()

                for line in lines:
                    if test_id_regexp.match(line):
                        print "macthing lock, removing lock"
                        os.remove(path_to_lock_file)
                        try_again = 0
                        break
            else:
                try_again = 0
    else:
        usage()

        
def usage():
    print "Usage: filelock.py [-h|--help] [-i <test_id_string>] [-p <path_to_lock_file>] [-c <lock_command>]"
    print "A program that manipulates the harness file locks"
    print
    print "-h, --help            Prints usage information."                              
    print "-p <path_to_lock_file>  The absoulte path to the lock file."
    print "-i <test_id_string>   The test string unique id."
    print "-c <lock_command>     The lock command [lock | unlock ]."



if __name__ == '__main__':
    main()
