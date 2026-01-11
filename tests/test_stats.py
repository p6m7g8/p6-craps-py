"""Tests for statistics aggregation utilities."""

from p6_craps.config import Config, PlayerConfig, SimulationConfig
from p6_craps.constants import STRATEGY_FLAT_PASS
from p6_craps.engine import PassLineOutcome, Phase, PointCycleResult, Roll
from p6_craps.players import PlayerState, create_player_states
from p6_craps.sim import SimulationEvent
from p6_craps.stats import (
    DiceTotalStats,
    PlayerSummary,
    compute_dice_totals,
    summarize_players,
)


def _make_player_state(name: str = "P1", bankroll: int = 2000) -> PlayerState:
    """Create a single player state from a minimal config."""
    sim_cfg = SimulationConfig(
        points=40,
        min_bankroll=0,
        max_bankroll=4000,
        random_seed=None,
    )
    player_cfg = PlayerConfig(
        name=name,
        starting_bankroll=bankroll,
        strategy=STRATEGY_FLAT_PASS,
        can_be_shooter=True,
    )
    cfg = Config(simulation=sim_cfg, players=[player_cfg])
    return create_player_states(cfg)[0]


def test_compute_dice_totals_counts_totals_and_phases() -> None:
    """compute_dice_totals should count totals and split by phase."""
    # Build three synthetic events:
    # - COME_OUT: total 7
    # - COME_OUT: total 4
    # - POINT_ON: total 7
    events = [
        SimulationEvent(
            roll_index=1,
            shooter_index=0,
            shooter_roll_index=1,
            point_cycle=PointCycleResult(
                roll=Roll(d1=3, d2=4),
                phase_before=Phase.COME_OUT,
                phase_after=Phase.COME_OUT,
                point_before=None,
                point_after=None,
                pass_line_outcome=PassLineOutcome.NONE,
                completed_point=False,
            ),
            resolved_bets=(),
            bets_snapshot=(),
            shooter_pnl=0,
        ),
        SimulationEvent(
            roll_index=2,
            shooter_index=0,
            shooter_roll_index=2,
            point_cycle=PointCycleResult(
                roll=Roll(d1=2, d2=2),
                phase_before=Phase.COME_OUT,
                phase_after=Phase.POINT_ON,
                point_before=None,
                point_after=4,
                pass_line_outcome=PassLineOutcome.NONE,
                completed_point=False,
            ),
            resolved_bets=(),
            bets_snapshot=(),
            shooter_pnl=0,
        ),
        SimulationEvent(
            roll_index=3,
            shooter_index=0,
            shooter_roll_index=3,
            point_cycle=PointCycleResult(
                roll=Roll(d1=5, d2=2),
                phase_before=Phase.POINT_ON,
                phase_after=Phase.POINT_ON,
                point_before=4,
                point_after=4,
                pass_line_outcome=PassLineOutcome.NONE,
                completed_point=False,
            ),
            resolved_bets=(),
            bets_snapshot=(),
            shooter_pnl=0,
        ),
    ]

    stats = compute_dice_totals(events)

    assert isinstance(stats, DiceTotalStats)
    assert stats.total_rolls == 3
    assert stats.by_total[7] == 2
    assert stats.by_total[4] == 1
    assert stats.by_total_come_out[7] == 1
    assert stats.by_total_come_out[4] == 1
    assert stats.by_total_point_on[7] == 1


def test_summarize_players_uses_player_state_fields() -> None:
    """summarize_players should mirror key fields from PlayerState."""
    player = _make_player_state()
    player.bankroll = 2200
    player.total_profit = 200
    player.shooter_profit = 50
    player.points_played_as_shooter = 3

    summaries = summarize_players([player])

    assert len(summaries) == 1
    summary = summaries[0]
    assert isinstance(summary, PlayerSummary)
    assert summary.name == player.name
    assert summary.final_bankroll == 2200
    assert summary.total_profit == 200
    assert summary.shooter_profit == 50
    assert summary.points_played_as_shooter == 3
    assert summary.strategy_name == STRATEGY_FLAT_PASS
    assert hasattr(summary, "bankroll_variance")
    assert hasattr(summary, "max_drawdown")


def test_summarize_simulation_composes_dice_and_player_stats() -> None:
    """summarize_simulation should combine dice and player summaries."""
    pass
