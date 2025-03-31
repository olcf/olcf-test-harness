.. _section_new_test:

=================
Adding a New Test
=================

The OLCF Test Harness (OTH) requires a specific source code repository structure for application tests.
This document describes how to add an application and associated tests for a specific system to the harness.

Application Source Code Repository Structure
--------------------------------------------

The top-level group in a GitLab group (or GitHub repo) contains a sub-group for each target machine.

Repository URL
^^^^^^^^^^^^^^

Each application that can be run on a given machine should have a repository (or directory) within that machine's group.

.. _repository-structure:

Repository structure
^^^^^^^^^^^^^^^^^^^^

The application repository must be structured as shown below:

.. code-block::

    <application name>/<test name>/
                                   Scripts/
                                          /rgt_test_input.ini
                                          /<check script>
                                          /<report script>
                                          /<job script template>
                                   Source/ (optional)
                                         /<an alternate build script just for this test>
                                         /<a modified source file>
    <application name>/Source/
                             /<build script>
                             /<other application source and build files>
                             /<inputs, scripts shared by multiple tests>


First, each application test must have its own subdirectory.
The test directory has a mandatory *Scripts* subdirectory,
which should contain the test configuration file (see :ref:`application-test-input` below)
and other required scripts (see :ref:`required-application-test-scripts` below).
This directory contains templates and input files for the test -- a test must not modify files in this directory.

Second, the application's source code and required build script should reside within the *Source* directory of the repository.
Optionally, a test may add or override files from the application's *Source* tree by providing a *Source* directory within the test directory.
This directory will be overlayed over the application *Source* directory, so it may use the same internal directory structure.

Example Repository Structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For instance, let's assume we have a Git repository for an application called *hello_mpi*.

To add a single node test and a two node test, we would create a separate subdirectory for each test, including their required *Scripts* subdirectory:

.. code-block:: bash

    hello_mpi/c_n001/Scripts/
             /c_n002/Scripts/
             /Source

Note that the test names are not required to follow any specific naming convention, but you should avoid spaces and special characters in the names.
Since these tests are going to share the same source and build script, we are not going to create a *Source* subdirectory in either of the tests' subdirectories.

.. _application-test-input:

Application Test Input
----------------------

Each test's *Scripts* directory should contain a test input file named *rgt_test_input.ini*.
The test input file contains information that is used by the OTH to build, submit, and check the results of application tests.
The test input file follows the Python3 `configparser <https://docs.python.org/3/library/configparser.html>`_ file format.
The fields in the ``[DEFAULT]`` section can be used in the other sections of the configuration file and are useful for defining a variable that is re-used in multiple sections.
All the fields in the ``[Replacements]`` section can be used in the job script template and will be replaced when creating the batch script (see :ref:`job-script-template` section below).
Variables in ``[Replacements]`` cannot be referenced from ``[EnvVars]``.
The fields in the ``[EnvVars]`` section allow you to set environment variables that all stages of your test will be able to use.
See :ref:`best-practices` section for recommendations on when to use EnvVars vs Replacements.

.. note::

    Environment variables cannot be used in the definition of other environment variables -- ie, ``foo = $bar`` (See: `Issue 132 <https://github.com/olcf/olcf-test-harness/issues/132>`_).

The following is a sample input for the single node test of the *hello_mpi* application mentioned above:

.. code-block:: bash

    [DEFAULT]
    # This is a comment
    # The DEFAULT section defines variables that can be re-used in Replacements or EnvVars
    my_custom_variable = abc

    [Replacements]
    # The following variables are required
    job_name = hello_mpi_c
    walltime = 10
    # %(<variablename>)s is the notation to use the value of a previously-defined variable
    batch_filename = run_%(job_name)s.sh
    build_cmd = ./build_hello_mpi_c.sh
    check_cmd = ./check_hello_mpi_c.sh 
    report_cmd = ./report_hello_mpi_c.sh
    # The following variables are optional
    executable_path = hello
    resubmit = 0
    # Optional: used in conjunction with resubmit argument to limit total submissions/runs of a test (inclusive of initial run)
    # Set to 0 (or don't define) for indefinite resubmissions
    max_submissions = 3 

    
    # The following are user-defined and used for Key-Value replacements 
    # ie, nodes replaces __nodes__ in the job script template
    nodes = 1
    total_processes = 16
    processes_per_node = 16
    
    [EnvVars]
    FOO = bar

.. note::

    Setting a variable in the Replacements section to ``<obtain_from_environment>`` pulls in the value set by an environment variable.
    For example, if you set ``nodes = <obtain_from_environment>`` and set *RGT_NODES=4* in your environment, then *__nodes__* will be replaced with 4.

.. _required-application-test-scripts:

Required Application Test Scripts
---------------------------------

The OTH requires each application test to provide (1) a build script, (2) a job script template, (3) a check script, and (4) a reporting script.
These scripts should be placed in the locations described in :ref:`repository-structure`.
The build, check, and reporting scripts may also be set to Linux commands such as ``/usr/bin/echo``.
This is useful in cases where a script is not needed.
For example, a test that relies on standard system-provided tools can set the build script to ``/usr/bin/echo`` to remove the need to have an empty build script.
If the OTH cannot find the scripts specified by the test input file (*rgt_test_input.ini*), it will fail to launch.

Build Script
^^^^^^^^^^^^

The build script can be a shell script, a Python script, or other executable command.
It is specified in the test input file as *build_cmd*, and the OTH will execute the provided value as a subprocess.
The build script should return 0 on success, non-zero otherwise.

For *hello_mpi*, an example build script named *build_hello_mpi_c.sh* may
contain the following:

.. code-block:: bash

    #!/bin/bash -l
    
    module load gcc
    module load openmpi
    module list
    
    mkdir -p bin
    mpicc hello_mpi.c -o bin/hello

The build command be executed from the directory **$BUILD_DIR**, which is a copy of the contents of *Source/*.
This means the build script should be written as if it were executed from *Source/*, regardless of where it actually is. 

Likewise, the path to the build script given by *build_cmd* in *rgt_test_input.ini* should be relative to the *Source/* directory. 

.. _job-script-template:

Job Script Template
^^^^^^^^^^^^^^^^^^^

The OTH will generate the batch job script from the job script template by replacing keywords
of the form ``__keyword__`` with the values specified in the test input ``[Replacements]`` section.

The job script template must be named appropriately to match the specific scheduler of the target machine.
For SLURM systems, use *slurm.template.x* as the name.
For LSF systems, use *lsf.template.x*.
An example SLURM template script for the *hello_mpi* application follows:

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH -J __job_name__
    #SBATCH -N __nodes__
    #SBATCH -t __walltime__
    #SBATCH -o __job_name__.o%j
    
    # Define environment variables needed
    export EXECUTABLE="__executable_path__"
    export SCRIPTS_DIR="__scripts_dir__"
    export WORK_DIR="__working_dir__"
    export RESULTS_DIR="__results_dir__"
    export HARNESS_ID="__harness_id__"
    export BUILD_DIR="__build_dir__"
    
    echo "Printing test directory environment variables:"
    env | fgrep RGT_APP_SOURCE_
    env | fgrep RGT_TEST_
    echo

    # Placing the environment setup script in a shared location reduces code duplication
    # and ensures you have the same environment in building & running
    source $BUILD_DIR/Common_Scripts/setup_env.sh
    
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
    scontrol show hostnames &> job.nodes
    ldd $BUILD_DIR/bin/$EXECUTABLE &> ldd.log
    
    # Run the executable.
    log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode start
    
    set -x
    srun -n __total_processes__ -N __nodes__ $BUILD_DIR/bin/$EXECUTABLE
    set +x
    
    log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode final
    
    # Ensure we return to the starting directory.
    cd $SCRIPTS_DIR
    
    # Copy the output and results back to the $RESULTS_DIR
    # Depending on the size of files in $WORK_DIR, you may want to change this
    cp -rf $WORK_DIR/* $RESULTS_DIR
    cp $BUILD_DIR/output_build*.txt $RESULTS_DIR
    
    # Check the final results.
    check_executable_driver.py -p $RESULTS_DIR -i $HARNESS_ID
    
    # Resubmit if needed:
    # If you always want tests to resubmit if ``.kill_test`` is not present,
    # then remove the conditional around calling ``test_harness_driver.py``.
    case __resubmit__ in
        0)
           echo "No resubmit";;
        1)
           test_harness_driver.py -r __max_submissions__ ;;
    esac

Using the job template above, the job will be submitted from the test *Run_Archive/* directory and starts there.
This is **$RESULTS_DIR** in the job template.
The executable should then be run from **$WORK_DIR** directory, which is a scratch workspace derived from **$RGT_PATH_TO_SSPACE**.

One can access or copy any files relative to the *Scripts/* directory using the **$SCRIPT_DIR** environment variable.
For example, if one stores a *CorrectResults* directory at the same level as *Scripts* and *Run_Archive* for a test case,
it can be be copied by adding the line

.. code-block:: bash

    cp -a ${SCRIPT_DIR}/../CorrectResults ${WORK_DIR}/

inside the job script.

The environment variable **$EXECUTABLE** is also populated based on ``executable_path`` entry in *rgt_test_input.ini* file.
The executable may still be inside **$BUILD_DIR** from the previous step,
so one would need to either copy it to **$WORK_DIR** or provide the absolute path in the job script such as **$BUILD_DIR/$EXECUTABLE**.


Check Script
^^^^^^^^^^^^

The check script can be a shell script, Python script, or other executable command.
This must be an absolute path to a command (ie, ``/usr/bin/echo`` instead of ``echo``).

Check scripts are used to verify that application tests ran as expected, and thus use standardized return codes to inform the OTH on the test result.
Checking performance is optional but recommended for most tests.
The check script return value should be one of the following:

* ``0``: test succeeded
* ``1``: test failed
* ``2``: test completed but gave an incorrect answer
* ``5``: test completed correctly but failed a performance target

These exit codes have no built-in meaning in the OTH other than ``0`` is a successful test and non-zero is a failed test.
This set of test exit codes has been developed as a standard for test exit codes.
The check script is launched from **$RESULTS_DIR** and stdout/stderr is captured in **$RESULTS_DIR/output_check.txt**.

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


Report Script
^^^^^^^^^^^^^

Like the check script, the report script can be a shell script, Python script, or other executable command.
Report scripts are generally used to compute performance metrics from the run.
The exit code of report scripts is not checked by the OTH.
The report script is launched from **$RESULTS_DIR** and stdout/stderr is captured in **$RESULTS_DIR/output_report.txt**.

.. note::

    In many cases, the check script serves the function of both the check and report script.
    In that event, report scripts often just ``exit 0``.
    An alternative to a no-op bash script, you may use ``/usr/bin/echo`` on most Linux systems.


Example Test from the Ground Up
-------------------------------

This section details the thought process when developing a new test from the ground up.
In this section, we develop an application repository named ``mpi-tests``, which contains two "Hello, World!" MPI tests at different node counts.
This section ignores Git integration and focuses on developing tests on an empty file system.

At the completion of this section, we will have created a directory structure that looks like the following:

.. code-block::

    mpi-tests/
             /Source/
                    /build.sh
                    /Common_Scripts/
                                   /setup_env.sh
                                   /slurm.template.x
                                   /check_hello_world.sh
             /hello_world_n0001/Scripts/
                                       /rgt_test_input.ini
                                       /slurm.template.x -> ../../Source/Common_Scripts/slurm.template.x
                                       /check.sh -> ../../Source/Common_Scripts/check_hello_world.sh
                                       /report.sh -> ../../Source/Common_Scripts/check_hello_world.sh
             /hello_world_n0002/Scripts/
                                       /rgt_test_input.ini
                                       /slurm.template.x -> ../../Source/Common_Scripts/slurm.template.x
                                       /check.sh -> ../../Source/Common_Scripts/check_hello_world.sh
                                       /report.sh -> ../../Source/Common_Scripts/check_hello_world.sh


First, we create the top-level directory structure:

.. code-block:: bash

    # Create the application's directory
    mkdir mpi-tests
    cd mpi-tests/
    # Create the Source directory
    mkdir ./Source/
    # Create directories for two tests -- hello_world_n0001 and hello_world_n0002
    mkdir -p ./hello_world_n0001/Scripts ./hello_world_n0002/Scripts


Both of these tests will use the same source code (this is very common for many tests), so we can go ahead and create that:

.. code-block:: bash

    # from mpi-tests root:
    cd Source
    # create a directory to hold the source files
    mkdir test_src
    echo '#include <stdio.h>
    #include <mpi.h>
    int main(int argc, char **argv) {
      int rank, nranks;
      MPI_Init(&argc, &argv);
      MPI_Comm_rank(MPI_COMM_WORLD, &rank);
      MPI_Comm_size(MPI_COMM_WORLD, &nranks);
      printf("Hello, World from rank %d of %d!\n",rank,nranks);
      MPI_Finalize();
    }' > test_src/hello_world.c

The environment and build scripts will also be the same for both tests, so we can create a build script and a script to set up the environment:

.. code-block:: bash

    # from mpi-tests root:
    cd Source
    # create a directory to hold shared scripts -- "Common_Scripts" is a good name for it, but not required
    mkdir Common_Scripts
    # Create a basic environment file:
    echo '#!/bin/bash
    # As an example, we do a ``module reset`` here
    module reset
    # The OTH is loaded by a module, so we need to re-add this to our environment
    module use $OLCF_HARNESS_DIR/modulefiles
    module load olcf_harness
    # Now, we load a basic gcc and openmpi
    module load gcc
    module load openmpi
    ' > Common_Scripts/setup_env.sh
    # Now, create a build script in the top-level of the Source directory:
    echo '#!/bin/bash
    # Setup the environment:
    source ./Common_Scripts/setup_env.sh
    # Compile the code into a binary:
    cd test_src/
    mpicc -O1 -g -Wall -o hello_world hello_world.c
    ' > ./build.sh

Let's give some thought to how we want to construct these tests.
We'll start by working on the *rgt_test_input.ini* for the single-node *Hello, World!* test.
Below is a file that can be used for the *rgt_test_input.ini*, with discussion infused as comments.

.. code-block::

    [Replacements]
    job_name = hello_world_n0001
    walltime = 5
    nodes = 1
    # Since nodes is defined, defining the number of MPI ranks per node (processes per node) might be useful, too
    ppn = 2
    # %(<variable>)s uses the value held by that variable
    batch_filename = run_%(job_name)s.sh
    # executable is in ${BUILD_DIR}/test_src/hello_world
    executable_path = test_src/hello_world
    # build.sh is in Source/build.sh directory
    build_cmd = ./build.sh
    # check.sh is in ${SCRIPTS_DIR}/check.sh
    # I think that providing the total number of expected ranks to the check & report script might be useful in validating
    # This can always be removed later
    check_cmd = ./check.sh $((%(nodes)s*%(ppn)s))
    # report.sh is in ${SCRIPTS_DIR}/check.sh
    report_cmd = ./report.sh $((%(nodes)s*%(ppn)s))
    # Don't allow resubmissions currently
    resubmit = 0

    [EnvVars]
    # We don't currently have anything here

Notice that the only lines specific to this test are the *job_name* and *nodes*.
This should help us re-use as much code as possible.
Duplicate code will make tests difficult to maintain in the long run.

Next up is the Slurm template.
Moving from 1 to 2 nodes shouldn't change much about the job template, so let's try to develop a generic Slurm job template for *Hello, World!* programs:

.. code-block:: bash

    #!/bin/bash

    #SBATCH -J __job_name__
    #SBATCH -N __nodes__
    #SBATCH -t __walltime__
    
    # Define environment variables needed
    export EXECUTABLE="__executable_path__"
    export SCRIPTS_DIR="__scripts_dir__"
    export WORK_DIR="__working_dir__"
    export RESULTS_DIR="__results_dir__"
    export HARNESS_ID="__harness_id__"
    export BUILD_DIR="__build_dir__"
    
    echo "Printing test directory environment variables:"
    env | fgrep RGT_APP_SOURCE_
    env | fgrep RGT_TEST_
    echo
    
    # Placing the environment setup script in a shared location reduces code duplication
    # and ensures you have the same environment in building & running
    source $BUILD_DIR/Common_Scripts/setup_env.sh
    
    # Ensure we are in the starting directory
    cd $SCRIPTS_DIR
    
    # Make the working scratch space directory.
    if [ ! -e $WORK_DIR ]
    then
        mkdir -p $WORK_DIR
    fi
    
    # Change directory to the working directory.
    cd $WORK_DIR
    
    # These are very useful for debugging
    env &> job.environ
    scontrol show hostnames > job.nodes
    
    # Run the executable.
    log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode start
    
    # We use ${SLURM_NNODES} over __nodes__ for several reasons:
    #   1. for testing purposes, it's good to ensure that SLURM_NNODES is correct, since users will use that
    #   2. if you inadvertently set $RGT_SUBMIT_ARGS, using SLURM_NNODES will adapt to the size of the job
    set -x
    srun -N ${SLURM_NNODES} -n $((${SLURM_NNODES}*__ppn__)) --ntasks-per-node=__ppn__ $BUILD_DIR/$EXECUTABLE &> stdout.txt
    set +x
    
    log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode final
    
    # Ensure we return to the starting directory.
    cd $SCRIPTS_DIR
    
    # Copy the output and results back to the $RESULTS_DIR
    # Depending on the size of files in $WORK_DIR, you may want to change this
    cp -rf $WORK_DIR/* $RESULTS_DIR
    cp $BUILD_DIR/output_build*.txt $RESULTS_DIR
    
    # Check the final results -- this will call your command specified by `check_cmd`
    check_executable_driver.py -p $RESULTS_DIR -i $HARNESS_ID
    
    # Resubmit if needed:
    # If you always want tests to resubmit if ``.kill_test`` is not present,
    # then remove the conditional around calling ``test_harness_driver.py``.
    case __resubmit__ in
        0)
           echo "No resubmit";;
        1)
           test_harness_driver.py -r __max_submissions__ ;;
    esac


This job script will leave the output from the application in a file named ``stdout.txt``.
Let's write a check script that can validate the output from this file.
Recall that we provided the check script with the total number of tasks to expect as a command-line argument.

.. code-block:: bash

    #!/bin/bash

    expected_ranks=$1
    nranks=$(grep "Hello, World from rank" ${RESULTS_DIR}/stdout.txt | wc -l)
    if [ ! "${nranks}" == "${expected_ranks}" ]; then
        echo "Found ${nranks}, expected ${expected_ranks}"
        exit 1
    fi
    echo "Success! Found ${nranks}."
    exit 0


This check script is generic and should be able to be re-used in multiple tests, so let's put it in ``Source/Common_Scripts/check_hello_world.sh``.

The OTH also wants a report script, but there's not much to report here.
You can either create a script that immediately exits, or just link to your check script.
Here, we will just link to the check script.

The Slurm template and check and report scripts are required in the *Scripts* directory, so we use symbolic links to achieve this:

.. code-block:: bash

    # from mpi-tests
    cd hello_world_n0001/Scripts
    ln -s ../../Source/Common_Scripts/slurm.template.x .
    ln -s ../../Source/Common_Scripts/check_hello_world.sh ./check.sh
    ln -s ../../Source/Common_Scripts/check_hello_world.sh ./report.sh


To expand to a 2-node *Hello, World!* test, we can just copy the *Scripts* directory from the single-node test, then modify the *rgt_test_input.ini* to specify 2 nodes instead of 1.
Everything else is generalized, so no modification is needed.


.. _best-practices:

Best Practices
--------------

The OTH is very flexible and gives the user a lot of power.
That power can be diminished by poor test design.

With that in mind, this section presents some of the best practices in test design.

Use a centralized script to set up the environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

During a test run, the environment is independently set up during the build and run stages.
If the build script and job script each contain several ``module load`` statements, there is a chance that those can diverge.
To centralize where the environment is set to a single file, place a script containing the ``module`` commands and environment modifications in the build directory,
and ``source`` that script from the build and job scripts.
For the build script, this can be accomplished as simply ``source env.sh``, if the script is in the top level of the Source directory.
For the job script, this can be accomplished by ``source $BUILD_DIR/env.sh``, if the **$BUILD_DIR** environment variable is defined as in the :ref:`job-script-template` section above.

Define replacement variables instead of just EnvVars
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In **rgt_test_input.ini**, it is recommended that if you define an environment variable in the ``[EnvVars]`` section,
that you also define a replacement variable in ``[Replacements]`` that is used in the job script to re-define that environment variable.
This helps to create a re-usable job script.
If the harness is responsible for defining environment variables that are required for the job to run,
it can be very difficult to understand the resulting job script and to re-run the job script outside of the test harness if needed.
The following is recommended within the test input file:

.. code-block:: bash

    [DEFAULT]
    my_custom_var_default = abc

    [Replacements]
    ...
    my_custom_variable = %(my_custom_var_default)s
    ...
    
    [EnvVars]
    MY_ENV_VAR = %(my_custom_var_default)s

Then, within the job script template:

.. code-block:: bash

    export MY_ENV_VAR="__my_custom_variable__"

If the job script template requires an environment variable that is set by the harness (ie, **RGT_MACHINE_NAME**, **RGT_CPUS_PER_NODE**),
it may be best to define a replacement in the test input file that inherits the value of the environment variable using ``<obtain_from_environment>`` like so:

.. code-block:: bash

    # Internal name modification translates `machine_name` to `RGT_MACHINE_NAME`
    machine_name = <obtain_from_environment>

Then, in the job script, re-define the environment variable:

.. code-block:: bash

    export RGT_MACHINE_NAME="__machine_name__"

The same feature cannot be used in the build script, which leads to the next best practice, checking for expected environment variables.

Check for expected environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following on the last best practice, if the harness or environment script define any environment variables required in the build and job scripts,
the scripts should check that those are set and return an error if they are not.
This increases the reusability of the scripts outside of the test harness and aids debugging.

