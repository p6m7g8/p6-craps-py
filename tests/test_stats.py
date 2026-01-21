"""Tests for stats collection."""

from __future__ import annotations

import pytest

from p6_craps.dice import Roll
from p6_craps.engine import CrapsEngine
from p6_craps.game import GameStopReason
from p6_craps.models import Bankroll, Player, Table
from p6_craps.stats import StatsCounters, TableStatsCollector, percent


def _player(name: str) -> Player:
    return Player(name=name, bankroll=Bankroll(balance=100))


def test_percent_handles_zero_denominator() -> None:
    """Percent should return 0 for empty totals."""
    assert percent(0, 0) == 0.0
    assert percent(5, 0) == 0.0


def test_stats_counters_record_rolls() -> None:
    """StatsCounters should track outcomes, totals, and points."""
    engine = CrapsEngine()
    counters = StatsCounters()

    result = engine.apply_roll(Roll(2, 2))  # point 4
    counters.record(result)
    assert counters.rolls == 1
    assert counters.roll_counts.totals[4] == 1
    assert counters.point_counts.established[4] == 1
    assert counters.outcomes.push == 1

    result = engine.apply_roll(Roll(2, 2))  # hit point 4
    counters.record(result)
    assert counters.rolls == 2
    assert counters.point_counts.made[4] == 1
    assert counters.outcomes.win == 1


def test_table_stats_collector_scopes() -> None:
    """TableStatsCollector should split overall and phase stats."""
    table = Table.empty().seat_player(0, _player("A")).seat_player(1, _player("B"))
    collector = TableStatsCollector()
    collector.record_game_start(table)

    engine = CrapsEngine()
    result = engine.apply_roll(Roll(3, 4))  # come-out 7
    collector.record_roll(result, shooter_index=1, roll_count=1, table=table)

    snapshot = collector.snapshot()
    assert snapshot.overall.rolls == 1
    assert snapshot.come_out.rolls == 1
    assert snapshot.point_on.rolls == 0
    assert snapshot.per_shooter[1].rolls == 1
    assert snapshot.per_player[1].rolls == 1


def test_table_stats_collector_end_reason() -> None:
    """End reason should be captured in snapshot."""
    collector = TableStatsCollector()
    table = Table.empty().seat_player(0, _player("A"))
    collector.record_game_start(table)
    collector.record_game_end(GameStopReason.MAX_ROLLS_REACHED, roll_count=5, points_made=2)
    snapshot = collector.snapshot()
    assert snapshot.end_reason == GameStopReason.MAX_ROLLS_REACHED
    assert snapshot.roll_count == 5
    assert snapshot.points_made == 2


def test_table_stats_collector_rejects_empty_shooter() -> None:
    """Collector should reject rolls from empty shooter seats."""
    table = Table.empty()
    collector = TableStatsCollector()
    collector.record_game_start(table)
    engine = CrapsEngine()
    result = engine.apply_roll(Roll(3, 4))
    with pytest.raises(ValueError, match="Shooter seat"):
        collector.record_roll(result, shooter_index=0, roll_count=1, table=table)
