"""Tests for the betting strategy module."""

from p6_craps.config import PlayerConfig
from p6_craps.constants import (
    ACTION_PLACE,
    BET_TYPE_PASS_LINE,
    BET_TYPE_PASS_LINE_ODDS,
    BET_TYPE_PLACE_6,
    BET_TYPE_PLACE_8,
    GAME_STATE_HAS_PASS_LINE_BET,
    GAME_STATE_HAS_PASS_LINE_ODDS,
    GAME_STATE_HAS_PLACE_6,
    GAME_STATE_HAS_PLACE_8,
    GAME_STATE_PHASE,
    STRATEGY_FLAT_PASS,
    STRATEGY_PASSLINE_WITH_ODDS,
    STRATEGY_PLACE_6_8,
)
from p6_craps.engine import Phase
from p6_craps.players import PlayerState
from p6_craps.strategy import (
    BetDecision,
    FlatPassStrategy,
    PassLineWithOddsStrategy,
    PlaceSixEightStrategy,
    get_strategy_by_name,
)


def _make_player_state(
    name: str = "Player",
    bankroll: int = 2000,
    strategy_name: str = STRATEGY_FLAT_PASS,
) -> PlayerState:
    """Create a PlayerState with the given parameters."""
    cfg = PlayerConfig(
        name=name,
        starting_bankroll=bankroll,
        strategy=strategy_name,
        can_be_shooter=True,
    )
    return PlayerState(config=cfg, bankroll=cfg.starting_bankroll)


def test_get_strategy_by_name_returns_flat_pass() -> None:
    """Ensure get_strategy_by_name returns FlatPassStrategy for STRATEGY_FLAT_PASS."""
    strategy = get_strategy_by_name(STRATEGY_FLAT_PASS)
    assert isinstance(strategy, FlatPassStrategy)
    assert strategy.name == STRATEGY_FLAT_PASS


def test_get_strategy_by_name_returns_passline_with_odds() -> None:
    """Ensure get_strategy_by_name returns PassLineWithOddsStrategy."""
    strategy = get_strategy_by_name(STRATEGY_PASSLINE_WITH_ODDS)
    assert isinstance(strategy, PassLineWithOddsStrategy)
    assert strategy.name == STRATEGY_PASSLINE_WITH_ODDS


def test_get_strategy_by_name_returns_place_6_8() -> None:
    """Ensure get_strategy_by_name returns PlaceSixEightStrategy."""
    strategy = get_strategy_by_name(STRATEGY_PLACE_6_8)
    assert isinstance(strategy, PlaceSixEightStrategy)
    assert strategy.name == STRATEGY_PLACE_6_8


def test_flat_pass_places_bet_on_come_out_when_no_existing_bet() -> None:
    """FlatPassStrategy places a pass line bet on come-out when none exists."""
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
    """FlatPassStrategy does nothing when a pass line bet is already present."""
    player_state = _make_player_state()
    game_state = {
        GAME_STATE_PHASE: Phase.COME_OUT,
        GAME_STATE_HAS_PASS_LINE_BET: True,
    }

    strategy = FlatPassStrategy(unit=25)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions


def test_flat_pass_skips_when_insufficient_bankroll() -> None:
    """FlatPassStrategy does nothing when bankroll is below the unit size."""
    player_state = _make_player_state(bankroll=10)
    game_state = {
        GAME_STATE_PHASE: Phase.COME_OUT,
        GAME_STATE_HAS_PASS_LINE_BET: False,
    }

    strategy = FlatPassStrategy(unit=25)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions


def test_flat_pass_skips_when_not_come_out_phase() -> None:
    """FlatPassStrategy does nothing when the phase is not COME_OUT."""
    player_state = _make_player_state()
    game_state = {
        GAME_STATE_PHASE: Phase.POINT_ON,
        GAME_STATE_HAS_PASS_LINE_BET: False,
    }

    strategy = FlatPassStrategy(unit=25)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions


def test_passline_with_odds_places_flat_bet_on_come_out() -> None:
    """PassLineWithOddsStrategy places only the flat bet on come-out."""
    player_state = _make_player_state(strategy_name=STRATEGY_PASSLINE_WITH_ODDS)
    game_state = {
        GAME_STATE_PHASE: Phase.COME_OUT,
        GAME_STATE_HAS_PASS_LINE_BET: False,
        GAME_STATE_HAS_PASS_LINE_ODDS: False,
    }

    strategy = PassLineWithOddsStrategy(flat_unit=25, odds_multiple=2)
    decisions = strategy.decide(game_state, player_state)

    assert len(decisions) == 1
    decision = decisions[0]
    assert decision.bet_type == BET_TYPE_PASS_LINE
    assert decision.amount == 25


def test_passline_with_odds_places_odds_when_point_on_and_affordable() -> None:
    """PassLineWithOddsStrategy places odds when point is on and bankroll is sufficient."""
    player_state = _make_player_state(strategy_name=STRATEGY_PASSLINE_WITH_ODDS)
    game_state = {
        GAME_STATE_PHASE: Phase.POINT_ON,
        GAME_STATE_HAS_PASS_LINE_BET: True,
        GAME_STATE_HAS_PASS_LINE_ODDS: False,
    }

    strategy = PassLineWithOddsStrategy(flat_unit=25, odds_multiple=2)
    decisions = strategy.decide(game_state, player_state)

    assert len(decisions) == 1
    decision = decisions[0]
    assert decision.bet_type == BET_TYPE_PASS_LINE_ODDS
    assert decision.amount == 50


def test_passline_with_odds_skips_odds_when_insufficient_bankroll() -> None:
    """PassLineWithOddsStrategy does nothing when bankroll is below the odds amount."""
    player_state = _make_player_state(
        bankroll=40,
        strategy_name=STRATEGY_PASSLINE_WITH_ODDS,
    )
    game_state = {
        GAME_STATE_PHASE: Phase.POINT_ON,
        GAME_STATE_HAS_PASS_LINE_BET: True,
        GAME_STATE_HAS_PASS_LINE_ODDS: False,
    }

    strategy = PassLineWithOddsStrategy(flat_unit=25, odds_multiple=2)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions


def test_place_6_8_places_bets_when_point_on_and_affordable() -> None:
    """PlaceSixEightStrategy places place-6 and place-8 bets when affordable."""
    player_state = _make_player_state(
        bankroll=100,
        strategy_name=STRATEGY_PLACE_6_8,
    )
    game_state = {
        GAME_STATE_PHASE: Phase.POINT_ON,
        GAME_STATE_HAS_PLACE_6: False,
        GAME_STATE_HAS_PLACE_8: False,
    }

    strategy = PlaceSixEightStrategy(unit=30)
    decisions = strategy.decide(game_state, player_state)

    assert len(decisions) == 2
    bet_types = {d.bet_type for d in decisions}
    assert BET_TYPE_PLACE_6 in bet_types
    assert BET_TYPE_PLACE_8 in bet_types


def test_place_6_8_respects_existing_bets_and_bankroll() -> None:
    """PlaceSixEightStrategy only places missing bets within bankroll limits."""
    player_state = _make_player_state(
        bankroll=35,
        strategy_name=STRATEGY_PLACE_6_8,
    )
    game_state = {
        GAME_STATE_PHASE: Phase.POINT_ON,
        GAME_STATE_HAS_PLACE_6: True,
        GAME_STATE_HAS_PLACE_8: False,
    }

    strategy = PlaceSixEightStrategy(unit=30)
    decisions = strategy.decide(game_state, player_state)

    # Bankroll only allows a single unit; since 6 is already covered, 8 should be placed.
    assert len(decisions) == 1
    decision = decisions[0]
    assert decision.bet_type == BET_TYPE_PLACE_8
    assert decision.amount == 30


def test_place_6_8_skips_when_not_point_on() -> None:
    """PlaceSixEightStrategy does nothing when there is no point established."""
    player_state = _make_player_state(
        bankroll=100,
        strategy_name=STRATEGY_PLACE_6_8,
    )
    game_state = {
        GAME_STATE_PHASE: Phase.COME_OUT,
        GAME_STATE_HAS_PLACE_6: False,
        GAME_STATE_HAS_PLACE_8: False,
    }

    strategy = PlaceSixEightStrategy(unit=30)
    decisions = strategy.decide(game_state, player_state)

    assert not decisions
