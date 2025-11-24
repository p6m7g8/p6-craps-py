"""Runtime player state models for the craps simulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .config import Config, PlayerConfig


@dataclass(slots=True)
class PlayerState:
    """Runtime representation of a player during a simulation run.

    This object tracks the current bankroll and per-shooter profit/loss,
    while delegating static properties (name, strategy, limits) to the
    underlying :class:`PlayerConfig`.
    """

    config: PlayerConfig
    bankroll: int
    total_profit: int = 0
    shooter_profit: int = 0
    is_current_shooter: bool = False
    points_played_as_shooter: int = 0

    @property
    def name(self) -> str:
        """Convenience accessor for the player's name."""
        return self.config.name

    @property
    def strategy_name(self) -> str:
        """Return the configured strategy name for this player."""
        return self.config.strategy

    @property
    def can_be_shooter(self) -> bool:
        """Return whether this player is allowed to be the shooter."""
        return self.config.can_be_shooter

    def credit(self, amount: int) -> None:
        """Increase the player's bankroll by ``amount``.

        Also updates total and shooter profit figures.
        """
        if amount < 0:
            raise ValueError("credit amount must be non-negative")

        self.bankroll += amount
        self.total_profit = self.bankroll - self.config.starting_bankroll

        if self.is_current_shooter:
            self.shooter_profit += amount

    def debit(self, amount: int) -> None:
        """Decrease the player's bankroll by ``amount``.

        Raises:
            ValueError: If ``amount`` is negative or exceeds the
                available bankroll.
        """
        if amount < 0:
            raise ValueError("debit amount must be non-negative")

        if amount > self.bankroll:
            raise ValueError(
                f"insufficient bankroll for player {self.name}: "
                f"attempted to debit {amount}, bankroll={self.bankroll}"
            )

        self.bankroll -= amount
        self.total_profit = self.bankroll - self.config.starting_bankroll

        if self.is_current_shooter:
            self.shooter_profit -= amount

    @property
    def has_reached_min_bankroll(self) -> bool:
        """Return True if the player has reached their configured minimum.

        If the player does not define a specific minimum, this property
        always returns False. Global simulation limits are enforced
        separately.
        """
        if self.config.min_bankroll is None:
            return False
        return self.bankroll <= self.config.min_bankroll

    @property
    def has_reached_max_bankroll(self) -> bool:
        """Return True if the player has reached their configured maximum.

        If the player does not define a specific maximum, this property
        always returns False. Global simulation limits are enforced
        separately.
        """
        if self.config.max_bankroll is None:
            return False
        return self.bankroll >= self.config.max_bankroll


def create_player_states(cfg: Config) -> List[PlayerState]:
    """Create initial player states from the loaded configuration.

    Each :class:`PlayerState` starts with its configured starting
    bankroll and zero profit.
    """
    players: List[PlayerState] = []

    for player_cfg in cfg.players:
        players.append(
            PlayerState(
                config=player_cfg,
                bankroll=player_cfg.starting_bankroll,
                total_profit=0,
                shooter_profit=0,
                is_current_shooter=False,
                points_played_as_shooter=0,
            )
        )

    return players
