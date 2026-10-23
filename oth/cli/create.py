import argparse as ap
import os
import sys
from pathlib import Path

from oth.libraries.output_hub import OutputHub
from oth.schedulers.slurm import Slurm

EXAMPLE_BUILD_SCRIPT: str = """\
#!/usr/bin/bash
set -o pipefail

### This is an example build script for the application.

source Common_Scripts/setup_env.sh

mpicxx hello_world.cpp -o hello_world

exit 0
"""

EXAMPLE_ENV_SCRIPT: str = """\
#!/usr/bin/bash
set -o pipefail

### This script configures the environment for building and running the application.

module reset
# Assumes MPI is loaded by default
module list
"""

EXAMPLE_CHECK_SCRIPT: str = """\
#!/usr/bin/bash
set -o pipefail

### This script checks the job output to see if it ran correctly

if [ "$(grep "Hello from rank" output.txt | wc -l)" == "${1:-1}" ]; then
    echo "Found expected number of processes: ${1:-1}"
    exit 0
else
    echo "Did not find expected number of processes (${1:-1}), found $(grep "Hello from rank" output.txt | wc -l). Output:"
    cat output.txt
    exit 1
fi
"""

EXAMPLE_SLURM_TEMPLATE: str = """\
#!/usr/bin/bash
#SBATCH -t {{walltime}}
#SBATCH -N {{nodes}}
#SBATCH -n {{(nodes | int)*(ppn | int)}}
#SBATCH --job-name={{job_name}}

# Define environment variables needed
export SCRIPTS_DIR="{{scripts_dir}}"
export WORK_DIR="{{working_dir}}"
export RESULTS_DIR="{{results_dir}}"
export HARNESS_ID="{{harness_id}}"
export BUILD_DIR="{{build_dir}}"

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
ldd ${BUILD_DIR}/hello_world > ldd.txt

# Run the executable.
log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode start

srun -N {{nodes}} -n {{(nodes | int)*(ppn | int)}} --ntasks-per-node={{ppn}} ${BUILD_DIR}/hello_world | tee output.txt

log_binary_execution_time.py --scriptsdir $SCRIPTS_DIR --uniqueid $HARNESS_ID --mode final

# Ensure we return to the starting directory.
cd $SCRIPTS_DIR

# Copy the output back to the $RESULTS_DIR, if desired
cp $WORK_DIR/* $RESULTS_DIR

# Check the final results.
check_executable_driver.py -p $RESULTS_DIR -i $HARNESS_ID

# Uncomment this if you want the test to resubmit
#test_harness_driver.py -r {{max_submissions}} ;;
"""

EXAMPLE_TEST_INPUT: str = """
variables:
    nnodes: 1
    ppn: 1

replacements:
    # Required replacements
    job_name: 'run_n{nnodes}_{ppn}ppn'
    nodes: '{nnodes}'
    walltime: 1
    batch_filename: run.sh
    build_cmd: ./build.sh
    check_cmd: './check.sh $(({nnodes}*{ppn}))'

    # User-defined replacements
    ppn: 1
"""

EXAMPLE_APPLICATION_SCRIPT: str = """\
#include <iostream>
#include <mpi.h>

int main(int argc, char **argv) {
  int rank, numprocs;
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
  std::cout << "Hello from rank " << rank << " of " << numprocs << std::endl;
  MPI_Finalize();
  return 0;
}
"""


def create(args: ap.Namespace) -> None:
    oh: OutputHub = OutputHub(__name__)

    if "RGT_PATH_TO_TESTS" in os.environ:
        path_to_tests: Path = Path(str(os.getenv("RGT_PATH_TO_TESTS"))).absolute()
    else:
        oh.log_critical("RGT_PATH_TO_TESTS is not set")
        sys.exit(1)

    path_to_application: Path = path_to_tests.joinpath(args.application)
    path_to_test: Path = path_to_application.joinpath(args.test)

    oh.print(
        f"Creating test '{args.test}' for application '{args.application}' at '{path_to_test}'."
    )

    if path_to_application.exists():
        oh.log_warning(
            f"application '{args.application}' already exists; not creating application"
        )
    else:
        (path_to_application / "Source/Common_Scripts").mkdir(parents=True)

        # build script
        with open(path_to_application / "Source/build.sh", "w") as f:
            f.write(EXAMPLE_BUILD_SCRIPT)
        (path_to_application / "Source/build.sh").chmod(0o755)

        # dummy C++ code
        with open(path_to_application / "Source/hello_world.cpp", "w") as f:
            f.write(EXAMPLE_APPLICATION_SCRIPT)

        # env script
        with open(path_to_application / "Source/Common_Scripts/setup_env.sh", "w") as f:
            f.write(EXAMPLE_ENV_SCRIPT)

    if path_to_test.exists():
        oh.log_critical(
            f"Test '{args.test}' for application '{args.application}' already exists"
        )
        sys.exit(1)
    else:
        (path_to_test / "Scripts").mkdir(parents=True)

        # test input
        with open(path_to_test / "Scripts/rgt_test_input.yaml", "w") as f:
            f.write(EXAMPLE_TEST_INPUT)

        # common logic
        app_path: Path = path_to_application / "Source/Common_Scripts"
        test_path: Path = path_to_test / "Scripts"
        if args.scheduler == "slurm":
            template_name: str = Slurm(oh, use_jinja2=True).batch_script_template_file
            template_content: str = EXAMPLE_SLURM_TEMPLATE

        # scheduler template
        if not (app_path / template_name).exists():
            with open(app_path / template_name, "w") as f:
                f.write(template_content)
        (test_path / template_name).symlink_to(
            "../../Source/Common_Scripts/" + template_name
        )

        # check script
        if not (app_path / "check.sh").exists():
            with open(app_path / "check.sh", "w") as f:
                f.write(EXAMPLE_CHECK_SCRIPT)
            (app_path / "check.sh").chmod(0o755)
        (test_path / "check.sh").symlink_to("../../Source/Common_Scripts/check.sh")
