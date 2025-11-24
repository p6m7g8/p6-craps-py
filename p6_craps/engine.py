"""Core craps rules and state handling.

This module implements a minimal craps engine responsible for:

* Generating dice rolls.
* Managing come-out and point-on phases.
* Tracking the current point and completed point cycles.
* Determining basic pass-line outcomes for each roll.
"""

from __future__ import annotations

import enum
import random
from dataclasses import dataclass
from typing import Optional


class Phase(enum.Enum):
    """Craps table phase."""

    COME_OUT = "come_out"
    POINT_ON = "point_on"


class PassLineOutcome(enum.Enum):
    """Pass line result for a single roll."""

    NONE = "none"
    WIN = "win"
    LOSS = "loss"


@dataclass(slots=True, frozen=True)
class Roll:
    """A single dice roll."""

    d1: int
    d2: int

    @property
    def total(self) -> int:
        """Return the sum of the dice."""
        return self.d1 + self.d2

    @property
    def is_craps(self) -> bool:
        """Return True if the roll is craps (2, 3, or 12)."""
        return self.total in {2, 3, 12}

    @property
    def is_natural(self) -> bool:
        """Return True if the roll is a natural (7 or 11)."""
        return self.total in {7, 11}


@dataclass(slots=True, frozen=True)
class PointCycleResult:
    """Result of applying a roll to the current point cycle."""

    roll: Roll
    phase_before: Phase
    phase_after: Phase
    point_before: Optional[int]
    point_after: Optional[int]
    pass_line_outcome: PassLineOutcome
    completed_point: bool


class CrapsEngine:
    """Basic craps state machine for pass-line play.

    This engine tracks:

    * The current table phase (come-out vs point-on).
    * The active point number, if any.
    * The number of completed point cycles.

    It does **not** yet know about specific bets beyond pass-line
    semantics; that will be layered on in later commits.
    """

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        """
        Initialize the craps engine.

        Args:
            rng: Optional random number generator. If not provided, a
                new ``random.Random`` instance is created. Injecting an
                RNG allows deterministic tests and reproducible runs.
        """
        self._rng: random.Random = rng or random.Random()
        self.phase: Phase = Phase.COME_OUT
        self.point: Optional[int] = None
        self.completed_points: int = 0

    def roll(self) -> PointCycleResult:
        """Generate a random roll and apply it to the current state."""
        d1 = self._rng.randint(1, 6)
        d2 = self._rng.randint(1, 6)
        return self.apply_roll(Roll(d1=d1, d2=d2))

    def apply_roll(self, roll: Roll) -> PointCycleResult:
        """
        Apply a specific roll to the current state.

        This method is the core of the craps point-cycle state machine
        and is intentionally deterministic given the current engine
        state and roll.
        """
        phase_before = self.phase
        point_before = self.point
        pass_line_outcome = PassLineOutcome.NONE
        completed_point = False

        total = roll.total

        if self.phase is Phase.COME_OUT:
            # Standard pass-line come-out rules.
            if total in (7, 11):
                pass_line_outcome = PassLineOutcome.WIN
                # Remain in come-out, no point established.
            elif total in (2, 3, 12):
                pass_line_outcome = PassLineOutcome.LOSS
                # Remain in come-out, no point established.
            elif total in (4, 5, 6, 8, 9, 10):
                # Establish a point and move to point-on phase.
                self.phase = Phase.POINT_ON
                self.point = total
        else:
            # POINT_ON phase: the next roll either makes the point,
            # sevens out, or continues the hand.
            assert self.point is not None, "POINT_ON phase requires an active point."

            if total == self.point:
                pass_line_outcome = PassLineOutcome.WIN
                completed_point = True
                self._reset_to_come_out()
            elif total == 7:
                pass_line_outcome = PassLineOutcome.LOSS
                completed_point = True
                self._reset_to_come_out()
            # Any other total leaves the point and phase unchanged.

        if completed_point:
            self.completed_points += 1

        return PointCycleResult(
            roll=roll,
            phase_before=phase_before,
            phase_after=self.phase,
            point_before=point_before,
            point_after=self.point,
            pass_line_outcome=pass_line_outcome,
            completed_point=completed_point,
        )

    def _reset_to_come_out(self) -> None:
        """Reset the table to a come-out state with no active point."""
        self.phase = Phase.COME_OUT
        self.point = None
