"""Betting strategy definitions for the craps simulator."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


@runtime_checkable
class Strategy(Protocol):
    """Protocol for betting strategies.

    Concrete implementations will examine the current game and player
    state and decide what bets to place, change, or remove.
    """

    name: str

    def decide(
        self,
        game_state: Mapping[str, Any],
        player_state: Mapping[str, Any],
    ) -> Sequence[Any]:
        """Return a sequence of bet operations based on the current state."""
