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

source Common_Scripts/env.sh

exit 0
"""

EXAMPLE_ENV_SCRIPT: str = """\
#!/usr/bin/bash
set -o pipefail

### This script configures the environment for building and running the application.

module reset
module list

exit 0
"""

EXAMPLE_CHECK_SCRIPT: str = """\
#!/usr/bin/bash
set -o pipefail

### This script checks the job output to see if it ran correctly

if grep output.* "Hello, world!"; then


"""

EXAMPLE_SLURM_TEMPLATE: str = """\
#!/usr/bin/bash
#SBATCH -N{{ nodes }}
#SBTACH -n{{ nodes | int * ppn | int }}

### This is a slurm submit script for the application.

export BUILD_DIR="{{ build_dir }}"

source ${BUILD_DIR}/Common_Scripts/env.sh

srun -N{{ nodes }} -n {{ nodes | int * ppn | int }} python3 hello_world.py

"""

EXAMPLE_TEST_INPUT: str = """
nodes: 1
ppn: 1
"""

EXAMPLE_APPLICATION_SCRIPT: str = """\
#!/usr/bin/env python3

print("Hello, world!")

exit(0)
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
        oh.log_info(f"Application '{args.application}' already exists")
    else:
        (path_to_application / "Source/Common_Scripts").mkdir(parents=True)

        # build script
        with open(path_to_application / "Source/build.sh", "w") as f:
            f.write(EXAMPLE_BUILD_SCRIPT)

        # env script
        with open(path_to_application / "Source/Common_Scripts/env.sh", "w") as f:
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
            with open(app_path / "check.sh") as f:
                f.write(EXAMPLE_CHECK_SCRIPT)
        (test_path / "check.sh").symlink_to("../../Source/Common_Scripts/check.sh")
