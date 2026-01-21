"""Core data models for players and tables."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional, Tuple


@dataclass(slots=True, frozen=True)
class Bankroll:
    """Player bankroll with optional maximum win target."""

    balance: int
    max_win: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate bankroll configuration."""
        if self.balance < 0:
            raise ValueError(f"Bankroll balance cannot be negative, got {self.balance}")
        if self.max_win is not None and self.max_win <= 0:
            raise ValueError(f"max_win must be positive, got {self.max_win}")

    def apply(self, delta: int) -> Bankroll:
        """Return a new bankroll with delta applied."""
        new_balance = self.balance + delta
        if new_balance < 0:
            raise ValueError("Bankroll cannot go negative")
        return replace(self, balance=new_balance)


@dataclass(slots=True, frozen=True)
class Player:
    """Player identity and bankroll."""

    name: str
    bankroll: Bankroll

    def __post_init__(self) -> None:
        """Validate player configuration."""
        if not self.name.strip():
            raise ValueError("Player name cannot be empty")


@dataclass(slots=True, frozen=True)
class Table:
    """Craps table seating for up to nine players."""

    seats: Tuple[Optional[Player], ...]

    def __post_init__(self) -> None:
        """Validate seat configuration."""
        if len(self.seats) != 9:
            raise ValueError(f"Table must have exactly 9 seats, got {len(self.seats)}")

    @classmethod
    def empty(cls) -> Table:
        """Create an empty table with nine open seats."""
        return cls(seats=(None,) * 9)

    def seat_player(self, seat_index: int, player: Player) -> Table:
        """Return a new table with a player seated."""
        if not 0 <= seat_index < 9:
            raise IndexError(f"Seat index must be 0-8, got {seat_index}")
        if self.seats[seat_index] is not None:
            raise ValueError(f"Seat {seat_index} is already occupied")
        updated = list(self.seats)
        updated[seat_index] = player
        return Table(seats=tuple(updated))
