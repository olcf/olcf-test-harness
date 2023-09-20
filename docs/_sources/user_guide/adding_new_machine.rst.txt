.. _section_new_machine:

===============================
Adding a New Machine to the OTH
===============================

The following steps can be used to add support for a new system:

1. Create a machine master configuration (e.g. *lyra.ini*, placed in *$OLCF_HARNESS_DIR/configs/lyra.ini*).
2. Create the location of the repository that will hold all applications and tests for that particular machine
    - This can be in a remote Git repository, or a directory on the file system

Creating a machine configuration file is discussed below.
The creation of tests is discussed in another section


Create a Basic Machine Configuration
------------------------------------

An example input file with detailed explanation is contained below.
All settings in the *machine.ini* file are used to set environment variables that can be used throughout the test.
For example, **gpus_per_node** is used to set **RGT_GPUS_PER_NODE**, which could be used in a job script.
These settings do not override existing environment variables.
If **RGT_SCHEDULER_TYPE** is set by the user, then the *machine.ini* file will not override it.

.. code-block:: text

    [MachineDetails]
    # Required:
    machine_name = crusher
    # Options: linux_x86_64 or ibm_power9
    machine_type = linux_x86_64
    # Options: slurm, pbs, lsf
    scheduler_type = slurm
    # Options: srun, aprun, jsrun, poe
    joblauncher_type = srun
    # Default queue/partition to submit jobs to
    batch_queue = batch
    # Overridden if project_id is set in the test's input file
    project_id = <default account for scheduler>
    # Any required flags to job scheduler (ie, ``-M clustername`` in Slurm)
    submit_args =
    nccs_test_harness_module = olcf_harness

    # Optional: specify some details about the machine
    # Each of these becomes an environment variable,
    # ie **RGT_CPUS_PER_NODE**, that can be used to template tests
    node_count = 1000
    cpus_per_node = 64
    sockets_per_node = 2
    gpus_per_node = 8

    # This section is only required when ``--mode checkout`` is used
    [RepoDetails]
    # Git is currently the only supported type of remote repository
    type_of_repository = git
    # Branch/tag to clone from remote repo
    git_reps_branch = master
    # Protocol to use when cloning
    git_data_transfer_protocol = ssh
    # Sub-project/group in the Git repository
    git_server_application_parent_dir = your-project/applications
    # Name of the machine to look for in Git.
    # OTH looks for:
    #   $git_ssh_server_url:$git_server_application_parent_dir/$git_machine_name/<application>
    git_machine_name = frontier
    # Git URLs:
    git_ssh_server_url = git@github.com
    git_https_server_url = https://www.github.com

    # This section provides defaults for testshot variables
    [TestshotDefaults]
    # The path used for building the application and scratch space used for running
    path_to_sspace = /default/path/to/scratch/space
    # A string that can be used to identify tests run for a specific purpose (ie: 'summit_tshot_cuda11')
    system_log_tag = some_default_log_tag


.. note::

    These variables can all be overridden by setting **RGT_<VARIABLE_NAME>** in the environment prior to launching.
    However, that usage of **batch_queue**/**RGT_BATCH_QUEUE** and **acct_id**/**RGT_ACCT_ID** may be incorrect.
    For handling these variables, please see :ref:`runtime_configurable_parameters`.
