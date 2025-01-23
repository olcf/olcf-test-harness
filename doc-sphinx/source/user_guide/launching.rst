.. _section_launching_oth:

=================
Quick-Start Guide
=================

This section serves as a quick-start guide for installing the OTH and launching an existing test.
For creating a new test, see :ref:`section_new_test`.
For adding support for a new machine, see :ref:`section_new_machine`.

.. _oth_setup:

Installation
------------

To launch the OLCF Test Harness (OTH) you must first access the harness code.
This can be done in two ways: by obtaining your own copy of the code or using the centralized harness code that is available on most OLCF systems.

Option 1: Using the centralized (pre-built) OTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On Andes and Frontier
"""""""""""""""""""""

On most OLCF machines, the code is already installed in: */sw/acceptance/olcf-test-harness*

Setup the environment:

.. code-block:: bash

    export OLCF_HARNESS_DIR=/sw/acceptance/olcf-test-harness
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    # Machine name examples: andes, frontier, odo
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
    You must have the *$OLCF_HARNESS_MACHINE.ini* file in your current directory or in *$OLCF_HARNESS_DIR/configs*.
    An *example_machine.ini* file is provided in the *$OLCF_HARNESS_DIR/configs* directory,
    and OLCF machine examples are provided in the *configs/olcf_examples* directory.
    For creating a new machine, see :ref:`section_new_machine`.


.. launching_oth:

Launching the OTH
-----------------

Basic Usage
^^^^^^^^^^^

Create a directory where you will place input files. No computation will be done here:

.. code-block:: bash

    mkdir summit_testshot
    cd summit_testshot

Prepare an input file of tests (e.g., *rgt.input.summit*).
In the file, set ``Path_to_tests`` to the location where you would like application source and run files to be kept
(note that the directory provided must be an existing directory on a file system visible to the current machine).
Next, provide one or more tests to run in the format ``Test = <app-name> <test-name>``.
In this example for Summit, the application **hello_mpi** is used and we specify two tests: **c_n001** and **c_n002**.

.. note::

    Tests may be hosted in GitHub/GitLab repositories, or may be placed on the file system in the directory specified by ``Path_to_tests``.
    The OTH can automatically clone Git repositories from remote servers.
    Configuration settings for Git repositories are in the *$OLCF_HARNESS_MACHINE.ini* file (see :ref:`section_new_machine` or :ref:`env_vars_config`).
    Applications not hosted in GitHub/GitLab must be manually placed in ``Path_to_tests``.

.. code-block:: bash

    ################################################################################
    #  Set the path to the top level of the application directory.                 #
    ################################################################################
    
    Path_to_tests = /some/path/to/my/applications
    
    Test = hello_mpi c_n001
    Test = hello_mpi c_n002


Set a scratch area for this specific instance of the harness (a default is set from *$OLCF_HARNESS_MACHINE.ini*, but this is how to change from the default):

.. code-block:: bash

    export RGT_PATH_TO_SSPACE=<some path in the file system>/Scratch


The latest version of the harness supports command line tasks as well as input file tasks.
If no tasks are provided in the input file, it will use the command line mode.
To launch via the command line, use a command like the following:

.. code-block:: bash

    # Preferred to checkout separately, to verify that the checkout was successful
    runtests.py --inputfile rgt.input.summit --mode checkout
    runtests.py --inputfile rgt.input.summit --mode start stop

To launch tasks in the input file instead of the command-line, add lines like the following to ``rgt.input.summit``:

.. code-block:: text

    # 1 task per line
    harness_task start
    harness_task stop


When using the checkout mode, the application source repository will be cloned to the *<Path_to_tests>/<app-name>* directory for all the tests,
but no tests will be run.

After using the start mode, results of the most recent test run can be found in *<Path_to_tests>/<app-name>/<test-name>/Run_Archive/<testid>*.
Results of the most recent test run can be found in the *<Path_to_tests>/<app-name>/<test-name>/Run_Archive/latest* symbolic link.

.. note::

    The *latest* link may not update cleanly if multiple instances of the same test are running simultaneously.
    The OTH will print a warning, but will continue running.


.. _command_line_options:

Command-line Options
^^^^^^^^^^^^^^^^^^^^

The OTH receives configurations from two primary methods: command-line flags and environment variables.
This section details the command-line parameters and the next section details available environment variables.

The primary OTH driver script, ``runtests.py``, supports the following command-line parameters:

.. code-block::

    -h,--help                           show help message and exit
    -i,--inputfile INPUTFILE            Input file name (default: rgt.input)
    -c,--configfile CONFIGFILE          Configuration file name (default: ${OLCF_HARNESS_MACHINE}.ini)
    -l,--loglevel LOGLEVEL              Logging level (default: NOTSET)
                    Options: [NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL]
    -o,--output {screen,logfile}        Destination for harness stdout/stderr messages (default: 'screen')
                    Options: [screen,logfile]
                            'screen'  - print messages to console (default)
                            'logfile' - print messages to log file
    -m,--mode MODE [MODE ...]           Specify the mode(s) to run the harness with (default: 'use_harness_tasks_in_rgt_input_file')
                    Options: [use_harness_tasks_in_rgt_input_file,checkout,start,stop,status]
                            'checkout'   - checkout application tests listed in input file
                            'start'      - start application tests listed in input file
                            'stop'       - stop application tests listed in input file
                            'status'     - check status of application tests listed in input file

    --fireworks                         Use FireWorks to run harness tasks (beta)
    -sb, --separate-build-stdio         Separate output from build into build_out.stderr.txt and build_out.stdout.txt

.. note::

    The ``--loglevel`` flag currently does not apply to all output from the OTH.
    This issue is tracked by `Issue 130 <https://github.com/olcf/olcf-test-harness/issues/130>`_.

.. _runtime_configurable_parameters:

Run-time environment parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OTH is designed to automatically ingest some parameters from user-set environment variables at launch time.
Nearly all parameters in the *$OLCF_HARNESS_MACHINE.ini* file can be directly overridden by a corresponding environment variable.
For example, *git_reps_branch* is a parameter in *$OLCF_HARNESS_MACHINE.ini* that specifies the branch of the remote repository to clone.
The *RGT_GIT_REPS_BRANCH* environment variable can be used to override this value at launch time.
The general precedence of configuration options from lowest to highest is:

1. *$OLCF_HARNESS_MACHINE.ini*
2. User-set environment variables (ie, *RGT_GIT_REPS_BRANCH*, *RGT_PROJECT_ID*)
3. *<Path_to_tests>/<app-name>/<test-name>/Scripts/rgt_test_input.ini*

The specific parameters are defined in :ref:`section_new_test` and :ref:`section_new_machine`.

The exception to this is setting the batch queue and project ID used for submission.
The precedence of configuration options for the batch queue and project ID from lowest to highest is:

1. **batch_queue** and **project_id** from *$OLCF_HARNESS_MACHINE.ini* (overridden by setting **RGT_BATCH_QUEUE** and **RGT_PROJECT_ID** at launch)
2. **batch_queue** and **project_id** from *<Path_to_tests>/<app-name>/<test-name>/Scripts/rgt_test_input.ini*
3. User-set environment variables: **RGT_SUBMIT_QUEUE** and **RGT_SUBMIT_ACCT**

Since the test configuration overrides the machine configuration for these two variables, the user cannot use the same environment variable names to override the settings.
The test configuration will just override whatever the user sets, because the OTH does not know who sets **RGT_BATCH_QUEUE** -- the user or the *machine.ini*.
So, two separate variables are used to override the machine and test configuration: **RGT_SUBMIT_QUEUE** for setting a batch queue and **RGT_SUBMIT_ACCT** for setting the account ID for submission.


.. understanding_output:

Finding Test Output
-------------------

This section details where all output files can be found once a harness run completes.
There are 4 directories referenced in this section:

- **$BUILD_DIR** - the build directory, equal to **$RGT_PATH_TO_SSPACE/<app>/<test>/<test-id>/build_directory**
- **$WORK_DIR** - equal to **$RGT_PATH_TO_SSPACE/<app>/<test>/<test-id>/workdir**
- **$RESULTS_DIR** - the directory used to launch the job and store relevant output, equal to **<Path_to_tests>/<app>/<test>/Run_Archive/<test-id>**
- **$STATUS_DIR** - the directory used to store harness status files, equal to **<Path_to_tests>/<app>/<test>/Status/<test-id>**

Build, Submit, and Check Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each OTH test run consists of 4 primary stages -- build, submit, run, and check, as can be seen in :ref:`section_overview`.
The build, submit, and check stages have pre-defined locations for the output:

- build output: **${BUILD_DIR}/output_build.txt**
- submit output: **${RESULTS_DIR}/submit.{out,err}**
- check output: **${RESULTS_DIR}/output_check.txt**

Application Output
^^^^^^^^^^^^^^^^^^

Output from the executable run can be found in one of two places.

- Uncaptured output will go to the scheduler's stdout/stderr mechanism, and will commonly be found in **${RESULTS_DIR}**
- Any output files created by the application should be in **${WORK_DIR}**

Harness-maintained Log Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OTH also produces log files, which contain messages from the harness with data useful for debugging failed tests.
These log files can be used to check internal error messages reported by extensions of the OTH such as database event and metric logging.
These log files are found in **${RESULTS_DIR}/LogFiles**.
