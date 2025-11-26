"""Statistics aggregation utilities for the craps simulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from .engine import Phase
from .players import PlayerState
from .sim import SimulationEvent, SimulationResult


@dataclass(slots=True)
class DiceTotalStats:
    """Aggregate counts of dice totals during a simulation."""

    total_rolls: int
    by_total: Dict[int, int]
    by_total_come_out: Dict[int, int]
    by_total_point_on: Dict[int, int]


@dataclass(slots=True)
class PlayerSummary:
    """Final per-player summary for a simulation run."""

    name: str
    final_bankroll: int
    total_profit: int
    shooter_profit: int
    points_played_as_shooter: int
    strategy_name: str
    bankroll_variance: float
    max_drawdown: int


@dataclass(slots=True)
class SimulationSummary:
    """High-level summary of a simulation run."""

    stop_reason: str
    completed_points: int
    dice: DiceTotalStats
    players: List[PlayerSummary]


def compute_dice_totals(events: Sequence[SimulationEvent]) -> DiceTotalStats:
    """Compute aggregated dice totals split by phase."""
    totals_range = range(2, 13)
    by_total: Dict[int, int] = {total: 0 for total in totals_range}
    by_total_come_out: Dict[int, int] = {total: 0 for total in totals_range}
    by_total_point_on: Dict[int, int] = {total: 0 for total in totals_range}

    total_rolls = 0

    for event in events:
        roll_total = event.point_cycle.roll.total
        if roll_total < 2 or roll_total > 12:
            continue

        total_rolls += 1
        by_total[roll_total] += 1

        phase_before = event.point_cycle.phase_before
        if phase_before is Phase.COME_OUT:
            by_total_come_out[roll_total] += 1
        elif phase_before is Phase.POINT_ON:
            by_total_point_on[roll_total] += 1

    return DiceTotalStats(
        total_rolls=total_rolls,
        by_total=by_total,
        by_total_come_out=by_total_come_out,
        by_total_point_on=by_total_point_on,
    )



def compute_bankroll_stats(events: Sequence[SimulationEvent], starting_bankroll: int) -> tuple[float, int]:
    """Compute bankroll variance and max drawdown for a player from simulation events (stub)."""
    # Placeholder: variance 0, drawdown 0
    return 0.0, 0

def summarize_players(players: Sequence[PlayerState], events: Sequence[SimulationEvent] = None) -> List[PlayerSummary]:
    """Build final per-player summaries from runtime state and events."""
    summaries: List[PlayerSummary] = []

    # If events are provided, compute stats; else, set to 0/0
    for player in players:
        if events is not None:
            variance, drawdown = compute_bankroll_stats(events, player.config.starting_bankroll)
        else:
            variance, drawdown = 0.0, 0
        summaries.append(
            PlayerSummary(
                name=player.name,
                final_bankroll=player.bankroll,
                total_profit=player.total_profit,
                shooter_profit=player.shooter_profit,
                points_played_as_shooter=player.points_played_as_shooter,
                strategy_name=player.strategy_name,
                bankroll_variance=variance,
                max_drawdown=drawdown,
            )
        )

    return summaries


def summarize_simulation(
    players: Sequence[PlayerState],
    result: SimulationResult,
) -> SimulationSummary:
    """Summarize a simulation result into high-level stats."""
    dice_stats = compute_dice_totals(result.events)
    player_summaries = summarize_players(players)

    return SimulationSummary(
        stop_reason=result.stop_reason,
        completed_points=result.completed_points,
        dice=dice_stats,
        players=player_summaries,
    )
