============================
 Harness Unit Testing Usage
============================

---------------------------
Terminology and Conventions
---------------------------

<harness-top-level>

--------
Overview
--------
The running of the harness unit tests requires 3 steps:

1. Setting up the correct environmental variables.

2. Loading the unit test module.

3. Executing the python unut test command.

Step 1 consists of defining the some environmental variables that
primarily set the path to the harness unit test python source files. There is a 
sample file named "rgt_environmental_variables.bash.x" 
that can be copied and filled with values appropiate for your 
testing environment. Step 2 is loading the harness unit module file. Loading
the harness unit module primarily sets environmental variables that
permits the harness to create the input files in order to run the units tests
as you the user. Step 3 is to execute the python command which lauches the 
harness unit tests.


------
Step 1 
------
Create a temporary working directory and copy the file
<harness-top-level>/test/input_file/Titan/rgt_environmental_variables.bash.x.

