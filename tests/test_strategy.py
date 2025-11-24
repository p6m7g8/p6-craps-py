"""Tests for the betting strategy module."""

from p6_craps.config import PlayerConfig
from p6_craps.constants import (
    ACTION_PLACE,
    BET_TYPE_PASS_LINE,
    GAME_STATE_HAS_PASS_LINE_BET,
    GAME_STATE_PHASE,
    STRATEGY_FLAT_PASS,
)
from p6_craps.engine import Phase
from p6_craps.players import PlayerState
from p6_craps.strategy import BetDecision, FlatPassStrategy, get_strategy_by_name


def _make_player_state(name: str = "Player", bankroll: int = 2000) -> PlayerState:
    cfg = PlayerConfig(
        name=name,
        starting_bankroll=bankroll,
        strategy=STRATEGY_FLAT_PASS,
        can_be_shooter=True,
    )
    return PlayerState(config=cfg, bankroll=cfg.starting_bankroll)


def test_get_strategy_by_name_returns_flat_pass() -> None:
    """
    Test that get_strategy_by_name returns an instance of FlatPassStrategy
    when provided with the STRATEGY_FLAT_PASS constant, and that the strategy's
    name attribute matches STRATEGY_FLAT_PASS.
    """
    strategy = get_strategy_by_name(STRATEGY_FLAT_PASS)
    assert isinstance(strategy, FlatPassStrategy)
    assert strategy.name == STRATEGY_FLAT_PASS


def test_flat_pass_places_bet_on_come_out_when_no_existing_bet() -> None:
    """
    Test that the FlatPassStrategy places a pass line bet of the specified unit amount
    when the game is in the come out phase and the player has no existing pass line bet.

    This test verifies:
    - The strategy returns exactly one decision.
    - The decision is to place a bet (ACTION_PLACE) on the pass line (BET_TYPE_PASS_LINE).
    - The bet amount matches the strategy's unit value (25).
    """
    player_state = _make_player_state()
    game_state = {
        GAME_STATE_PHASE: Phase.COME_OUT,
        GAME_STATE_HAS_PASS_LINE_BET: False,
    }

    strategy = FlatPassStrategy(unit=25)
    decisions = strategy.decide(game_state, player_state)

    assert len(decisions) == 1
    decision = decisions[0]
    assert isinstance(decision, BetDecision)
    assert decision.action == ACTION_PLACE
    assert decision.bet_type == BET_TYPE_PASS_LINE
    assert decision.amount == 25


def test_flat_pass_skips_when_already_has_pass_line_bet() -> None:
    """
    Test that the FlatPassStrategy does not place a new Pass Line bet if the player already has one.

    This test verifies that when the game is in the COME_OUT phase and the player already has a Pass Line bet,
    the strategy's decide method returns an empty list, indicating no additional bets are placed.
    """
    player_state = _make_player_state()
    game_state = {
        GAME_STATE_PHASE: Phase.COME_OUT,
        GAME_STATE_HAS_PASS_LINE_BET: True,
    }

    strategy = FlatPassStrategy(unit=25)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions


def test_flat_pass_skips_when_insufficient_bankroll() -> None:
    """
    Test that the FlatPassStrategy does not place a bet when the player's bankroll is insufficient.

    This test verifies that when the player's bankroll is less than the required betting unit,
    the strategy's decide method returns an empty list, indicating no bets are placed.
    """
    player_state = _make_player_state(bankroll=10)
    game_state = {
        GAME_STATE_PHASE: Phase.COME_OUT,
        GAME_STATE_HAS_PASS_LINE_BET: False,
    }

    strategy = FlatPassStrategy(unit=25)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions


def test_flat_pass_skips_when_not_come_out_phase() -> None:
    """
    Test that the FlatPassStrategy does not make any betting decisions when the game is not in the 'come out' phase.

    This test verifies that when the game phase is 'POINT_ON' (i.e., not the 'come out' phase) and the player does not
         have a pass line bet, the strategy's decide method returns an empty list, indicating no action is taken.
    """
    player_state = _make_player_state()
    game_state = {
        GAME_STATE_PHASE: Phase.POINT_ON,
        GAME_STATE_HAS_PASS_LINE_BET: False,
    }

    strategy = FlatPassStrategy(unit=25)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions
