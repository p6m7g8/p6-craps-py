"""Tests for betting strategies."""

from __future__ import annotations

import pytest

from p6_craps.enums import PassLineOutcome
from p6_craps.strategy import (
    BetDecision,
    BettingState,
    FlatBetStrategy,
    MartingaleStrategy,
    ParoliStrategy,
)


def test_betting_state_validation() -> None:
    """Betting state should validate inputs."""
    with pytest.raises(ValueError, match="bankroll"):
        BettingState(bankroll=-1, base_bet=5)
    with pytest.raises(ValueError, match="base_bet"):
        BettingState(bankroll=10, base_bet=0)
    with pytest.raises(ValueError, match="max_bet"):
        BettingState(bankroll=10, base_bet=5, max_bet=0)
    with pytest.raises(ValueError, match="max_bet"):
        BettingState(bankroll=10, base_bet=10, max_bet=5)
    with pytest.raises(ValueError, match="consecutive_wins"):
        BettingState(bankroll=10, base_bet=5, consecutive_wins=-1)
    with pytest.raises(ValueError, match="consecutive_losses"):
        BettingState(bankroll=10, base_bet=5, consecutive_losses=-1)


def test_bet_decision_validation() -> None:
    """Bet decisions should validate amount and reason."""
    with pytest.raises(ValueError, match="amount"):
        BetDecision(amount=-1, reason="bad")
    with pytest.raises(ValueError, match="reason"):
        BetDecision(amount=1, reason="  ")


def test_flat_bet_caps_at_bankroll() -> None:
    """Flat bet should never exceed bankroll."""
    strategy = FlatBetStrategy()
    state = BettingState(bankroll=3, base_bet=10)
    decision = strategy.next_bet(state)
    assert decision.amount == 3


@pytest.mark.parametrize(
    ("losses", "expected"),
    [
        (0, 5),
        (1, 10),
        (2, 20),
    ],
)
def test_martingale_doubles(losses: int, expected: int) -> None:
    """Martingale should double after each loss."""
    strategy = MartingaleStrategy()
    state = BettingState(bankroll=100, base_bet=5, consecutive_losses=losses)
    decision = strategy.next_bet(state)
    assert decision.amount == expected


def test_martingale_respects_max_bet() -> None:
    """Martingale should honor max bet caps."""
    strategy = MartingaleStrategy()
    state = BettingState(bankroll=100, base_bet=5, max_bet=12, consecutive_losses=3)
    decision = strategy.next_bet(state)
    assert decision.amount == 12


def test_paroli_doubles_on_wins() -> None:
    """Paroli should double after each win."""
    strategy = ParoliStrategy()
    state = BettingState(bankroll=100, base_bet=5, consecutive_wins=2)
    decision = strategy.next_bet(state)
    assert decision.amount == 20


def test_paroli_respects_bankroll() -> None:
    """Paroli should never exceed bankroll."""
    strategy = ParoliStrategy()
    state = BettingState(bankroll=7, base_bet=5, consecutive_wins=2)
    decision = strategy.next_bet(state)
    assert decision.amount == 7
