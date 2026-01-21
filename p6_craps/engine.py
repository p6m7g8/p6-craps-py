"""Core craps rules engine implementing standard Las Vegas rules."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from p6_craps.dice import Dice, Roll
from p6_craps.enums import PassLineOutcome, Phase


@dataclass(slots=True, frozen=True)
class RollResult:
    """Outcome of applying a roll to the game state."""

    roll: Roll
    phase_before: Phase
    phase_after: Phase
    point_before: Optional[int]
    point_after: Optional[int]
    pass_line_outcome: PassLineOutcome


class CrapsEngine:
    """Craps rules engine for standard Las Vegas gameplay."""

    def __init__(self, rng: Optional[random.Random] = None, dice: Optional[Dice] = None) -> None:
        """Initialize engine with optional RNG or Dice."""
        if dice is not None and rng is not None:
            raise ValueError("Provide either dice or rng, not both")
        self._dice = dice or Dice(rng=rng or random.Random())
        self.phase = Phase.COME_OUT
        self.point: Optional[int] = None
        self.completed_points = 0

    def roll(self) -> RollResult:
        """Roll the dice and apply the outcome to the game state."""
        return self.apply_roll(self._dice.roll())

    def apply_roll(self, roll: Roll) -> RollResult:
        """Apply a roll to the current state and return the result."""
        phase_before = self.phase
        point_before = self.point
        total = roll.total

        if self.phase == Phase.COME_OUT:
            if total in (7, 11):
                outcome = PassLineOutcome.WIN
                phase_after = Phase.COME_OUT
                point_after = None
            elif total in (2, 3, 12):
                outcome = PassLineOutcome.LOSS
                phase_after = Phase.COME_OUT
                point_after = None
            elif total in (4, 5, 6, 8, 9, 10):
                outcome = PassLineOutcome.PUSH
                phase_after = Phase.POINT_ON
                point_after = total
            else:
                raise ValueError(f"Invalid roll total {total}")
        else:
            if self.point is None:
                raise ValueError("Point must be set in POINT_ON phase")
            if total == self.point:
                outcome = PassLineOutcome.WIN
                phase_after = Phase.COME_OUT
                point_after = None
                self.completed_points += 1
            elif total == 7:
                outcome = PassLineOutcome.LOSS
                phase_after = Phase.COME_OUT
                point_after = None
            else:
                outcome = PassLineOutcome.PUSH
                phase_after = Phase.POINT_ON
                point_after = self.point

        self.phase = phase_after
        self.point = point_after

        return RollResult(
            roll=roll,
            phase_before=phase_before,
            phase_after=phase_after,
            point_before=point_before,
            point_after=point_after,
            pass_line_outcome=outcome,
        )
