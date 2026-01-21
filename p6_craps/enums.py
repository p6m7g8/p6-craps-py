"""Enumerations for craps game state and outcomes."""

from __future__ import annotations

import enum


class Phase(enum.Enum):
    """Craps table phase."""

    COME_OUT = "come_out"
    POINT_ON = "point_on"


class PassLineOutcome(enum.Enum):
    """Pass line outcome for a roll."""

    WIN = "win"
    LOSS = "loss"
    PUSH = "push"
