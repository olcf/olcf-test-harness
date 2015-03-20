#! /usr/bin/env python
from libraries import input_files
from libraries import regression_test

#
# Author: Arnold Tharrington
# Email: arnoldt@ornl.gov
# National Center of Computational Science, Scientifc Computing Group.
#

def main():
    #
    # Read the input
    #    
    ifile = input_files.rgt_input_file()

    #
    # Run the regression test.
    #
    rgt = regression_test.run_me(ifile)
    
    
if __name__ == "__main__":
    main()
