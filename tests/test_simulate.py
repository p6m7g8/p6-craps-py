"""Tests for simulation helpers."""

from __future__ import annotations

from p6_craps.game import GameConfig, PlayerState
from p6_craps.models import Bankroll, Player
from p6_craps.simulate import run_until_complete


def _player(name: str, bankroll: int, max_win: int | None = None) -> PlayerState:
    return PlayerState(player=Player(name=name, bankroll=Bankroll(balance=bankroll, max_win=max_win)))


def test_run_until_complete_stops_on_max_rolls() -> None:
    """Simulation should respect max rolls stop condition."""
    players = (_player("A", 1000),)
    rolls, points = run_until_complete(players, GameConfig(max_rolls=2))
    assert rolls == 2
    assert points >= 0


def test_run_until_complete_stops_on_target_points() -> None:
    """Simulation should stop when target points are reached."""
    players = (_player("A", 1000),)
    rolls, points = run_until_complete(players, GameConfig(target_points=1))
    assert points == 1
    assert rolls >= 1
