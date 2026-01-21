"""Tests for the core craps rules engine."""

from __future__ import annotations

import random

from p6_craps.dice import Dice, Roll
from p6_craps.engine import CrapsEngine
from p6_craps.enums import PassLineOutcome, Phase


class TestCrapsEngine:
    """Test suite for CrapsEngine."""

    def test_initial_state(self) -> None:
        """New engine starts in come-out with no point."""
        engine = CrapsEngine()
        assert engine.phase == Phase.COME_OUT
        assert engine.point is None
        assert engine.completed_points == 0

    def test_come_out_natural_wins(self) -> None:
        """Rolling 7 or 11 on come-out wins."""
        engine = CrapsEngine()
        result = engine.apply_roll(Roll(d1=3, d2=4))
        assert result.pass_line_outcome == PassLineOutcome.WIN
        assert result.phase_after == Phase.COME_OUT
        assert result.point_after is None

    def test_come_out_craps_loses(self) -> None:
        """Rolling 2, 3, or 12 on come-out loses."""
        engine = CrapsEngine()
        result = engine.apply_roll(Roll(d1=1, d2=1))
        assert result.pass_line_outcome == PassLineOutcome.LOSS
        assert result.phase_after == Phase.COME_OUT
        assert result.point_after is None

    def test_come_out_establishes_point(self) -> None:
        """Rolling a point number establishes point and moves to point-on."""
        engine = CrapsEngine()
        result = engine.apply_roll(Roll(d1=2, d2=2))
        assert result.pass_line_outcome == PassLineOutcome.PUSH
        assert result.phase_after == Phase.POINT_ON
        assert result.point_after == 4

    def test_point_on_hits_point(self) -> None:
        """Hitting the point wins and resets to come-out."""
        engine = CrapsEngine()
        engine.apply_roll(Roll(d1=3, d2=3))  # point 6
        result = engine.apply_roll(Roll(d1=2, d2=4))
        assert result.pass_line_outcome == PassLineOutcome.WIN
        assert result.phase_after == Phase.COME_OUT
        assert result.point_after is None
        assert engine.completed_points == 1

    def test_point_on_seven_out(self) -> None:
        """Rolling 7 during point-on loses and resets to come-out."""
        engine = CrapsEngine()
        engine.apply_roll(Roll(d1=2, d2=3))  # point 5
        result = engine.apply_roll(Roll(d1=3, d2=4))
        assert result.pass_line_outcome == PassLineOutcome.LOSS
        assert result.phase_after == Phase.COME_OUT
        assert result.point_after is None

    def test_point_on_other_roll_pushes(self) -> None:
        """Non-point, non-7 rolls during point-on continue play."""
        engine = CrapsEngine()
        engine.apply_roll(Roll(d1=3, d2=3))  # point 6
        result = engine.apply_roll(Roll(d1=2, d2=3))  # roll 5
        assert result.pass_line_outcome == PassLineOutcome.PUSH
        assert result.phase_after == Phase.POINT_ON
        assert result.point_after == 6

    def test_dice_roll_determinism(self) -> None:
        """Dice with the same seed should roll the same values."""
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        dice1 = Dice(rng=rng1)
        dice2 = Dice(rng=rng2)
        roll1 = dice1.roll()
        roll2 = dice2.roll()
        assert roll1 == roll2
