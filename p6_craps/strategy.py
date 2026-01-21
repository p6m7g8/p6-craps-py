"""Betting strategy framework for the craps simulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from p6_craps.enums import PassLineOutcome


@dataclass(slots=True, frozen=True)
class BettingState:
    """State used by betting strategies."""

    bankroll: int
    base_bet: int
    max_bet: Optional[int] = None
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    last_outcome: Optional[PassLineOutcome] = None

    def __post_init__(self) -> None:
        """Validate betting state."""
        if self.bankroll < 0:
            raise ValueError("bankroll must be non-negative")
        if self.base_bet <= 0:
            raise ValueError("base_bet must be positive")
        if self.max_bet is not None and self.max_bet <= 0:
            raise ValueError("max_bet must be positive")
        if self.max_bet is not None and self.max_bet < self.base_bet:
            raise ValueError("max_bet cannot be less than base_bet")
        if self.consecutive_wins < 0:
            raise ValueError("consecutive_wins must be non-negative")
        if self.consecutive_losses < 0:
            raise ValueError("consecutive_losses must be non-negative")


@dataclass(slots=True, frozen=True)
class BetDecision:
    """Betting decision for a single roll."""

    amount: int
    reason: str

    def __post_init__(self) -> None:
        """Validate bet decision."""
        if self.amount < 0:
            raise ValueError("amount must be non-negative")
        if not self.reason.strip():
            raise ValueError("reason must be non-empty")


class BettingStrategy(Protocol):
    """Protocol for betting strategies."""

    def next_bet(self, state: BettingState) -> BetDecision:
        """Return the next bet decision for a player."""


@dataclass(slots=True, frozen=True)
class FlatBetStrategy:
    """Always wager the base bet amount."""

    def next_bet(self, state: BettingState) -> BetDecision:
        """Return a flat bet, capped by bankroll."""
        amount = min(state.base_bet, state.bankroll)
        return BetDecision(amount=amount, reason="flat bet")


@dataclass(slots=True, frozen=True)
class MartingaleStrategy:
    """Double the bet after losses, capped by max bet and bankroll."""

    def next_bet(self, state: BettingState) -> BetDecision:
        """Return a martingale bet based on consecutive losses."""
        bet = state.base_bet * (2**state.consecutive_losses)
        cap = state.max_bet if state.max_bet is not None else bet
        amount = min(bet, cap, state.bankroll)
        return BetDecision(amount=amount, reason="martingale")


@dataclass(slots=True, frozen=True)
class ParoliStrategy:
    """Double the bet after wins, capped by max bet and bankroll."""

    def next_bet(self, state: BettingState) -> BetDecision:
        """Return a paroli bet based on consecutive wins."""
        bet = state.base_bet * (2**state.consecutive_wins)
        cap = state.max_bet if state.max_bet is not None else bet
        amount = min(bet, cap, state.bankroll)
        return BetDecision(amount=amount, reason="paroli")
