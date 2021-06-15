============================
Overview of the Test Harness
============================

Purpose
=================

.. toctree::
   :maxdepth: 1

The OLCF Test Harness (OTH) helps automate the testing of applications, tools,
and other system software. Users of the OTH have the flexibility to run
individual standalone tests or to simulate production workloads by running a
large collection of tests continuously. Each test provides its own scripts that
support the core operations of building executables, running jobs, and checking
test results.

Execution Overview
=====================

*runtests.py* is the program used to execute the OTH. Users provide a test
input file that lists the set of application tests to run, and a command-line
run mode option controls whether to run a single iteration (**\-\-mode start stop**)
or continuously (**\-\-mode start**). In continuous mode, the test job script has the
option to resubmit another iteration of the test.  

A brief logical flow of harness execution follows:

....

* Read 'RGT_PATH_TO_SSPACE' from environment (OTH_SCRATCH)
* Read 'Path_to_tests' from inputfile (OTH_APPS)
* Read Machine configurations from <machine>.ini
* foreach (app,test) in inputfile:
    #. generate unique id (UID) 
    #. create *Run_Archive* and *Status* directories @ *OTH_APPS/app/test/{Run_Archive,Status}/UID* 
    #. create scratch directory (APPTEST_SCRATCH) @ *OTH_SCRATCH/app/test/UID*
    #. recursively copy *OTH_APPS/app/Source/ to APPTEST_SCRATCH/build_directory/*
    #. change working directory to *APPTEST_SCRATCH/build_directory/*, and execute test's build command
    #. if build script succeeds, generate test's job script from template in *OTH_APPS/app/test/Scripts*
    #. submit job script to scheduler - when job runs, it:
         - changes working directory to *APPTEST_SCRATCH/workdir* (after creating it
           if necessary)
         - copies any needed input files from *OTH_APPS/app/test*
         - runs the test executable
         - copies any needed output files back to the *Run_Archive* directory
         - runs the test's check command, passing it the *Run_Archive* directory
           location
         - if in continuous mode, start another iteration of the harness test end
