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

On Spock and Crusher
""""""""""""""""""""

The code is already installed in: */sw/acceptance/olcf-test-harness*

Setup the environment:

.. code-block:: bash

    export OLCF_HARNESS_DIR=/sw/acceptance/olcf-test-harness
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    # For Spock:
    export OLCF_HARNESS_MACHINE=spock
    # For Crusher:
    export OLCF_HARNESS_MACHINE=crusher

Option 2: Using your own copy of the harness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone the repo on the target system:

.. code-block:: bash

    git clone https://github.com/olcf/olcf-test-harness.git

Setup the environment:

.. code-block:: bash

    cd olcf-test-harness
    export OLCF_HARNESS_DIR=`pwd`
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    export OLCF_HARNESS_MACHINE=<machine>

.. note::
    You must have the <machine>.ini file in the *configs* directory of your
    harness repository for your specified machine. On Spock, Crusher,  and
    Lyra, this is provided for you in the centralized harness. An
    example_machine.ini file is provided in the *configs* directory.


Logging harness events to InfluxDB
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OTH can log the status of tests to an InfluxDB server by setting the
appropriate values of *RGT_INFLUX_URI* and *RGT_INFLUX_TOKEN*, to match
the target InfluxDB server. The harness
events (listed below) are logged to the InfluxDB server, where they can
be watched in real time by a data visualization tool, such as Grafana.


.. list-table:: OTH Test Status Events
   :widths: 25 140
   :header-rows: 1

   * - Status
     - Description
   * - logging_start
     - Harness is starting up and creating log files.
   * - build_start
     - The build process has started.
   * - build_end
     - The build process finished.
   * - submit_start
     - The job submission process has started.
   * - submit_end
     - The job submission process has finished.
   * - job_queued
     - The job is queued in the scheduler.
   * - binary_execute_start
     - The application has started. Triggered by call to log_binary_execution_time.py --mode start inside the job script.
   * - binary_execute_end
     - The application has ended. Triggered by call to log_binary_execution_time.py --mode final inside the job script.
   * - check_start
     - The check process has started. Triggered by call to check_executable_driver.py inside the job script.
   * - check_end
     - The check process has ended.


Logging test metrics to InfluxDB
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In a similar manner to logging harness events to InfluxDB, you can send
performance metrics from your test to InfluxDB, where they can be visualized
by a data visualization tool, such as Grafana. For details on how to make a
test capable of logging metrics to InfluxDB, see
:ref:`Modifying a Test to Log Metrics to InfluxDB`. Given a compatible test that reports
application metrics, adding *RGT_INFLUX_TOKEN* and *RGT_INFLUX_URI* to the
environment enables InfluxDB test metric logging.


Launching the OTH
-----------------

Create a directory for your run - this is where you will place input files and
retrieve a copy of OTH log files. No computation will be done here:

.. code-block:: bash

    mkdir lyra_testshot
    cd lyra_testshot

In this run directory, prepare an input file of tests (e.g., *rgt.input.lyra*).
In the file, set ``Path_to_tests`` to the location where you would like application
source and run files to be kept (note that the directory provided must be an
existing directory on a file system visible to the current machine). Next, provide
one or more tests to run in the format ``Test = <app-name> <test-name>``. In this
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
default is set by <machine>.ini but this lets you change the default):

.. code-block:: bash

    export RGT_PATH_TO_SSPACE=<some path in the file system>/Scratch


The latest version of the harness supports command line tasks as well as input
file tasks. If no tasks are provided in the input file, it will use the command
line mode. To launch via the CLI, use a command like the following:

.. code-block:: bash

    runtests.py --inputfile rgt.input.lyra --mode checkout
    runtests.py --inputfile rgt.input.lyra --mode start
    runtests.py --inputfile rgt.input.lyra --mode checkout start stop


When using the checkout mode, the application source repository will be cloned
to the *<Path_to_tests>/<app-name>* directory for all the tests, but no tests
will be run.


After using the start mode, results of the most recent test run can be found in
*<Path_to_tests>/<app-name>/<test-name>/Run_Archive/latest*.

The build and run directories can be found in
*<RGT_PATH_TO_SSPACE>/<app-name>/<test-name>/<test-id>/Run_Archive*,
and are sym-linked inside the *Run_Archive/<test-id>* directory in *Path_to_tests*.
