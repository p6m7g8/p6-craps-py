"""Betting strategy definitions for the craps simulator.

This module defines:

* A protocol for strategies.
* A simple value object that describes bet decisions.
* A concrete "flat pass line" strategy.
* Additional place-bet and odds-based strategies.
* A factory for resolving strategies by name.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Protocol,
    Sequence,
    runtime_checkable,
)

from .constants import (
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
        by ``game_state[GAME_STATE_HAS_PASS_LINE_BET]``) and has sufficient
        bankroll, place a single flat pass-line bet.
    * Otherwise:
      * Do nothing.

    This strategy will be extended later to add odds and more nuanced
    behavior.
    """

    name = STRATEGY_FLAT_PASS

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
        """Return bet decisions for the current state."""
        decisions: List[BetDecision] = []

        phase = game_state.get(GAME_STATE_PHASE)
        has_pass_line_bet = bool(game_state.get(GAME_STATE_HAS_PASS_LINE_BET, False))

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
                action=ACTION_PLACE,
                bet_type=BET_TYPE_PASS_LINE,
                amount=self._unit,
            )
        )
        return decisions


class PassLineWithOddsStrategy:
    """Strategy that combines a flat pass-line bet with odds.

    Behavior:

    * On come-out:
      * Ensure a flat pass-line bet of ``flat_unit`` if the player does
        not already have one and has enough bankroll.
    * On point-on:
      * If the player has a pass-line bet but does not yet have odds, and
        has sufficient bankroll, place odds equal to
        ``flat_unit * odds_multiple``.
    """

    name = STRATEGY_PASSLINE_WITH_ODDS

    def __init__(self, flat_unit: int = 25, odds_multiple: int = 2) -> None:
        """Initialize the strategy.

        Args:
            flat_unit: Base pass-line bet amount.
            odds_multiple: Multiplier applied to the flat unit to compute
                the odds amount.
        """
        if flat_unit <= 0:
            raise ValueError("flat_unit must be positive")
        if odds_multiple <= 0:
            raise ValueError("odds_multiple must be positive")

        self._flat_unit = flat_unit
        self._odds_multiple = odds_multiple

    def decide(
        self,
        game_state: Mapping[str, Any],
        player_state: PlayerState,
    ) -> Sequence[BetDecision]:
        """Return bet decisions for the current state."""
        decisions: List[BetDecision] = []

        phase = game_state.get(GAME_STATE_PHASE)
        has_pass_line_bet = bool(game_state.get(GAME_STATE_HAS_PASS_LINE_BET, False))
        has_pass_line_odds = bool(game_state.get(GAME_STATE_HAS_PASS_LINE_ODDS, False))

        remaining = player_state.bankroll

        if phase is Phase.COME_OUT and not has_pass_line_bet:
            if remaining >= self._flat_unit:
                decisions.append(
                    BetDecision(
                        action=ACTION_PLACE,
                        bet_type=BET_TYPE_PASS_LINE,
                        amount=self._flat_unit,
                    )
                )
                remaining -= self._flat_unit

        if phase is Phase.POINT_ON and has_pass_line_bet and not has_pass_line_odds:
            odds_amount = self._flat_unit * self._odds_multiple
            if remaining >= odds_amount:
                decisions.append(
                    BetDecision(
                        action=ACTION_PLACE,
                        bet_type=BET_TYPE_PASS_LINE_ODDS,
                        amount=odds_amount,
                    )
                )

        return decisions


class PlaceSixEightStrategy:
    """Strategy that places bets on 6 and 8 when a point is on.

    Behavior:

    * On point-on:
      * If the player does not yet have a place bet on 6 or 8 and has
        sufficient bankroll, place up to one unit on each of 6 and 8.
    * On come-out:
      * Do nothing.
    """

    name = STRATEGY_PLACE_6_8

    def __init__(self, unit: int = 30) -> None:
        """Initialize the strategy.

        Args:
            unit: The amount to place on each of 6 and 8.
        """
        if unit <= 0:
            raise ValueError("unit must be positive")
        self._unit = unit

    def decide(
        self,
        game_state: Mapping[str, Any],
        player_state: PlayerState,
    ) -> Sequence[BetDecision]:
        """Return bet decisions for the current state."""
        decisions: List[BetDecision] = []

        phase = game_state.get(GAME_STATE_PHASE)
        if phase is not Phase.POINT_ON:
            # Only act when there is a point established.
            return decisions

        has_place_6 = bool(game_state.get(GAME_STATE_HAS_PLACE_6, False))
        has_place_8 = bool(game_state.get(GAME_STATE_HAS_PLACE_8, False))

        remaining = player_state.bankroll

        if not has_place_6 and remaining >= self._unit:
            decisions.append(
                BetDecision(
                    action=ACTION_PLACE,
                    bet_type=BET_TYPE_PLACE_6,
                    amount=self._unit,
                )
            )
            remaining -= self._unit

        if not has_place_8 and remaining >= self._unit:
            decisions.append(
                BetDecision(
                    action=ACTION_PLACE,
                    bet_type=BET_TYPE_PLACE_8,
                    amount=self._unit,
                )
            )

        return decisions


_STRATEGY_REGISTRY: Dict[str, Callable[[], Strategy]] = {
    STRATEGY_FLAT_PASS: FlatPassStrategy,
    STRATEGY_PASSLINE_WITH_ODDS: PassLineWithOddsStrategy,
    STRATEGY_PLACE_6_8: PlaceSixEightStrategy,
}


def get_strategy_by_name(name: str) -> Strategy:
    """Return a strategy instance for the given name.

    Args:
        name: Normalized strategy name from configuration.

    Raises:
        ValueError: If the name does not correspond to a known strategy.
    """
    try:
        factory = _STRATEGY_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Unknown strategy: {name!r}") from exc

    return factory()
