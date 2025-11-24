"""Shared constants for the craps simulator."""

from __future__ import annotations

# Strategy names
STRATEGY_FLAT_PASS = "flat_pass"
STRATEGY_PASSLINE_WITH_ODDS = "flat_pass_with_odds"
STRATEGY_PLACE_6_8 = "place_6_8"

# Game state keys used between engine, strategies, and simulation.
GAME_STATE_PHASE = "phase"
GAME_STATE_HAS_PASS_LINE_BET = "has_pass_line_bet"
GAME_STATE_HAS_PASS_LINE_ODDS = "has_pass_line_odds"
GAME_STATE_HAS_PLACE_6 = "has_place_6"
GAME_STATE_HAS_PLACE_8 = "has_place_8"

# Bet actions
ACTION_PLACE = "place"

# Bet types
BET_TYPE_PASS_LINE = "pass_line"
BET_TYPE_PASS_LINE_ODDS = "pass_line_odds"
BET_TYPE_PLACE_6 = "place_6"
BET_TYPE_PLACE_8 = "place_8"

# Stop reasons for a simulation run.
STOP_REASON_MAX_POINTS = "max_points"
STOP_REASON_BANKROLL = "bankroll_limits"
STOP_REASON_MAX_ROLLS = "max_rolls"

DEFAULT_CONFIG_PATH = "config.json"
