# OLCF Test Harness (OTH)

This repository hosts the source code and documentation of the OLCF Test Harness (OTH).
The full OTH documentation can be found at [](https://olcf.github.io/olcf-test-harness),
or can be viewed locally by cloning this repository and launching a Python HTTP server in the `docs` directory:

```
git clone https://github.com/olcf/olcf-test-harness
cd olcf-test-harness/docs
python3 -m http.server 8080
# Then, navigate to localhost:8080 in a browser on your computer
```

Sample tests can be found at https://github.com/olcf/olcf-test-harness-examples.

## Quick-Start

### Obtaining the OTH source code

To obtain the OTH source code, run the following commands on the machine you are testing:
```
git clone git@github.com:olcf/olcf-test-harness.git  
cd olcf-test-harness
export OLCF_HARNESS_DIR=`pwd`  
module use $OLCF_HARNESS_DIR/modulefiles  
module load olcf_harness
export OLCF_HARNESS_MACHINE=<machine>
```

### Configuring the machine settings

If you are using an OLCF machine, there are machine configuration files provided in `${OLCF_HARNESS_DIR}/configs/olcf_examples`.
Please copy these into the `configs` directory.
If you are using a machine which is not provided in the `${OLCF_HARNESS_DIR}/configs/olcf_examples` directory, please see the [OTH User Guide](https://olcf.github.io/olcf-test-harness).

### Specifying tests to run

Once the `${OLCF_HARNESS_MACHINE}.ini` file is placed in the `${OLCF_HARNESS_DIR}/configs` directory, construct an input file to provide the OTH at run-time.
In this example, we will name it `rgt.inp`, but the name is not important, as long as you specify the correct name with the `-i` command-line flag.

First, clone the OLCF Test Harness examples:
```
mkdir -p /home/auser/oth/applications
git clone https://github.com/olcf/olcf-test-harness-examples.git /home/auser/oth/applications/olcf-test-harness-examples
```

rgt.inp:
```
# Within the Path_to_tests directory, you will place application repositories
# Inside each application is one or more tests that can be called
# In this case, the OTH examples are nested deeply to support >1 machine,
# so we have to specify the Frontier applications directory
Path_to_tests = /home/auser/oth/applications/olcf-test-harness-examples/frontier

# Syntax for defining a test to run:
# Test = <appname> <testname>
# This test is in the olcf-test-harness-examples repo for Frontier:
Test = lammps test_1node_4mil_reax
# Multiple tests may be defined by copying the above line and changing the test name
```

### Launching a test

To launch one of the examples from the [OTH Examples Repo](https://github.com/olcf/olcf-test-harness-examples) on Frontier:

```
# Optional: replace with your own instance of the OTH
export OLCF_HARNESS_DIR="/sw/acceptance/olcf-test-harness"
module use $OLCF_HARNESS_DIR/modulefiles
module load olcf_harness
export OLCF_HARNESS_MACHINE="frontier"
# Set this to an account that you have permission to submit to:
export RGT_SUBMIT_ACCT="YOURACCOUNT123"
# Launch the test!
runtests -i rgt.inp --mode start stop
```

At the end of the output on your screen, you should see a a few lines like the following:
```
Path to Source: /home/auser/oth/applications/olcf-test-harness-examples/frontier/lammps/Source
Path to Build Dir: /<your RGT_PATH_TO_SSPACE>/lammps/test_1node_4mil_reax/1695761632.2935946/build_directory
Submitting job from SLURM class using batchfilename run.sh
sbatch  -p batch  -A <your RGT_SUBMIT_ACCT> run.sh
SLURM jobID =  <some schedulerJob ID>
build exit value = 0
submit exit value = 0
Skipped 0, launched 1.
```

When you see `submit exit value = 0`, you know your job was successfully launched.

### Checking Test Results

To find the results of the test, you may go to `<your Path_to_tests>/<app>/<test>/Run_Archive/latest` (in this case, `/home/auser/oth/applications/olcf-test-harness-examples/frontier/lammps/test_1node_4mil_reax/Run_Archive/latest`).
This is the directory your job launched from, and it is the directory your job stdout/stderr will go to and any output files will be copied back to.
When the job completes, you should see all output files in this directory as well as an `output_check.txt`.
This file contains the output from your check script, which parses your output files to check the result of the test for correctness and performance.

