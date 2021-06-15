=====================================
Launching the OLCF Test Harness (OTH)
=====================================

To launch the OLCF Test Harness (OTH) you must first access the harness code.
This can be done in two ways, one by obtaining your own copy of the code or
using the centralized harness code that will be available on the system under
test.

OTH Setup
---------

Option 1: Using the centralized (pre-built) OTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On Lyra
"""""""

The code is already installed in: */sw/lyra/acceptance/olcf-test-harness*

Setup the environment:

.. code-block:: bash

    export OLCF_HARNESS_DIR=/sw/lyra/acceptance/olcf-test-harness
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    export OLCF_HARNESS_MACHINE=lyra

On Spock
""""""""

The code is already installed in: */ccs/proj/stf016/spock_acpt/olcf-test-harness*

Setup the environment:

.. code-block:: bash

    export OLCF_HARNESS_DIR=/ccs/proj/stf016/spock_acpt/olcf-test-harness/
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    export OLCF_HARNESS_MACHINE=spock

Option 2: Using your own copy of the harness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone the repo on the target system:

.. code-block:: bash

    git clone gitlab@gitlab.ccs.ornl.gov:olcf-system-test/olcf-test-harness.git

Setup the environment:

.. code-block:: bash

    cd olcf-test-harness
    export OLCF_HARNESS_DIR=``pwd``
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    export OLCF_HARNESS_MACHINE=<machine>


Launching the OTH
-----------------

Create a directory for your run - this is where you will place input files and
retrieve a copy of OTH log files. No computation will be done here:

.. code-block:: bash

    mkdir lyra_testshot
    cd lyra_testshot

Prepare an input file of tests (e.g., *rgt.input.lyra*). In the file, set
``Path_to_tests`` to the location where you would like application source and
run files to be kept (note that the directory provided must be an existing
directory on a file system visible to the current machine). Next, provide one
or more tests to run in the format ``Test = <app-name> <test-name>``. In this
example for Lyra, the application **hello_mpi** is used and we specify two
tests: **c_n001** and **c_n002**.

.. code-block:: bash

    ################################################################################
    #  Set the path to the top level of the application directory.                 #
    ################################################################################
    
    Path_to_tests = /some/path/to/my/applications
    
    Test = hello_mpi c_n001
    Test = hello_mpi c_n002


Set a different scratch area for this specific instance of the harness (a
default is set but this lets you change the default):

.. code-block:: bash

    export RGT_PATH_TO_SSPACE=<some path in the file system>/Scratch


The latest version of the harness supports command line tasks as well as input
file tasks. If no tasks are provided in the input file, it will use the command
line mode. To launch via the CLI:

.. code-block:: bash

    runtests.py --inputfile rgt.input.lyra --mode checkout
    runtests.py --inputfile rgt.input.lyra --mode start
    runtests.py --inputfile rgt.input.lyra --mode checkout start stop


When using the checkout mode, the application source repository will be cloned
to the *<Path_to_tests>/<app-name>* directory.


After using the start mode, results of the most recent test run can be found in
*<Path_to_tests>/<app-name>/<test-name>/Run_Archive/latest*.
