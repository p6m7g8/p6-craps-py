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
