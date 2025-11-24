#!/usr/bin/env python
"""CLI entrypoint for the p6 craps simulator.

This CLI loads a JSON configuration, runs a simulation, and renders a
terminal-friendly view of the evolving game state.
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Any, Optional

import docopt

from p6_craps.config import ConfigError, load_config
from p6_craps.sim import FrameCallback, Simulation, SimulationEvent
from p6_craps.stats import summarize_simulation
from p6_craps.ui.terminal import (
    build_header_info,
    draw_frame,
    render_frame,
    snapshot_players,
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


def _parse_max_rolls(raw_value: Any) -> Optional[int]:
    """Parse the optional ``--max-rolls`` value from the CLI."""
    if raw_value is None:
        return None

    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"--max-rolls must be an integer, got {raw_value!r}") from exc

    if value <= 0:
        raise SystemExit("--max-rolls must be a positive integer")

    return value


def _parse_frame_delay(raw_value: Any) -> float:
    """Parse the ``--frame-delay`` value from the CLI."""
    if raw_value is None:
        return 0.0

    try:
        value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"--frame-delay must be a number of seconds, got {raw_value!r}") from exc

    if value < 0:
        raise SystemExit("--frame-delay must be non-negative")

    return value


def _make_frame_callback(clear: bool, frame_delay: float) -> FrameCallback:
    """Create a frame callback that renders the current state to stdout."""
    interesting_stages = {
        "initial",
        "after_bets",
        "after_roll",
        "after_payouts",
    }

    def _callback(sim: Simulation, event: Optional[SimulationEvent], stage: str) -> None:
        # Prefer roll metadata from the event when available.
        if event is not None:
            roll_index = event.roll_index
            shooter_index = event.shooter_index
            shooter_roll_index = event.shooter_roll_index
        else:
            roll_index = sim.roll_index
            shooter_index = sim.current_shooter_index
            shooter_roll_index = sim.current_shooter_roll_index

        header = build_header_info(
            engine=sim.engine,
            roll_index=roll_index,
            shooter_index=shooter_index,
            shooter_roll_index=shooter_roll_index,
        )
        rows = snapshot_players(sim.players, sim.table)
        frame = render_frame(header, rows)
        draw_frame(sys.stdout, frame, clear=clear)

        if frame_delay > 0.0 and stage in interesting_stages:
            time.sleep(frame_delay)

    return _callback


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

    sim = Simulation(cfg)
    frame_callback = _make_frame_callback(clear=clear, frame_delay=frame_delay)
    result = sim.run(max_rolls=max_rolls, frame_callback=frame_callback)

    # Compute and log high-level summary statistics.
    summary = summarize_simulation(players=sim.players, result=result)
    LOGGER.info(
        "Simulation finished",
        extra={
            "stop_reason": summary.stop_reason,
            "completed_points": summary.completed_points,
            "total_rolls": summary.dice.total_rolls,
            "num_players": len(summary.players),
        },
    )

    # Keep the last frame on screen for interactive use.
    if sys.stdout.isatty():
        try:
            input("Press Enter to exit...")
        except EOFError:
            pass

    return 0


if __name__ == "__main__":
    cli_arguments: dict[str, Any] = docopt.docopt(
        USAGE,
        options_first=False,
        version=VERSION,
    )
    sys.exit(main(cli_arguments))
