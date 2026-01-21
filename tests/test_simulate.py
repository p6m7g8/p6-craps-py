"""Tests for simulation helpers."""

from __future__ import annotations

from p6_craps.game import GameConfig, PlayerState
from p6_craps.models import Bankroll, Player
from p6_craps.simulate import (
    game_config_from_config,
    players_from_config,
    run_until_complete,
    simulation_config_from_config,
)


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


def test_players_from_config_defaults() -> None:
    """Config should return default players when not provided."""
    players = players_from_config({})
    assert len(players) >= 1


def test_players_from_config_custom() -> None:
    """Config should create player states from entries."""
    config = {
        "players": [
            {"name": "A", "bankroll": 200, "base_bet": 10, "strategy": "martingale"},
            {"name": "B", "bankroll": 150, "can_shoot": False},
        ]
    }
    players = players_from_config(config)
    assert len(players) == 2
    assert players[0].player.bankroll.balance == 200
    assert players[1].can_shoot is False


def test_game_config_from_config() -> None:
    """Game config should honor overrides and defaults."""
    config = {"target_points": 2, "max_rolls": 10}
    game_config = game_config_from_config(config, max_rolls=None)
    assert game_config.target_points == 2
    assert game_config.max_rolls == 10
    override = game_config_from_config(config, max_rolls=5)
    assert override.max_rolls == 5


def test_simulation_config_from_config() -> None:
    """Simulation config should merge CLI overrides."""
    config = {"frame_delay": 0.5, "clear": False}
    sim_config = simulation_config_from_config(config, frame_delay=0.0, clear=True)
    assert sim_config.frame_delay == 0.5
    assert sim_config.clear is False
