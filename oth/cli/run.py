import argparse as ap
import sys

from oth.libraries import input_files, regression_test
from oth.libraries.config_file import rgt_config_file
from oth.libraries.output_hub import OutputHub


def run(args: ap.Namespace) -> None:
    oh: OutputHub = OutputHub(__name__)

    oh.log_info("reading the harness input file")
    input_file = input_files.rgt_input_file(
        inputfilename=args.input_file,
        runmodecmd=args.mode,
        app_filter=args.app_filter,
        test_filter=args.test_filter,
        logger=oh,
    )
    oh.log_info("completed reading the harness input file")

    if len(input_file.get_tests()) == 0:
        oh.print("No tests were found in the input file. Aborting!")
        sys.exit(0)

    oh.log_info("reading the harness config file")
    try:
        config = rgt_config_file(configfilename=args.config_file, logger=oh)
    except NameError as e:
        oh.log_critical(str(e))
        sys.exit(1)
    oh.log_info("completed reading the harness config file")

    rgt = regression_test.Harness(
        config,
        input_file,
        args.log_level,
        args.output,
        args.separate_build_stdio,
        args.reuse_first_build,
        args.reuse_build_from_id,
        shuffle=args.shuffle,
    )
    oh.log_info(f"created an instance of the harness: {rgt}")

    oh.log_info("running the harness tasks")
    rgt.run_me()
    oh.log_info("completed running the harness tasks")
