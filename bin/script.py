#!/usr/bin/env python
"""CLI entrypoint for the p6 craps simulator."""

from __future__ import annotations

import logging
import sys
import time
from typing import Any, Optional

import docopt

USAGE = """p6-craps-py - Craps simulation CLI.

Usage:
    script.py [--debug | --verbose] [--config PATH] [--max-rolls N] [--no-clear] [--frame-delay SECONDS]
    script.py (-h | --help)
    script.py --version

Options:
    --debug                 Enable debug logging.
    --verbose               Enable verbose logging.
    --config PATH           Path to config file [default: config.json].
    --max-rolls N           Stop after at most N rolls (safety guard).
    --no-clear              Do not clear the terminal between frames.
    --frame-delay SECONDS   Sleep this many seconds between frames [default: 0].
    -h --help               Show this message.
    --version               Show version information.
"""

LOGGER = logging.getLogger(__name__)
DEFAULT_CONFIG_PATH = "config.json"
VERSION = "0.0.1"


def setup_logging(debug: bool, verbose: bool) -> None:
    """
    Set up logging based on the debug and verbose flags.

    Args:
        debug: Enable debug logging if True.
        verbose: Enable info logging if True.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


def main(args: dict[str, Any]) -> int:
    """Run a craps simulation based on parsed CLI arguments."""
    debug = bool(args.get("--debug", False))
    verbose = bool(args.get("--verbose", False))

    setup_logging(debug=debug, verbose=verbose)

    config_path = str(args.get("--config") or DEFAULT_CONFIG_PATH)
    max_rolls = _parse_max_rolls(args.get("--max-rolls"))
    clear = not bool(args.get("--no-clear", False))
    frame_delay = _parse_frame_delay(args.get("--frame-delay"))

    LOGGER.info(
        "Starting simulation",
        extra={
            "config_path": config_path,
            "max_rolls": max_rolls,
            "clear": clear,
            "frame_delay": frame_delay,
        },
    )

    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        LOGGER.error("Failed to load config: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    cli_arguments: dict[str, Any] = docopt.docopt(
        USAGE,
        options_first=False,
        version=VERSION,
    )
    sys.exit(main(cli_arguments))
