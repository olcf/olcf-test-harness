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

To launch the OLCF Test Harness (OTH) you must first access the core harness code.
This can be done in two ways: by obtaining your own copy of the code or using the centralized harness code that is available on most OLCF systems.

Option 1: Using the centralized (pre-built) OTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On Riker and Frontier
"""""""""""""""""""""

On all OLCF machines, the latest release of the code is already installed in: */sw/acceptance/olcf-test-harness*

Setup the environment:

.. code-block:: bash

    export OLCF_HARNESS_DIR=/sw/acceptance/olcf-test-harness
    export PATH=${OLCF_HARNESS_DIR}/bin:${PATH}
    # Or, use the module
    #module use $OLCF_HARNESS_DIR/modulefiles
    #module load olcf_harness

    # Machine name examples: riker, frontier, odo
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
    export PATH=${PWD}/bin:${PATH}
    # Or, use the legacy environment module to do the PATH modification
    #module use $OLCF_HARNESS_DIR/modulefiles
    #module load olcf_harness

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

There are 3 directory trees that the OTH expects to see:

1. "Launch" directory: where you run the ``othctl run`` command from, contains the input files defining which tests to run.
2. "Path_to_tests" directory: where the content of each app-test is cloned or developed locally.
3. "Scratch" directory: where the OTH automatically populates build & work directories for use within the test.

First, create a launch directory where you will place the ``othctl run`` input files, which instructs the OTH on which tests to launch:

.. code-block:: bash

    mkdir frontier_testshot
    cd frontier_testshot

Prepare an input file of tests in this directory (e.g., *rgt.input.frontier*).
Provide one or more tests to run in the format ``Test = <app-name> <test-name>``.
In the example below, the application **hello_mpi** is used and we specify two tests: **c_n001** and **c_n002**.
Either the *RGT_PATH_TO_TESTS* environment variable or ``Path_to_tests`` in the input file must be set, and provide a path to a directory that holds the application-test configurations (e.g., for ``othctl run --mode start -i rgt.inp``, ``$RGT_PATH_TO_TESTS/<app>/<test>`` should exist).

.. note::

    Tests may be hosted in GitHub/GitLab repositories, or may be placed on the file system in the directory specified by ``Path_to_tests``/*RGT_PATH_TO_TESTS*.
    The OTH can also automatically clone Git repositories from remote servers.
    Configuration settings for Git repositories are in the *$OLCF_HARNESS_MACHINE.ini* file (see :ref:`section_new_machine` or :ref:`env_vars_config`).
    Applications not hosted in GitHub/GitLab should be manually placed in ``Path_to_tests``.

.. code-block:: bash

    # Path_to_tests can be specified here instead of the RGT_PATH_TO_TESTS environment variable, if desired
    #Path_to_tests = /some/path/to/my/applications
    
    Test = hello_mpi c_n001
    Test = hello_mpi c_n002

For convenience, the ``Include`` keyword reads in another harness input file, adding the tests, paths, and tasks to the current harness parameters.
``Path_to_tests`` is set to the first value encountered while parsing the input files.
For example:

.. code-block:: bash

    Path_to_tests = /some/path/to/my/applications

    Include 1-node-tests.inp
    Include 2-node-tests.inp

Second, set a scratch area for this specific instance of the harness (a default can be set in *$OLCF_HARNESS_MACHINE.ini*, this is how to override the default):

.. code-block:: bash

    export RGT_PATH_TO_SSPACE=/some/path/to/my/Scratch
    # optional (in place of Path_to_tests in input file):
    #export RGT_PATH_TO_TESTS=/some/path/to/my/applications


The harness supports providing tasks/modes on the command-line or in the input file.
If no tasks are provided in the input file, ``othctl run`` will use the command line mode.
To launch via the command line, use a command like the following:

.. code-block:: bash

    # Preferred to checkout separately, to verify that the checkout was successful
    othctl run -i rgt.input.frontier --mode checkout
    othctl run -i rgt.input.frontier --mode start stop

To launch tasks in the input file instead of the command-line, add lines like the following to ``rgt.input.frontier``:

.. code-block:: text

    # 1 task per line
    harness_task check_out_tests
    harness_task start_tests
    harness_task stop_tests

When using the checkout mode, the application source repository will be cloned to the *<Path_to_tests>/<app-name>* directory for all the tests, but no tests will be run.
If the repository already exists, no action will be taken.
Updating the repo via ``git pull`` or ``git fetch`` must be done outside of the test harness.

After using the *start* mode, results can be found in *<Path_to_tests>/<app-name>/<test-name>/Run_Archive/<testid>*.
Results of the most recent test run can be found in the *<Path_to_tests>/<app-name>/<test-name>/Run_Archive/latest* symbolic link.

.. note::

    The *latest* link may not update cleanly if multiple instances of the same test are running simultaneously.
    The OTH will print a warning, but will continue running.


.. _command_line_options:

Command-line Options
^^^^^^^^^^^^^^^^^^^^

The OTH receives configurations from two primary methods: command-line flags and environment variables.
This section details the command-line parameters and the next section details available environment variables.

The primary OTH run command, ``othctl run``, supports the following command-line parameters:

.. code-block::

    usage: othctl run [-h] [-i INPUT_FILE] [--shuffle] [-o {screen,logfile}]
                    [-m {checkout,start,stop,status} [{checkout,start,stop,status} ...]]
                    [-sb] [--reuse-first-build]
                    [--reuse-build-from-id REUSE_BUILD_FROM_ID]
                    [--app-filter APP_FILTER] [--test-filter TEST_FILTER]

    optional arguments:
    -h, --help            show this help message and exit
    -i INPUT_FILE, --input-file INPUT_FILE
                            input file (default: rgt.input)
    --shuffle             shuffle the test launch order (default: False)
    -o {screen,logfile}, --output {screen,logfile}
                            test output method (default: screen)
    -m {checkout,start,stop,status} [{checkout,start,stop,status} ...], --mode {checkout,start,stop,status} [{checkout,start,stop,status} ...]
                            perform checkout, start, stop, or status on
                            application tests listed in the input file (default:
                            ['use_input_file'])
    -sb, --separate-build-stdio
                            separate build output into build_out.stderr.txt and
                            build_out.stdout.txt (default: False)
    --reuse-first-build   for re-submittable tests, re-use the first build in
                            the chain (default: False)
    --reuse-build-from-id REUSE_BUILD_FROM_ID
                            re-use build from specified test ID (default: None)
    --app-filter APP_FILTER
                            comma-separated list of regular expressions or strings
                            used to select specific applications from the provided
                            input file (default: [])
    --test-filter TEST_FILTER
                            comma-separated list of regular expressions or strings
                            used to select specific tests from the provided input
                            file (default: [])


.. _runtime_configurable_parameters:

Run-time environment parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OTH is designed to automatically ingest some parameters from user-set environment variables at launch time.
Nearly all parameters in the *$OLCF_HARNESS_MACHINE.ini* file can be directly overridden by a corresponding environment variable.
For example, *git_reps_branch* is a parameter in *$OLCF_HARNESS_MACHINE.ini* that specifies the branch of the remote repository to clone.
The *RGT_GIT_REPS_BRANCH* environment variable can be used to override this value at launch time.
The general precedence of configuration options from lowest to highest is:

1. *$OLCF_HARNESS_MACHINE.ini* (lowest priority)
2. User-set environment variables (ie, *RGT_GIT_REPS_BRANCH*, *RGT_PROJECT_ID*)
3. *<Path_to_tests>/<app-name>/<test-name>/Scripts/rgt_test_input.ini* (highest priority)

The specific parameters are defined in :ref:`section_new_test` and :ref:`section_new_machine`.

The exception to this is setting the batch queue and project ID used for submission.
The precedence of configuration options for the batch queue and project ID from lowest to highest is:

1. **batch_queue** and **project_id** from *$OLCF_HARNESS_MACHINE.ini* (overridden by setting **RGT_BATCH_QUEUE** and **RGT_PROJECT_ID** at launch)
2. **batch_queue** and **project_id** from *<Path_to_tests>/<app-name>/<test-name>/Scripts/rgt_test_input.ini*
3. A big hammer to override all test-specific settings: environment variables **RGT_SUBMIT_QUEUE** and **RGT_SUBMIT_ACCT**


.. understanding_output:

Finding Test Output
-------------------

This section details where all output files can be found once a harness run completes.
There are 4 directories referenced in this section:

- **$BUILD_DIR** - the build directory, equal to **$RGT_PATH_TO_SSPACE/<app>/<test>/<test-id>/build_directory**
- **$WORK_DIR** - equal to **$RGT_PATH_TO_SSPACE/<app>/<test>/<test-id>/workdir**
- **$RESULTS_DIR** - the directory used to launch the job and store relevant output, equal to **<Path_to_tests>/<app>/<test>/Run_Archive/<test-id>**
- **$STATUS_DIR** - the directory used to store harness status files, equal to **<Path_to_tests>/<app>/<test>/Status/<test-id>**

**$RESULTS_DIR** is the best starting point, as it contains symbolic links to the other 3 directories.

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

The OTH also produces log files throughout the run using the Python ``logging`` module, containing messages from the harness with data useful for debugging failed tests.
These log files default to the Python logging level of INFO, but will be changed to DEBUG if the ``--loglevel=DEBUG`` flag is provided on the command-line.
The table below lists the available log files and what scope messages in each file is from, in relative chronological order.

.. list-table:: Harness-generated log files
   :widths: 50 25 80
   :header-rows: 1

   * - Directory
     - Logfile name
     - Description
   * - **<launch_directory>**
     - ``main.log``
     - The highest-level execution information. For example, "Completed reading the harness input file." This scope ends when the ``othctl run`` command returns.
   * - **<launch_directory>/harness_log_files.<timestamp>**
     - ``libraries.regression_test.<timestamp>.txt``
     - High-level logging messages while preparing tests. For example, "Application Hello, World! has completed launching." This scope ends when the ``othctl run`` command returns.
   * - **<launch_directory>/harness_log_files.<timestamp>/<app>**
     - ``<app>__<test>.logfile.txt``
     - A brief scope between the regression_test log-file and the log files located inside the test's results directory. This scope ends when the ``othctl run`` command returns.
   * - **${RESULTS_DIR}/LogFiles**
     - application_logfile.txt
     - The majority of log messages generated while building, submitting, running, and checking a test.
   * - **${RESULTS_DIR}/LogFiles**
     - status_logfile.txt
     - Log messages generated at various checkpoints during the lifetime of a test such as ``build_end`` ``binary_execute_start`` and ``check_end``.

