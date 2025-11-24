"""Shared constants for the craps simulator."""

from __future__ import annotations

# Strategy names
STRATEGY_FLAT_PASS = "flat_pass"

# Game state keys used between engine, strategies, and simulation.
GAME_STATE_PHASE = "phase"
GAME_STATE_HAS_PASS_LINE_BET = "has_pass_line_bet"

# Bet actions
ACTION_PLACE = "place"

# Bet types
BET_TYPE_PASS_LINE = "pass_line"

# Stop reasons for a simulation run.
STOP_REASON_MAX_POINTS = "max_points"
STOP_REASON_BANKROLL = "bankroll_limits"
STOP_REASON_MAX_ROLLS = "max_rolls"

DEFAULT_CONFIG_PATH = "config.json"
