"""Game orchestration and stop-condition logic for the craps simulator."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol, Tuple

from p6_craps.dice import Dice
from p6_craps.engine import CrapsEngine, RollResult
from p6_craps.enums import PassLineOutcome, Phase
from p6_craps.models import Player, Table


class StatsCollector(Protocol):
    """Interface for collecting game statistics."""

    def record_game_start(self, table: Table) -> None:
        """Record the start of a game."""

    def record_roll(self, roll_result: RollResult, shooter_index: int, roll_count: int, table: Table) -> None:
        """Record a single roll."""

    def record_game_end(self, reason: GameStopReason, roll_count: int, points_made: int) -> None:
        """Record the end of a game."""


class NullStatsCollector:
    """No-op stats collector."""

    def record_game_start(self, table: Table) -> None:
        """Ignore game start."""

    def record_roll(self, roll_result: RollResult, shooter_index: int, roll_count: int, table: Table) -> None:
        """Ignore roll."""

    def record_game_end(self, reason: GameStopReason, roll_count: int, points_made: int) -> None:
        """Ignore game end."""


class GameStopReason(str, Enum):
    """Reasons that a game can terminate."""

    TARGET_POINTS_REACHED = "target_points_reached"
    MAX_ROLLS_REACHED = "max_rolls_reached"
    NO_BANKROLL_REMAINING = "no_bankroll_remaining"
    ALL_MAX_WIN_REACHED = "all_max_win_reached"
    ONLY_NON_SHOOTER_LEFT = "only_non_shooter_left"


@dataclass(slots=True, frozen=True)
class GameConfig:
    """Configuration for stopping conditions."""

    target_points: Optional[int] = None
    max_rolls: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.target_points is not None and self.target_points <= 0:
            raise ValueError("target_points must be positive")
        if self.max_rolls is not None and self.max_rolls <= 0:
            raise ValueError("max_rolls must be positive")


@dataclass(slots=True, frozen=True)
class PlayerState:
    """Player runtime state for a game."""

    player: Player
    can_shoot: bool = True

    def has_bankroll(self) -> bool:
        """Return True if player can keep wagering."""
        return self.player.bankroll.balance > 0

    def reached_max_win(self) -> bool:
        """Return True if player has reached their configured max win."""
        max_win = self.player.bankroll.max_win
        return max_win is not None and self.player.bankroll.balance >= max_win


@dataclass(slots=True, frozen=True)
class GameStep:
    """Result of a single game step."""

    roll_result: RollResult
    shooter_index: int
    roll_count: int
    stop_reason: Optional[GameStopReason]


class Game:
    """Orchestrates a craps game across a table of players."""

    def __init__(
        self,
        table: Table,
        player_states: Tuple[Optional[PlayerState], ...],
        config: Optional[GameConfig] = None,
        rng: Optional[random.Random] = None,
        dice: Optional[Dice] = None,
        stats: Optional[StatsCollector] = None,
    ) -> None:
        """Initialize a game with a table, player states, and configuration."""
        if len(player_states) != 9:
            raise ValueError("player_states must have exactly 9 entries")
        for seat_index, seat in enumerate(table.seats):
            state = player_states[seat_index]
            if seat is None and state is not None:
                raise ValueError("player_states must be None for empty seats")
            if seat is not None and (state is None or state.player != seat):
                raise ValueError("player_states must match table seats")

        self._table = table
        self._player_states = player_states
        self._config = config or GameConfig()
        self._engine = CrapsEngine(rng=rng, dice=dice)
        self._stats = stats or NullStatsCollector()
        self.roll_count = 0
        self.shooter_index = self._first_shooter_index()

        self._stats.record_game_start(self._table)

    @classmethod
    def from_players(
        cls,
        players: Tuple[PlayerState, ...],
        config: Optional[GameConfig] = None,
        rng: Optional[random.Random] = None,
        dice: Optional[Dice] = None,
        stats: Optional[StatsCollector] = None,
    ) -> Game:
        """Build a table by seating players in order."""
        table = Table.empty()
        player_states: list[Optional[PlayerState]] = [None] * 9
        for seat_index, state in enumerate(players):
            if seat_index >= 9:
                raise ValueError("Cannot seat more than 9 players")
            table = table.seat_player(seat_index, state.player)
            player_states[seat_index] = state
        return cls(
            table=table,
            player_states=tuple(player_states),
            config=config,
            rng=rng,
            dice=dice,
            stats=stats,
        )

    def step(self) -> GameStep:
        """Advance the game by one roll."""
        roll_result = self._engine.roll()
        self.roll_count += 1
        self._stats.record_roll(
            roll_result=roll_result,
            shooter_index=self.shooter_index,
            roll_count=self.roll_count,
            table=self._table,
        )

        if self._should_rotate_shooter(roll_result):
            self.shooter_index = self._next_shooter_index(self.shooter_index)

        stop_reason = self.check_stop()
        if stop_reason is not None:
            self._stats.record_game_end(stop_reason, self.roll_count, self._engine.completed_points)

        return GameStep(
            roll_result=roll_result,
            shooter_index=self.shooter_index,
            roll_count=self.roll_count,
            stop_reason=stop_reason,
        )

    def snapshot(self) -> tuple[int, int]:
        """Return the roll count and points made so far."""
        return self.roll_count, self._engine.completed_points

    def check_stop(self) -> Optional[GameStopReason]:
        """Return a stop reason if the game should end."""
        if self._config.target_points is not None and self._engine.completed_points >= self._config.target_points:
            return GameStopReason.TARGET_POINTS_REACHED
        if self._config.max_rolls is not None and self.roll_count >= self._config.max_rolls:
            return GameStopReason.MAX_ROLLS_REACHED
        if not self._players_with_bankroll():
            return GameStopReason.NO_BANKROLL_REMAINING
        if self._all_max_win_reached():
            return GameStopReason.ALL_MAX_WIN_REACHED
        if self._only_non_shooter_left():
            return GameStopReason.ONLY_NON_SHOOTER_LEFT
        return None

    def _eligible_players(self) -> Tuple[PlayerState, ...]:
        """Return players who can keep wagering and have not hit max win."""
        eligible: list[PlayerState] = []
        for state in self._player_states:
            if state is None:
                continue
            if state.has_bankroll() and not state.reached_max_win():
                eligible.append(state)
        return tuple(eligible)

    def _players_with_bankroll(self) -> Tuple[PlayerState, ...]:
        """Return players who still have money."""
        remaining: list[PlayerState] = []
        for state in self._player_states:
            if state is None:
                continue
            if state.has_bankroll():
                remaining.append(state)
        return tuple(remaining)

    def _all_max_win_reached(self) -> bool:
        """Return True if all players with bankroll have reached max win targets."""
        players_with_bankroll = self._players_with_bankroll()
        if not players_with_bankroll:
            return False
        for state in players_with_bankroll:
            if state.player.bankroll.max_win is None:
                return False
            if not state.reached_max_win():
                return False
        return True

    def _only_non_shooter_left(self) -> bool:
        """Return True if only one eligible player remains and they cannot shoot."""
        eligible = self._eligible_players()
        return len(eligible) == 1 and not eligible[0].can_shoot

    def _first_shooter_index(self) -> int:
        """Find the first eligible shooter."""
        for seat_index, state in enumerate(self._player_states):
            if state is not None and state.has_bankroll() and state.can_shoot and not state.reached_max_win():
                return seat_index
        raise ValueError("No eligible shooters available")

    def _next_shooter_index(self, current_index: int) -> int:
        """Rotate to the next eligible shooter."""
        for offset in range(1, 10):
            seat_index = (current_index + offset) % 9
            state = self._player_states[seat_index]
            if state is not None and state.has_bankroll() and state.can_shoot and not state.reached_max_win():
                return seat_index
        raise ValueError("No eligible shooters available for rotation")

    @staticmethod
    def _should_rotate_shooter(roll_result: RollResult) -> bool:
        """Rotate shooter on seven-out."""
        return (
            roll_result.phase_before == Phase.POINT_ON
            and roll_result.roll.total == 7
            and roll_result.pass_line_outcome == PassLineOutcome.LOSS
        )
