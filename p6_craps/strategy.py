"""Betting strategy definitions for the craps simulator.

This module defines:

* A protocol for strategies.
* A simple value object that describes bet decisions.
* A concrete "flat pass line" strategy.
* A factory for resolving strategies by name.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Mapping, Protocol, Sequence, runtime_checkable

from .engine import Phase
from .players import PlayerState


@dataclass(slots=True, frozen=True)
class BetDecision:
    """Describe an intended bet operation for a player.

    The actual execution and tracking of these decisions will be handled
    by the table/engine layer in a later step.
    """

    action: str
    bet_type: str
    amount: int

    def __post_init__(self) -> None:
        """Perform basic validation on the bet decision."""
        if self.amount <= 0:
            raise ValueError("bet amount must be positive")


@runtime_checkable
class Strategy(Protocol):
    """Protocol for betting strategies."""

    name: str

    def decide(
        self,
        game_state: Mapping[str, Any],
        player_state: PlayerState,
    ) -> Sequence[BetDecision]:
        """Return a sequence of bet operations based on the current state."""


class FlatPassStrategy:
    """Simple strategy that plays a flat pass-line bet on come-out.

    Behavior (for now):

    * On come-out:
      * If the player does not already have a pass-line bet (as indicated
        by ``game_state["has_pass_line_bet"]``) and has sufficient
        bankroll, place a single flat pass-line bet.
    * Otherwise:
      * Do nothing.

    This strategy will be extended later to add odds and more nuanced
    behavior.
    """

    name = "flat_pass"

    def __init__(self, unit: int = 25) -> None:
        """Initialize the strategy.

        Args:
            unit: The flat pass-line bet amount to attempt.
        """
        if unit <= 0:
            raise ValueError("unit must be positive")
        self._unit = unit

    def decide(
        self,
        game_state: Mapping[str, Any],
        player_state: PlayerState,
    ) -> Sequence[BetDecision]:
        """Return bet decisions for the current state.

        Expected keys in ``game_state``:

        * ``phase``: a :class:`Phase` value.
        * ``has_pass_line_bet``: bool indicating whether the player
          already has an active pass-line bet.

        The function is intentionally conservative and returns an empty
        list whenever required context is missing.
        """
        decisions: List[BetDecision] = []

        phase = game_state.get("phase")
        has_pass_line_bet = bool(game_state.get("has_pass_line_bet", False))

        if phase is not Phase.COME_OUT:
            # Strategy only acts on come-out rolls.
            return decisions

        if has_pass_line_bet:
            # Already have a pass-line bet; do nothing.
            return decisions

        if player_state.bankroll < self._unit:
            # Not enough bankroll for the base unit.
            return decisions

        decisions.append(
            BetDecision(
                action="place",
                bet_type="pass_line",
                amount=self._unit,
            )
        )
        return decisions


def get_strategy_by_name(name: str) -> Strategy:
    """Return a strategy instance for the given name.

    Args:
        name: Strategy name from configuration (case-insensitive).

    Raises:
        ValueError: If the name does not correspond to a known strategy.
    """
    normalized = name.strip().lower()

    if normalized == "flat_pass":
        return FlatPassStrategy()

    raise ValueError(f"Unknown strategy: {name!r}")
