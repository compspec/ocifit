#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2025, Vanessa Sochat"
__license__ = "MIT"

import argparse
import os
import sys

import ocifit
import ocifit.defaults as defaults
from ocifit.logger import setup_logger


def get_parser():
    parser = argparse.ArgumentParser(
        description="OCI Fit",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )
    description = "actions for ocifit"
    subparsers = parser.add_subparsers(
        help="actions",
        title="actions",
        description=description,
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", description="show software version")
    compat = subparsers.add_parser(
        "compat",
        description="Generate a compatibility spec for your Dockerfile or container URI.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    for command in [compat]:
        command.add_argument(
            "image",
            help="Container URI to parse",
        )
        command.add_argument(
            "-o",
            "--outfile",
            help="Output manifest file, over-rides outdir",
            dest="outfile",
        )
        command.add_argument(
            "--outdir",
            help="Root to write output structure, not used if not set.",
        )
        command.add_argument(
            "--save",
            help="Save image to cache (requires --uri).",
            default=False,
            action="store_true",
        )
        command.add_argument(
            "--uri",
            help="Unique resource identifier of relevant image.",
        )
        command.add_argument(
            "--model-name",
            help="Gemini or Gemma model name to use",
            default=defaults.model_name,
        )
        command.add_argument(
            "--parser",
            help="Select parser type to use.",
            default="software",
            choices=["software", "nfd"],
        )
        command.add_argument(
            "--pattern",
            help="Pattern to filter paths to, if --path not provided",
            default="mpi",
        )
        command.add_argument(
            "--path",
            help="Absolute path or basename of executable to run ldd on",
            action="append",
            default=None,
        )
        command.add_argument(
            "--no-cache",
            dest="no_cache",
            help="Don't use the cache",
            default=False,
            action="store_true",
        )
    return parser


def run():
    """
    Entrypoint to generating container guts
    """
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """
        version = ocifit.__version__

        print("\nOCI Fit Client v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(ocifit.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action for action in parser._actions if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    # Does the user want a shell?
    if args.command == "manifest":
        from .manifest import main
    elif args.command == "diff":
        from .diff import main
    elif args.command == "similar":
        from .similar import main
    elif args.command == "compat":
        from .compat import main

    # Pass on to the correct parser
    return_code = 0
    main(args=args, parser=parser, extra=extra, subparser=helper)
    sys.exit(return_code)

    help(return_code)


if __name__ == "__main__":
    run()
