#!/usr/bin/env python
"""A script with command-line argument parsing and logging setup."""

import logging
import sys

import docopt

__doc__: str = """
Usage:
    script.py [--debug | --verbose]

Options:
    --debug           Enable debug logging.
    --verbose         Enable verbose logging.
"""


def setup_logging(debug: bool, verbose: bool) -> None:
    """
    Set up logging based on the debug and verbose flags.

    Args:
        debug (bool): Enable debug logging if True.
        verbose (bool): Enable verbose logging if True.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


def main(args) -> int:
    """
    Run the main function with command-line arguments.

    Args:
        args (dict): Command-line arguments parsed by docopt.
    """
    debug: bool = bool(args["--debug"])
    verbose: bool = bool(args["--verbose"])

    setup_logging(debug, verbose)
    return 0


if __name__ == "__main__":
    cli_arguments: dict = docopt.docopt(__doc__, options_first=True, version="0.0.1")
    sys.exit(main(cli_arguments))
