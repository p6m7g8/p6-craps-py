"""Dice primitives for the craps simulator."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(slots=True, frozen=True)
class Roll:
    """Immutable dice roll."""

    d1: int
    d2: int

    def __post_init__(self) -> None:
        """Validate die values are within standard range."""
        if not 1 <= self.d1 <= 6:
            raise ValueError(f"d1 must be between 1 and 6, got {self.d1}")
        if not 1 <= self.d2 <= 6:
            raise ValueError(f"d2 must be between 1 and 6, got {self.d2}")

    @property
    def total(self) -> int:
        """Return the sum of both dice."""
        return self.d1 + self.d2


@dataclass(slots=True)
class Dice:
    """Standard two-dice roller with injectable RNG."""

    rng: random.Random

    def roll(self) -> Roll:
        """Roll two dice using the configured RNG."""
        return Roll(d1=self.rng.randint(1, 6), d2=self.rng.randint(1, 6))
