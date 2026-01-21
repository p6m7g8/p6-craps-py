#!/usr/bin/env python
"""CLI entrypoint for the p6 craps simulator."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import docopt

from p6_craps.simulate import (
    game_config_from_config,
    players_from_config,
    run_simulation,
    simulation_config_from_config,
)

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
    LOGGER.debug("Loaded config", extra={"config_keys": sorted(cfg)})

    players = players_from_config(cfg)
    game_config = game_config_from_config(cfg, max_rolls=max_rolls)
    sim_config = simulation_config_from_config(cfg, frame_delay=frame_delay, clear=clear)
    try:
        return run_simulation(players, game_config=game_config, sim_config=sim_config)
    except ValueError as exc:
        LOGGER.error("Simulation failed: %s", exc)
        return 1


class ConfigError(RuntimeError):
    """Raised when configuration loading fails."""


def load_config(path: str) -> dict[str, Any]:
    """Load JSON configuration from disk."""
    if not path:
        raise ConfigError("Config path is required")
    config_path = Path(path)
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"Failed to read config: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON config: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Config must be a JSON object")
    return data


def _parse_max_rolls(value: Any) -> int | None:
    """Parse the max rolls option."""
    return _parse_positive_int(value, "max rolls")


def _parse_frame_delay(value: Any) -> float:
    """Parse the frame delay option."""
    if value is None:
        return 0.0
    try:
        delay = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Frame delay must be a number, got {value!r}") from exc
    if delay < 0:
        raise ConfigError("Frame delay must be non-negative")
    return delay


def _parse_positive_int(value: Any, label: str) -> int | None:
    """Parse a positive integer option or return None."""
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{label} must be an integer, got {value!r}") from exc
    if parsed <= 0:
        raise ConfigError(f"{label} must be positive")
    return parsed


if __name__ == "__main__":
    cli_arguments: dict[str, Any] = docopt.docopt(
        USAGE,
        options_first=False,
        version=VERSION,
    )
    sys.exit(main(cli_arguments))
