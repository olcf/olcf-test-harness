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

.. image:: /images/OTH_flowchart.jpg
    :align: center
    :width: 60%
    :alt: OTH Flowchart
