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
    if snapshot.end_reason is not None:
        lines.append(f"end: {snapshot.end_reason.value}")
        lines.append(f"rolls: {snapshot.roll_count}")
        lines.append(f"points: {snapshot.points_made}")
    return "\n".join(lines).rstrip()


def _render_rows(rows: Iterable[TableRow]) -> list[str]:
    """Render a list of rows using padded columns."""
    rendered = []
    for row in rows:
        values = " | ".join(row.values)
        rendered.append(f"{row.label:<10} {values}")
    return rendered
