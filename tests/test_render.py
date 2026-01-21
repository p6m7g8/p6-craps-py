"""Tests for terminal rendering."""

from __future__ import annotations

from p6_craps.dice import Roll
from p6_craps.engine import CrapsEngine
from p6_craps.models import Bankroll, Player, Table
from p6_craps.render import render_stats
from p6_craps.stats import TableStatsCollector


def test_render_includes_sections_and_totals() -> None:
    """Rendered output should include core sections and totals."""
    table = Table.empty().seat_player(0, Player(name="A", bankroll=Bankroll(balance=100)))
    collector = TableStatsCollector()
    collector.record_game_start(table)

    engine = CrapsEngine()
    result = engine.apply_roll(Roll(3, 4))  # 7 on come-out
    collector.record_roll(result, shooter_index=0, roll_count=1, table=table)

    output = render_stats(collector.snapshot())
    assert "[overall]" in output
    assert "totals" in output
    assert "die 1" in output
    assert "die 2" in output
    assert "point est" in output
    assert "[shooter 0]" in output
