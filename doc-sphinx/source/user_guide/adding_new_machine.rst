.. _section_new_machine:

====================
Adding a New Machine
====================

A system is defined either through a Python ConfigParser-formatted configuration file and/or through environment variables.
The following section assumes that you will create a machine configuration file with at least some subset of the configurations, though the configuration file is not mandatory and may be disabled with **OTHCTL_USE_CONFIG_FILE=0**.

The following steps can be used to add support for a new system:

1. Create a machine configuration file (e.g. *lyra.ini*, placed in *$OLCF_HARNESS_DIR/configs/lyra.ini*).
2. Create the location of the repository that will hold all applications and tests for that particular machine
    - This can be in a remote Git repository, but must also be a directory on the file system (which is then used as **Path_to_tests** in the input file)

Creating a new machine configuration file is discussed below.
The creation of new tests is discussed in :ref:`section_new_test`.


Just Let Me Run Now
-------------------

You don't need a configuration file, it just makes life easier.
This section supposes you don't care, and you just want to run without having to make the configuration file.
All settings for the OTH can be done by environment variables.
Below is an example of a minimal (no Git) set of environment variables to start running immediately:

.. code-block:: text

    export OTHCTL_MACHINE=frontier
    export OTHCTL_SCHEDULER_TYPE=slurm
    export OTHCTL_BATCH_QUEUE=batch
    export OTHCTL_PROJECT_ID=mySlurmAccount
    export OTHCTL_PATH_TO_TESTS=/my/path/to/apptests
    export OTHCTL_PATH_TO_SSPACE=/my/path/to/sspace
    export OTHCTL_USE_CONFIG_FILE=0

    othctl run -i rgt.inp --mode start stop


See :ref:`env_vars_config` for a complete listing of available environment variables.


Create a Basic Machine Configuration
------------------------------------

All settings in the *machine.ini* file are directly used to set environment variables that can be used throughout the test.
For example, **path_to_sspace** is used to set **OTHCTL_PATH_TO_SSPACE**, which could be used in a job script.
The settings in the *machine.ini* file do not override existing environment variables.
If **OTHCTL_PATH_TO_SSPACE** is set by the user, then the *machine.ini* file will not override it.
See :ref:`env_vars_config` for a complete listing of available environment variables.

As of v4.0.0 of the OLCF Test Harness, the *machine.ini* has no required section names, but the user is free to name sections however they see fit.
In the example below, we use the legacy name, **MachineDetails**, but we could name the section whatever we choose.
The below config is a common example of settings including scheduler, Git, and path configurations.

.. code-block:: text

    [MachineDetails]
    # Required variables ###################
    machine_name = frontier
    machine_type = linux_x86_64  # does not imply x86 CPU, just a Unix-based OS
    # options: slurm, pbs, lsf, k8s, openshift
    scheduler_type = slurm
    # note, a local scheduler (e.g., ./<batchscript>) can be enabled by setting on a per-test basis in ``rgt_test_input.{ini,yaml}``
    # End required #########################

    # This section is only required when ``--mode checkout`` is used
    [ORNLGitLab]
    # Git is currently the only supported type of remote repository
    # OTH looks for:
    #   $git_ssh_server_url:$git_server_application_parent_dir/$git_machine_name/<application>
    type_of_repository = git
    # Protocol to use when cloning
    git_data_transfer_protocol = ssh
    # Sub-project/group hierarchy in the Git repository
    git_app_parent_dir = your-project/applications
    # Name of the machine to look for in Git.
    git_machine_name = frontier
    git_ssh_server_url = gitlab@gitlab.com
    git_https_server_url = https://www.gitlab.com

    [DefaultPaths]
    # A path used for build and scratch space used while running. This will usually be overridden at run-time
    path_to_sspace = /default/path/to/scratch/space
    # A path to where application repositories are cloned (can be overridden by 'Path_to_tests' in ``othctl run`` input file)
    path_to_tests = /some/path/to/my/applications
    # A string that can be used to identify tests run for a specific purpose (ie: 'summit_tshot_cuda11'). This will usually be overridden at run-time
    system_log_tag = frontier_test
    # Default queue/partition to submit jobs to
    batch_queue = batch
    # Default project to submit jobs under
    project_id = <default account for scheduler>
    # Any required flags to job scheduler (ie, ``-M clustername`` in Slurm)
    submit_args =


.. note::

    These variables can all be overridden by setting **OTHCTL_<VARIABLE_NAME>** in the environment prior to launching.
    However, that usage of **batch_queue**/**OTHCTL_BATCH_QUEUE** and **project_id**/**OTHCTL_PROJECT_ID** may be ineffective.
    For handling these two specific variables, please see :ref:`runtime_configurable_parameters`.
