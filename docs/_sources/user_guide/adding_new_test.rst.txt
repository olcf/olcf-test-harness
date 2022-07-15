============================
Adding a New Test to the OTH
============================

The OLCF Test Harness (OTH) requires a specific source code repository
structure for application tests. This document describes how to add an
application and associated tests for a specific system to the harness.

Application Source Code Repository Structure
--------------------------------------------

The top-level group in a GitLab group (or GitHub repo) contains
a sub-group for each target machine.

Repository URL
^^^^^^^^^^^^^^

Each application that can be tested on a given machine has a repository
within the machine's group.


Repository structure
^^^^^^^^^^^^^^^^^^^^

The application repository must be structured as shown below:

.. code-block::

    <application name>/<test name>/Scripts/
                                          /rgt_test_input.ini
                                          /<check script>
                                          /<report script>
                                          /<job script template>
    <application name>/Source/
                             /<build script>
                             /<other application source and build files>


First, each application test must have its own subdirectory. The test directory
has a mandatory *Scripts* subdirectory, which should contain the test input file
(see :ref:`application-test-input` below) and other required scripts (see
:ref:`required-application-test-scripts` below).

Second, the application's source code and required build script should reside
within the *Source* directory of the repository.

Example Repository
^^^^^^^^^^^^^^^^^^

For instance, let's assume we have a Git repository for an application
called *hello_mpi*.

To add a single node test and a two node test, we would create a separate
subdirectory for each test, including their required *Scripts* subdirectory:

.. code-block:: bash

    hello_mpi/c_n001/Scripts/
             /c_n002/Scripts/

Note that the test names are not required to follow any specific naming convention,
but you should avoid spaces in the names. 

.. _application-test-input:

Application Test Input
----------------------

Each test scripts directory should contain a test input file named
*rgt_test_input.ini*. The test input file contains information that is used by the
OTH to build, submit, and check the results of application tests. All the fields in
the ``[Replacements]`` section can be used in the job script template and will be
replaced when creating the batch script (see :ref:`job-script-template` section below).
The fields in the ``[EnvVars]`` section allow you to set environment variables that
your job will be able to use.

The following is a sample input for the single node test of the *hello_mpi*
application mentioned above:

.. code-block:: bash

    [Replacements]
    #-- This is a comment
    #-- The following variables are required
    job_name = hello_mpi_c
    batch_queue = batch
    walltime = 10
    project_id = my_project
    executable_path = hello
    batch_filename = run_hello_mpi_c.sh
    build_cmd = ./build_hello_mpi_c.sh
    check_cmd = ./check_hello_mpi_c.sh 
    report_cmd = ./report_hello_mpi_c.sh
    resubmit = 0
    # Use in conjunction with resubmit argument to limit total submissions/runs of a test (inclusive of initial run)
    # Set to 0 for indefinite resubmissions
    max_submissions = 3 

    
    #-- The following are user's defined and used for Key-Value replacements 
    nodes = 1
    total_processes = 16
    processes_per_node = 16
    
    [EnvVars]
    FOO = bar

.. _required-application-test-scripts:

Required Application Test Scripts
---------------------------------

The OTH requires each application test to provide a build script, a check
script, and a job script template. An optional report script may also be
provided. These scripts should be placed in the locations described above.
If the OTH cannot find the scripts specified in the test input, it will
fail to launch.

Build Script
^^^^^^^^^^^^

The build script can be a shell script, a Python script, or other executable
command. It is specified in the test input file as *build_cmd*, and the OTH
will execute the provided value as a subprocess. The build script should
return 0 on success, non-zero otherwise.

For *hello_mpi*, an example build script named *build_hello_mpi_c.sh* may
contain the following:

.. code-block:: bash

    #!/bin/bash -l
    
    module load gcc
    module load openmpi
    module list
    
    mkdir -p bin
    mpicc hello_mpi.c -o bin/hello

The first step of building the application will be executed from the directory
**$BUILD_DIR**, which will be a copy of *Source/*. This means the build script
should be written as if it were executed from *Source/*, regardless of where it
actually is. 

Correspondingly, the path to the build script given in *rgt_test_input.ini*
should be relative to the *Source/* directory. 

.. _job-script-template:

Job Script Template
^^^^^^^^^^^^^^^^^^^

The OTH will generate the batch job script from the job script template by
replacing keywords of the form ``__keyword__`` with the values specified in
the test input ``[Replacements]`` section.

The job script template must be named appropriately to match the specific
scheduler of the target machine. For SLURM systems, use *slurm.template.x* as
the name. For LSF systems, use *lsf.template.x*. An example SLURM template
script for the *hello_mpi* application follows:

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH -J __job_name__
    #SBATCH -N __nodes__
    #SBATCH -t __walltime__
    #SBATCH -A __project_id__
    #SBATCH -o __job_name__.o%j
    
    module load openmpi
    module list
    
    # Define environment variables needed
    EXECUTABLE="__executable_path__"
    SCRIPTS_DIR="__scripts_dir__"
    WORK_DIR="__working_dir__"
    RESULTS_DIR="__results_dir__"
    HARNESS_ID="__harness_id__"
    BUILD_DIR="__build_dir__"
    
    echo "Printing test directory environment variables:"
    env | fgrep RGT_APP_SOURCE_
    env | fgrep RGT_TEST_
    echo
    
    # Ensure we are in the starting directory
    cd $SCRIPTS_DIR
    
    # Make the working scratch space directory.
    if [ ! -e $WORK_DIR ]
    then
        mkdir -p $WORK_DIR
    fi
    
    # Change directory to the working directory.
    cd $WORK_DIR
    
    env &> job.environ
    scontrol show hostnames > job.nodes
    
    # Run the executable.
    log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode start
    
    #CMD="srun -n __total_processes__ -N __nodes__ $BUILD_DIR/bin/$EXECUTABLE"
    CMD="mpirun -n __total_processes__ --map-by node --hostfile job.nodes $BUILD_DIR/$EXECUTABLE"
    echo "$CMD"
    $CMD
    
    log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode final
    
    # Ensure we return to the starting directory.
    cd $SCRIPTS_DIR
    
    # Copy the output and results back to the $RESULTS_DIR
    cp -rf $WORK_DIR/* $RESULTS_DIR
    cp $BUILD_DIR/output_build.*.txt $RESULTS_DIR
    
    # Check the final results.
    check_executable_driver.py -p $RESULTS_DIR -i $HARNESS_ID
    
    # Resubmit if needed
    case __resubmit__ in
        0)
           echo "No resubmit";;
        1)
           test_harness_driver.py -r __max_submissions__ ;;
    esac

Using the job template above, the job will be submitted from the test *Scripts/*
directory and starts there. This is **$SCRIPT_DIR** in the job template. The
executable will then be run from **$WORK_DIR** directory, an entirely new directory. 

One can access or copy any files relative to the *Scripts/* directory using the
**$SCRIPT_DIR** environment variable. For example, if one stores a *CorrectResults*
directory for a test case, it can be be copied by adding the line

.. code-block:: bash

    cp -a ${SCRIPT_DIR}/../CorrectResults ${WORK_DIR}/

inside the job script.

The environment variable **$EXECUTABLE** is also populated based on
``executable_path`` entry in *rgt_test_input.ini* file. This is relative to the
**$WORK_DIR**, an entirely new directory created for every harness run. 

Since the actual executable may still be inside **$BUILD_DIR** from the previous
step, one would need to either copy it to **$WORK_DIR** or prepend the path in the
job script such as **$BUILD_DIR/$EXECUTABLE**.


Check Script
^^^^^^^^^^^^

The check script can be a shell script, Python script, or other executable
command.

Check scripts are used to verify that application tests ran as expected, and
thus use standardized return codes to inform the OTH on the test result. The
check script return value must be one of the following:

* ``0``: test succeeded
* ``1``: test failed
* ``5``: test completed correctly but failed a performance target

For *hello_mpi*, an example check script named *check_hello_mpi_c.sh* may
contain the following:

.. code-block:: bash

    #!/bin/bash
    echo "This is the check script for hello_mpi."
    echo
    echo -n "Working Directory: "; pwd
    echo
    echo "Test Result Files:"
    ls ./*
    echo
    exit 0

Notes on Where Things Are
^^^^^^^^^^^^^^^^^^^^^^^^^

It can be a little bit confusing to know where everything is and from which
directory they are executed. These are explained briefly in :doc:`overview`.
The following elaborates on this topic a bit more with some concrete examples.

In reading these notes, please keep in mind the application repository structure
describe above. 


Modifying a Test to Log Metrics to InfluxDB
-------------------------------------------

.. note::

    Logging to InfluxDB requires the *RGT_INFLUX_TOKEN* and *RGT_INFLUX_URI*
    to be set in the environment prior to harness launch.


The OTH is capable of logging event status and test performance metrics to
InfluxDB, where they can be viewed through a visualization tool such as
Grafana. Event status logging is done automatically, and doesn't require
any information from the test, aside from exit codes. However, to log test
performance metrics, the OTH needs to know how the application performed,
and what metrics to log.

Test performance logging is entirely controlled by a file named
*metrics.txt*. Each line in the file can have any of the following formats:

.. code-block:: bash

    # This is a comment line
    metric_name_1=value_1
    # Spaces in metric names are valid, but will be replaced by underscores when sending to influx
    metric name 2=value_2
    # Whitespace before and after the equals signs (and metric names) is okay. Python str.strip() is used
    metric_name_3 = value_3
    metric_name_4\t=\tvalue_4


If this file is present in the *<Path_to_tests>/Run_Archive/<test-id>*
directory when the check step completes, then the harness parses the
*metrics.txt* file and attempts to send the resulting metrics to
InfluxDB, along with 2 automatically calculated metrics,
build time and execution time.
