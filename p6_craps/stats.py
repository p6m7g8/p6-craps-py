"""Statistics collection for craps game simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from p6_craps.dice import Roll
from p6_craps.engine import RollResult
from p6_craps.enums import PassLineOutcome, Phase
from p6_craps.game import GameStopReason, StatsCollector
from p6_craps.models import Table

POINT_NUMBERS = (4, 5, 6, 8, 9, 10)


def percent(numerator: int, denominator: int) -> float:
    """Return a percentage for a count."""
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) * 100.0


@dataclass(slots=True)
class OutcomeCounts:
    """Counts for pass line outcomes."""

    win: int = 0
    loss: int = 0
    push: int = 0

    def record(self, outcome: PassLineOutcome) -> None:
        """Record a pass line outcome."""
        if outcome == PassLineOutcome.WIN:
            self.win += 1
        elif outcome == PassLineOutcome.LOSS:
            self.loss += 1
        else:
            self.push += 1

    def as_percentages(self, total: int) -> Dict[str, float]:
        """Return outcome percentages."""
        return {
            "win": percent(self.win, total),
            "loss": percent(self.loss, total),
            "push": percent(self.push, total),
        }


@dataclass(slots=True)
class RollCounts:
    """Counts for roll totals and individual dice."""

    totals: Dict[int, int] = field(default_factory=lambda: {total: 0 for total in range(2, 13)})
    die_one: Dict[int, int] = field(default_factory=lambda: {pip: 0 for pip in range(1, 7)})
    die_two: Dict[int, int] = field(default_factory=lambda: {pip: 0 for pip in range(1, 7)})

    def record(self, roll: Roll) -> None:
        """Record a roll total and pip counts."""
        self.totals[roll.total] += 1
        self.die_one[roll.d1] += 1
        self.die_two[roll.d2] += 1


@dataclass(slots=True)
class PointCounts:
    """Counts for points established and made."""

    established: Dict[int, int] = field(default_factory=lambda: {point: 0 for point in POINT_NUMBERS})
    made: Dict[int, int] = field(default_factory=lambda: {point: 0 for point in POINT_NUMBERS})

    def record_established(self, point: int) -> None:
        """Record a point being established."""
        if point in self.established:
            self.established[point] += 1

    def record_made(self, point: int) -> None:
        """Record a point being made."""
        if point in self.made:
            self.made[point] += 1


@dataclass(slots=True)
class StatsCounters:
    """Aggregate stats for a scope of play."""

    rolls: int = 0
    outcomes: OutcomeCounts = field(default_factory=OutcomeCounts)
    roll_counts: RollCounts = field(default_factory=RollCounts)
    point_counts: PointCounts = field(default_factory=PointCounts)

    def record(self, roll_result: RollResult) -> None:
        """Record a roll result into the counters."""
        self.rolls += 1
        self.outcomes.record(roll_result.pass_line_outcome)
        self.roll_counts.record(roll_result.roll)

        if roll_result.phase_before == Phase.COME_OUT and roll_result.pass_line_outcome == PassLineOutcome.PUSH:
            if roll_result.point_after is not None:
                self.point_counts.record_established(roll_result.point_after)

        if roll_result.phase_before == Phase.POINT_ON and roll_result.pass_line_outcome == PassLineOutcome.WIN:
            if roll_result.point_before is not None:
                self.point_counts.record_made(roll_result.point_before)


@dataclass(slots=True)
class StatsSnapshot:
    """Snapshot of collected stats for reporting."""

    overall: StatsCounters
    come_out: StatsCounters
    point_on: StatsCounters
    per_shooter: Dict[int, StatsCounters]
    per_player: Dict[int, StatsCounters]
    end_reason: Optional[GameStopReason] = None
    roll_count: int = 0
    points_made: int = 0


class TableStatsCollector(StatsCollector):
    """Collect stats by phase and shooter for a game table."""

    def __init__(self) -> None:
        """Initialize stats containers."""
        self._overall = StatsCounters()
        self._come_out = StatsCounters()
        self._point_on = StatsCounters()
        self._per_shooter: Dict[int, StatsCounters] = {}
        self._per_player: Dict[int, StatsCounters] = {}
        self._end_reason: Optional[GameStopReason] = None
        self._roll_count = 0
        self._points_made = 0

    def record_game_start(self, table: Table) -> None:
        """Initialize per-seat stats."""
        for seat_index, seat in enumerate(table.seats):
            if seat is None:
                continue
            self._per_player[seat_index] = StatsCounters()
            self._per_shooter[seat_index] = StatsCounters()

    def record_roll(self, roll_result: RollResult, shooter_index: int, roll_count: int, table: Table) -> None:
        """Record a single roll and update per-scope stats."""
        if table.seats[shooter_index] is None:
            raise ValueError("Shooter seat is empty")

        self._roll_count = roll_count
        self._overall.record(roll_result)

        if roll_result.phase_before == Phase.COME_OUT:
            self._come_out.record(roll_result)
        else:
            self._point_on.record(roll_result)

        if shooter_index not in self._per_shooter:
            self._per_shooter[shooter_index] = StatsCounters()
        self._per_shooter[shooter_index].record(roll_result)

        if shooter_index not in self._per_player:
            self._per_player[shooter_index] = StatsCounters()
        self._per_player[shooter_index].record(roll_result)

    def record_game_end(self, reason: GameStopReason, roll_count: int, points_made: int) -> None:
        """Record the game end reason and totals."""
        self._end_reason = reason
        self._roll_count = roll_count
        self._points_made = points_made

    def snapshot(self) -> StatsSnapshot:
        """Return a snapshot of current stats."""
        return StatsSnapshot(
            overall=self._overall,
            come_out=self._come_out,
            point_on=self._point_on,
            per_shooter=dict(self._per_shooter),
            per_player=dict(self._per_player),
            end_reason=self._end_reason,
            roll_count=self._roll_count,
            points_made=self._points_made,
        )
