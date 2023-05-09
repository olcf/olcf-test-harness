=====================================
Launching the OLCF Test Harness (OTH)
=====================================

To launch the OLCF Test Harness (OTH) you must first access the harness code.
This can be done in two ways: by obtaining your own copy of the code or using the centralized harness code that will be available on each system under test.

OTH Setup
---------

Option 1: Using the centralized (pre-built) OTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On Andes, Crusher, Frontier, and Summit
"""""""""""""""""""""""""""""""""""""""

On most OLCF machines, the code is already installed in: */sw/acceptance/olcf-test-harness*

Setup the environment:

.. code-block:: bash

    export OLCF_HARNESS_DIR=/sw/acceptance/olcf-test-harness
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    # Machine name examples: andes, crusher, frontier, summit
    # Check ${OLCF_HARNESS_DIR}/configs/*.ini to see all available machines
    export OLCF_HARNESS_MACHINE=<machine_name>

Option 2: Using your own copy of the harness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone the repo on the target system:

.. code-block:: bash

    git clone https://github.com/olcf/olcf-test-harness.git

Setup the environment:

.. code-block:: bash

    cd olcf-test-harness
    export OLCF_HARNESS_DIR=${PWD}
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    export OLCF_HARNESS_MACHINE=<machine_name>

.. note::
    You must have the *$OLCF_HARNESS_MACHINE.ini* file in a directory searched by your PATH environment variable for your specified machine.
    In the centralized harness, this is provided for you in the *$OLCF_HARNESS_DIR/configs* directory.
    An *example_machine.ini* file is provided in the *configs* directory,
    and OLCF machine examples are provided in the *configs/olcf_examples* directory.

Launching the OTH
-----------------

Getting Started
^^^^^^^^^^^^^^^

Create a directory for your run - this is where you will place input files and retrieve a copy of OTH log files. No computation will be done here:

.. code-block:: bash

    mkdir summit_testshot
    cd summit_testshot

Prepare an input file of tests (e.g., *rgt.input.summit*).
In the file, set ``Path_to_tests`` to the location where you would like application source and run files to be kept
(note that the directory provided must be an existing directory on a file system visible to the current machine).
Next, provide one or more tests to run in the format ``Test = <app-name> <test-name>``.
In this example for Summit, the application **hello_mpi** is used and we specify two tests: **c_n001** and **c_n002**.

.. note::

    Tests may be hosted in GitHub/GitLab, or may be placed on the file system in the directory specified by ``Path_to_tests``.
    The OTH can automatically clone Git repositories from remote servers.
    Configuration settings for Git repositories are in the *$OLCF_HARNESS_MACHINE.ini* file.
    Applications not hosted in GitHub/GitLab must be manually placed in ``Path_to_tests``.

.. code-block:: bash

    ################################################################################
    #  Set the path to the top level of the application directory.                 #
    ################################################################################
    
    Path_to_tests = /some/path/to/my/applications
    
    Test = hello_mpi c_n001
    Test = hello_mpi c_n002


Set a different scratch area for this specific instance of the harness (a default is set from *$OLCF_HARNESS_MACHINE.ini*, but this lets you change the default):

.. code-block:: bash

    export RGT_PATH_TO_SSPACE=<some path in the file system>/Scratch


The latest version of the harness supports command line tasks as well as input file tasks.
If no tasks are provided in the input file, it will use the command line mode.
To launch via the CLI, use a command like the following:

.. code-block:: bash

    runtests.py --inputfile rgt.input.lyra --mode checkout
    runtests.py --inputfile rgt.input.lyra --mode start
    runtests.py --inputfile rgt.input.lyra --mode checkout start stop

To launch tasks in the input file, add lines like the following to ``rgt.input.summit``:

.. code-block:: text

    # 1 task per line
    harness_task start
    harness_task stop


When using the checkout mode, the application source repository will be cloned to the *<Path_to_tests>/<app-name>* directory for all the tests,
but no tests will be run.

After using the start mode, results of the most recent test run can be found in *<Path_to_tests>/<app-name>/<test-name>/Run_Archive/latest*.


Run-time configurable parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OTH is designed to automatically ingest many parameters from user-set environment variables at launch time.
All parameters in the *$OLCF_HARNESS_MACHINE.ini* file can be overridden by a corresponding environment variable.
For example, *git_reps_branch* is a parameter in *$OLCF_HARNESS_MACHINE.ini* that specifies the branch of the remote repository to clone.
The *RGT_GIT_REPS_BRANCH* environment variable can be used to override this value at launch time.
The precedence of configuration options from lowest to highest is:

1. *$OLCF_HARNESS_MACHINE.ini*
2. User-set environment variables (ie, *RGT_GIT_REPS_BRANCH*, *RGT_PROJ_ID*)
3. *<Path_to_tests>/<app-name>/<test-name>/Scripts/rgt_test_input.[ini,txt]*

The specific parameters are discussed in the sections for adding new tests and new machines to the OTH.

