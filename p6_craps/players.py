"""Runtime player state models for the craps simulator."""

from __future__ import annotations

from dataclasses import dataclass

from .config import PlayerConfig


@dataclass(slots=True)
class PlayerState:
    """Runtime representation of a player during a simulation run."""

    config: PlayerConfig
    bankroll: int

    @property
    def name(self) -> str:
        """Convenience accessor for the player's name."""
        return self.config.name
