"""Terminal-based UI for rendering the craps simulation in real time.

This module provides a simple, testable renderer that can turn the
current simulation state into a human-readable table. The CLI is
responsible for driving the simulation, calling these functions in a
loop, and keeping the final frame on screen at the end.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, TextIO

from ..engine import CrapsEngine, CrapsTable, Phase
from ..players import PlayerState


@dataclass(slots=True)
class PlayerRow:
    """Snapshot of a single player's state for display."""

    name: str
    bankroll: int
    total_profit: int
    shooter_profit: int
    on_table: int
    is_shooter: bool
    strategy_name: str


@dataclass(slots=True)
class HeaderInfo:
    """Summary information for the current roll and shooter."""

    roll_index: int
    shooter_index: int
    shooter_roll_index: int
    phase: Phase
    point: Optional[int]


def _calc_on_table_for_player(table: CrapsTable, player_index: int) -> int:
    """Return the total amount currently on the table for a player."""
    total = 0
    for bet in table.bets:
        if bet.player_index == player_index and bet.working:
            total += bet.total_wagered
    return total


def snapshot_players(players: Sequence[PlayerState], table: CrapsTable) -> List[PlayerRow]:
    """Build a list of :class:`PlayerRow` snapshots from current state."""
    rows: List[PlayerRow] = []

    for index, player in enumerate(players):
        on_table = _calc_on_table_for_player(table, index)
        rows.append(
            PlayerRow(
                name=player.name,
                bankroll=player.bankroll,
                total_profit=player.total_profit,
                shooter_profit=player.shooter_profit,
                on_table=on_table,
                is_shooter=player.is_current_shooter,
                strategy_name=player.strategy_name,
            )
        )

    return rows


def build_header_info(
    engine: CrapsEngine,
    roll_index: int,
    shooter_index: int,
    shooter_roll_index: int,
) -> HeaderInfo:
    """Construct :class:`HeaderInfo` from the engine and roll counters."""
    return HeaderInfo(
        roll_index=roll_index,
        shooter_index=shooter_index,
        shooter_roll_index=shooter_roll_index,
        phase=engine.phase,
        point=engine.point,
    )


def format_header(header: HeaderInfo) -> str:
    """Format a textual header block for the current roll."""
    phase_label = header.phase.name
    point_label = "-" if header.point is None else str(header.point)

    line1 = (
        f"Roll {header.roll_index} " f"(Shooter {header.shooter_index}, " f"Shooter roll {header.shooter_roll_index})"
    )
    line2 = f"Phase: {phase_label}  Point: {point_label}"
    underline = "-" * max(len(line1), len(line2))

    return "\n".join([line1, line2, underline])


def format_player_table(rows: Sequence[PlayerRow]) -> str:
    """Format the per-player table as a multi-line string."""
    if not rows:
        return "No players configured."

    headers = ("Player", "Bankroll", "Profit", "Shooter P&L", "On Table", "Shooter", "Strategy")
    widths = (16, 10, 10, 13, 10, 8, 16)

    header_line = (
        f"{headers[0]:<{widths[0]}} "
        f"{headers[1]:>{widths[1]}} "
        f"{headers[2]:>{widths[2]}} "
        f"{headers[3]:>{widths[3]}} "
        f"{headers[4]:>{widths[4]}} "
        f"{headers[5]:^{widths[5]}} "
        f"{headers[6]:<{widths[6]}}"
    )
    underline = "-" * len(header_line)

    lines = [header_line, underline]

    for row in rows:
        shooter_flag = "Y" if row.is_shooter else ""
        lines.append(
            f"{row.name:<{widths[0]}} "
            f"{row.bankroll:>{widths[1]}} "
            f"{row.total_profit:>{widths[2]}} "
            f"{row.shooter_profit:>{widths[3]}} "
            f"{row.on_table:>{widths[4]}} "
            f"{shooter_flag:^{widths[5]}} "
            f"{row.strategy_name:<{widths[6]}}"
        )

    return "\n".join(lines)


def render_frame(header: HeaderInfo, player_rows: Sequence[PlayerRow]) -> str:
    """Render a full frame combining header and player table."""
    header_block = format_header(header)
    table_block = format_player_table(player_rows)
    return f"{header_block}\n\n{table_block}\n"


def draw_frame(stream: TextIO, frame: str, clear: bool = True) -> None:
    """Write the rendered frame to the provided stream.

    Args:
        stream: A text stream to write to, typically ``sys.stdout``.
        clear: If True, emit an ANSI clear-screen sequence before the
            frame so that the display appears to auto-refresh in place.
    """
    if clear:
        stream.write("\x1b[2J\x1b[H")
    stream.write(frame)
    stream.flush()
