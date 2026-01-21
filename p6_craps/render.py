"""Terminal rendering for craps stats."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from p6_craps.stats import StatsCounters, StatsSnapshot, percent


@dataclass(slots=True, frozen=True)
class TableRow:
    """Single row of a rendered table."""

    label: str
    values: Sequence[str]


def _format_percent(numerator: int, denominator: int) -> str:
    """Format a percentage string."""
    return f"{percent(numerator, denominator):6.2f}%"


def _format_counts(counters: StatsCounters) -> list[TableRow]:
    """Format roll/outcome counts into table rows."""
    total_rolls = counters.rolls
    return [
        TableRow("rolls", [str(total_rolls)]),
        TableRow(
            "wins",
            [f"{counters.outcomes.win} ({_format_percent(counters.outcomes.win, total_rolls)})"],
        ),
        TableRow(
            "losses",
            [f"{counters.outcomes.loss} ({_format_percent(counters.outcomes.loss, total_rolls)})"],
        ),
        TableRow(
            "pushes",
            [f"{counters.outcomes.push} ({_format_percent(counters.outcomes.push, total_rolls)})"],
        ),
        TableRow("totals", [_format_totals(counters.roll_counts.totals)]),
        TableRow("die 1", [_format_totals(counters.roll_counts.die_one)]),
        TableRow("die 2", [_format_totals(counters.roll_counts.die_two)]),
        TableRow("point est", [_format_totals(counters.point_counts.established)]),
        TableRow("point made", [_format_totals(counters.point_counts.made)]),
    ]


def render_stats(snapshot: StatsSnapshot) -> str:
    """Render a stats snapshot as a human-readable table string."""
    sections = [
        ("overall", snapshot.overall),
        ("come-out", snapshot.come_out),
        ("point-on", snapshot.point_on),
    ]
    lines: list[str] = []
    for title, counters in sections:
        lines.append(f"[{title}]")
        lines.extend(_render_rows(_format_counts(counters)))
        lines.append("")

    lines.extend(_render_scoped("shooter", snapshot.per_shooter))
    lines.extend(_render_scoped("player", snapshot.per_player))
    if snapshot.end_reason is not None:
        lines.append(f"end: {snapshot.end_reason.value}")
        lines.append(f"rolls: {snapshot.roll_count}")
        lines.append(f"points: {snapshot.points_made}")
    return "\n".join(lines).rstrip()


def _format_totals(values: dict[int, int]) -> str:
    """Format counts as key=value pairs."""
    return " ".join(f"{key}={values[key]}" for key in sorted(values))


def _render_scoped(label: str, scoped: dict[int, StatsCounters]) -> list[str]:
    """Render per-seat scoped stats sections."""
    lines: list[str] = []
    for seat_index in sorted(scoped):
        lines.append(f"[{label} {seat_index}]")
        lines.extend(_render_rows(_format_counts(scoped[seat_index])))
        lines.append("")
    return lines


def _render_rows(rows: Iterable[TableRow]) -> list[str]:
    """Render a list of rows using padded columns."""
    rendered = []
    for row in rows:
        values = " | ".join(row.values)
        rendered.append(f"{row.label:<10} {values}")
    return rendered
