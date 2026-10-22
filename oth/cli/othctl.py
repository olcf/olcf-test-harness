import argparse as ap
import sys
from typing import List

from oth import __version__
from oth.libraries.config_file import rgt_config_file
from oth.libraries.output_hub import OutputHub

from .create import create
from .run import run


def comma_separated_items(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> None:
    # argument parser
    arg_parser: ap.ArgumentParser = ap.ArgumentParser(
        prog="othctl",
        description="OLCF Test Harness CLI driver.",
        epilog="See https://github.com/olcf/olcf-test-harness.git",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )
    arg_parser.add_argument(
        "-l",
        "--log-level",
        default="WARNING",
        type=str,
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        required=False,
        help="logging level",
    )
    arg_parser.add_argument(
        "-c",
        "--config-file",
        default=rgt_config_file.get_default_config_file_name(),
        type=str,
        required=False,
        help="machine configuration file",
    )

    # No public type for arg_parser.add_subparsers
    sub_parsers = arg_parser.add_subparsers(
        dest="subcommand", help="harness action"
    )  # TODO: add required=True when Python >= 3.7

    # create subparser
    create_parser: ap.ArgumentParser = sub_parsers.add_parser(
        "create",
        help="create application test",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    create_parser.add_argument(
        "application",
        type=str,
        help="application to be tested",
    )
    create_parser.add_argument(
        "test",
        type=str,
        help="name of the application test",
    )
    create_parser.add_argument(
        "--scheduler",
        default="slurm",
        type=str,
        choices=("slurm",),
        required=False,
        help="test scheduler",
    )

    # run subparser
    run_parser: ap.ArgumentParser = sub_parsers.add_parser(
        "run",
        help="run test(s)",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    run_parser.add_argument(
        "-i",
        "--input-file",
        default="rgt.input",
        type=str,
        required=False,
        help="input file",
    )
    run_parser.add_argument(
        "--shuffle", action="store_true", help="shuffle the test launch order"
    )
    run_parser.add_argument(
        "-o",
        "--output",
        default="screen",
        type=str,
        choices=("screen", "logfile"),
        required=False,
        help="test output method",
    )
    run_parser.add_argument(
        "-m",
        "--mode",
        nargs="+",
        default=["use_input_file"],
        choices=("checkout", "start", "stop", "status"),
        required=False,
        help="perform checkout, start, stop, or status on application tests listed in the input file",
    )
    run_parser.add_argument(
        "-sb",
        "--separate-build-stdio",
        action="store_true",
        required=False,
        help="separate build output into build_out.stderr.txt and build_out.stdout.txt",
    )
    run_parser.add_argument(
        "--reuse-first-build",
        action="store_true",
        required=False,
        help="for re-submittable tests, re-use the first build in the chain",
    )
    run_parser.add_argument(
        "--reuse-build-from-id",
        action="store",
        default=None,
        type=str,
        required=False,
        help="re-use build from specified test ID",
    )
    run_parser.add_argument(
        "--app-filter",
        default=[],
        type=comma_separated_items,
        required=False,
        help="comma-separated list of regular expressions or strings used to select specific applications from the provided input file",
    )
    run_parser.add_argument(
        "--test-filter",
        default=[],
        type=comma_separated_items,
        required=False,
        help="comma-separated list of regular expressions or strings used to select specific tests from the provided input file",
    )

    # parse args
    args: ap.Namespace = arg_parser.parse_args()

    # start harness
    oh: OutputHub = OutputHub(
        __name__,
        log_level=args.log_level,
        log_file="main.log",
        console_log_level=args.log_level,
        file_log_level=args.log_level,
    )
    oh.log_info("starting harness")
    oh.log_info(f"invoked with: '{' '.join(sys.argv[1:])}'")

    oh.log_debug(f"parsed command line options: {args}")
    oh.print(f"Using machine config: {args.config_file}")

    # branch to sub-command
    if args.subcommand == "create":
        create(args)
    elif args.subcommand == "run":
        run(args)
    else:
        # TODO: remove when >= Python 3.7 because we can add required=True to add_subparsers
        raise ValueError("you must specify a valid subcommand - options: (create, run)")

    oh.log_info("ending harness")


if __name__ == "__main__":
    main()
