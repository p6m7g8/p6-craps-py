"""Tests for game orchestration and stop conditions."""

from __future__ import annotations

from p6_craps.dice import Roll
from p6_craps.game import Game, GameConfig, GameStopReason, PlayerState
from p6_craps.models import Bankroll, Player


class SequenceDice:
    """Deterministic dice for testing."""

    def __init__(self, rolls: list[Roll]) -> None:
        self._rolls = list(rolls)

    def roll(self) -> Roll:
        if not self._rolls:
            raise IndexError("No rolls remaining")
        return self._rolls.pop(0)


def _player(name: str, balance: int, max_win: int | None = None) -> Player:
    return Player(name=name, bankroll=Bankroll(balance=balance, max_win=max_win))


def _replace_players(game: Game, players: list[PlayerState]) -> None:
    # Test helper: mutate internal states to simulate bankroll/limits changes.
    game._player_states = tuple(players + [None] * (9 - len(players)))


def test_shooter_rotates_on_seven_out() -> None:
    """Seven-out during point-on should rotate the shooter."""
    rolls = [Roll(3, 3), Roll(3, 4)]
    dice = SequenceDice(rolls)
    players = (
        PlayerState(player=_player("A", 100)),
        PlayerState(player=_player("B", 100)),
    )
    game = Game.from_players(players=players, dice=dice)
    step1 = game.step()
    assert step1.shooter_index == 0
    step2 = game.step()
    assert step2.shooter_index == 1


def test_stop_on_target_points() -> None:
    """Game stops when target points are reached."""
    rolls = [Roll(2, 2), Roll(2, 2)]
    dice = SequenceDice(rolls)
    players = (PlayerState(player=_player("A", 100)),)
    game = Game.from_players(players=players, dice=dice, config=GameConfig(target_points=1))
    assert game.step().stop_reason is None
    assert game.step().stop_reason == GameStopReason.TARGET_POINTS_REACHED


def test_stop_on_max_rolls() -> None:
    """Game stops when max rolls are reached."""
    rolls = [Roll(3, 4)]
    dice = SequenceDice(rolls)
    players = (PlayerState(player=_player("A", 100)),)
    game = Game.from_players(players=players, dice=dice, config=GameConfig(max_rolls=1))
    assert game.step().stop_reason == GameStopReason.MAX_ROLLS_REACHED


def test_stop_conditions_from_player_states() -> None:
    """Stop conditions react to player bankroll and max win status."""
    rolls = [Roll(3, 4)]
    dice = SequenceDice(rolls)
    players = (
        PlayerState(player=_player("A", 100)),
        PlayerState(player=_player("B", 100)),
    )
    game = Game.from_players(players=players, dice=dice)

    no_bankroll = [PlayerState(player=_player("A", 0)), PlayerState(player=_player("B", 0))]
    _replace_players(game, no_bankroll)
    assert game.check_stop() == GameStopReason.NO_BANKROLL_REMAINING

    maxed = [
        PlayerState(player=_player("A", 50, max_win=50)),
        PlayerState(player=_player("B", 50, max_win=50)),
    ]
    _replace_players(game, maxed)
    assert game.check_stop() == GameStopReason.ALL_MAX_WIN_REACHED

    only_non_shooter = [PlayerState(player=_player("A", 50), can_shoot=False)]
    _replace_players(game, only_non_shooter)
    assert game.check_stop() == GameStopReason.ONLY_NON_SHOOTER_LEFT
