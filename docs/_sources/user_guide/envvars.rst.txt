=====================
Environment Variables
=====================

.. toctree::
   :maxdepth: 1

The OLCF Test Harness (OTH) is extremely flexible and can be configured in a number of ways.
There are a few command-line options, but many more environment variables.
In addition to the environment variables used to configure the OTH behavior, the OTH sets several useful environment variables during a test.
These environment variables are detailed below.

.. note::

    The ``<machine>.ini`` file can contain user-defined environment variables (such as ``mpi_version``, which sets ``RGT_MPI_VERSION`` in the environment).
    The only variables covered in this section are those ingested by the core harness code.

.. _env_vars_config:

Configuration Variables
=======================

There are many variables required to parameterize the OTH behavior.
All but ONE of these can have default values provided through the ``<machine>ini`` file,
which can be overridden by setting the environment variable prior to launching the harness.
These variables are all available for use in the build, run, and check stages of an OTH job.
These variables canl also be used as a replacement in the ``rgt_test_input.ini`` file by setting the variable name to ``<obtain_from_environment>``.
For example, ``machine_name = <obtain_from_environment>`` will fetch the value from ``RGT_MACHINE_NAME`` and use it while evaluating replacements.

.. note::

    If you re-run a test's job script outside of the harness, these variables will not all be set.
    Consider using replacements with ``<obtain_from_environment>`` in your test's ini file to capture the value of a variable,
    then explicitly set it using a replacement variable in the job script.

.. code-block::

    OLCF_HARNESS_MACHINE            Name of the system, used to find the machine ini file (default: 'master')
                                        This is the ONLY variable that CANNOT be set in ``<machine>.ini``,
                                        since it is needed to locate that file.
    RGT_MACHINE_NAME                Name of the system (can be different than OLCF_HARNESS_MACHINE).
                                        Used for status file and database logging.
    RGT_MACHINE_TYPE                System architecture: 'linux_x86_64' or 'ibm_power9'.
    RGT_SCHEDULER_TYPE              Name of the scheduler: 'slurm' or 'pbs' or 'lsf' or 'none'.
    RGT_JOBLAUNCHER_TYPE            Name of the job launcher: 'srun' or 'jsrun' or 'mpirun'.
    RGT_CPUS_PER_NODE               Number of CPUs per node.
    RGT_GPUS_PER_NODE               Number of GPUs per node.
    RGT_BATCH_QUEUE                 Which scheduler queue/partition to submit to.
                                    NOTE: is overridden by `batch_queue` in a test's ini file.
                                    To override a test's ini file, use `RGT_SUBMIT_QUEUE`
                                        For Slurm, this is enforced with `-p $RGT_BATCH_QUEUE`
                                        For LSF, this is enforced with `-q $RGT_BATCH_QUEUE`
                                        For PBS, this is enforced with `-q $RGT_BATCH_QUEUE`
    RGT_PROJECT_ID                  Which project ID to use when submitting to the scheduler.
                                    NOTE: is overridden by `proj_id` in a test's ini file.
                                        For Slurm and PBS, this is enforced with `-A $RGT_PROJECT_ID`
                                        For LSF, this is enforced with `-P $RGT_PROJECT_ID`
    RGT_SUBMIT_ARGS                 Provide additional flags to use when submitting to the scheduler
    RGT_SUBMIT_QUEUE                The highest-precedence specification of which scheduler queue/partition to submit to.
    RGT_SUBMIT_ACCT                 The highest-precedence specification of which project ID to submit to.
    RGT_NCCS_TEST_HARNESS_MODULE    Name of the OLCF Harness module

    RGT_TYPE_OF_REPOSITORY          Type of repository to access/clone the code. Must be 'git' currently.
    RGT_GIT_REPS_BRANCH             Branch name to clone a Git repo from. Optional, default behavior is to clone default branch.
    RGT_GIT_DATA_TRANSFER_PROTOCOL  Protocol to use when communicating with Git. 'https' or 'ssh'.
    RGT_GIT_MACHINE_NAME            Name of machine to use for navigating the Git repo.
                                        ie, a test system may use the same test as the corresponding production machine.
    RGT_GIT_SERVER_APPLICATION_PARENT_DIR 
                                    Path from the root of the parent repo to find the machine name collections.
    RGT_GIT_SSH_SERVER_URL          URL for the SSH Git client
    RGT_GIT_HTTPS_SERVER_URL        URL for the HTTPS Git client

    RGT_PATH_TO_SSPACE              Path to the harness scratch directory (for work & build spaces).
    RGT_SYSTEM_LOG_TAG              A tag describing the purpose of the test launch. Used in status file & database logging.


.. _env_vars_run:

Run-Time Variables
=====================

The OLCF Test Harness also SETS many variables while inside of a test.
These variables cannot be used by the ``rgt_test_input.ini`` file via ``<obtain_from_environment>``.
These variables are detailed below:

.. code-block::

    PATH_TO_RGT_PACKAGE         Path to the OLCF Test Harness code.
    RGT_APP_SOURCE_DIR          Path to the 'Source' directory of the current application.
    RGT_TEST_BUILD_DIR          Path to the build directory of the currently-running test.
    RGT_TEST_RUNARCHIVE_DIR     Path to the run archive directory of the currently-running test.
    RGT_TEST_SOURCE_DIR         Path to the source overlay directory of the currently-running test.
    RGT_TEST_SCRIPTS_DIR        Path to the scripts directory of the currently-running test.
    RGT_TEST_STATUS_DIR         Path to the status directory of the currently-running test.
    RGT_TEST_WORK_DIR           Path to the work (scratch) directory of the currently-running test.


.. _env_vars_ext:

Extension-specific Variables
============================

With the addition of several extensions to the OTH, there are a few more environment variables that configure extension behavior.
These are grouped below by extension. The general naming convention is ``RGT_<extension>_<option>``.

.. code-block::

    RGT_INFLUXDB_DISABLE        When set to '1', explicitly disables InfluxDB logging for the run tests.
                                    Creates a `.disable_influxdb` dot-file in the Run_Archive/<test_id> directory
                                    to prevent any future logging for this test ID.
    RGT_INFLUXDB_URI            URL's to one or more InfluxDB server, separated by semi-colons. This may either be of format:
                                    https://my.influxdb.server:<port>/api/v2/write?org=myorg&bucket=mybucket
                                    OR
                                    https://my.influxdb.server:<port>
                                    If the latter, you must provide RGT_INFLUXDB_BUCKET and RGT_INFLUXDB_ORG.
                                    Otherwise, the OTH can automatically detect your settings.
                                    Only org, bucket, and precision are supported.
    RGT_INFLUXDB_TOKEN          Authentication tokens for each provided InfluxDB server. Separate by semi-colons if >1.
    RGT_INFLUXDB_BUCKET         The data bucket to log to in InfluxDB.
                                    If >1 InfluxDB instance, use URL encoding to specify the bucket if not the same.
    RGT_INFLUXDB_ORG            The organization to log as in InfluxDB.
                                    If >1 InfluxDB instance, use URL encoding to specify the org if not the same.
    RGT_INFLUXDB_PRECISION      The precision to log with in InfluxDB. Only `ms` (milliseconds) or `ns` (nanoseconds) are supported.
                                    Default: 'ns'
                                    If >1 InfluxDB instance, use URL encoding to specify the precision if not the same.
    RGT_INFLUXDB_DRY_RUN        Print the database logging string, but do not send it to the database.

    RGT_NODE_LOCATION_FILE      (Node health only) Provides metadata about the physical location of a node to the node health
                                database logging extension. Set to "none" (not case-sensitive) to disable.

