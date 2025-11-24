"""Tests for the simulation loop and stop conditions."""

from p6_craps.config import Config, PlayerConfig, SimulationConfig
from p6_craps.engine import (
    CrapsEngine,
    CrapsTable,
    PassLineOutcome,
    PointCycleResult,
    Roll,
)
from p6_craps.sim import (
    STOP_REASON_BANKROLL,
    STOP_REASON_MAX_POINTS,
    STOP_REASON_MAX_ROLLS,
    Simulation,
)
from p6_craps.strategy import STRATEGY_FLAT_PASS


class StubEngine(CrapsEngine):
    """Stub engine that completes a point on every roll."""

    def __init__(self) -> None:
        super().__init__(rng=None)

    def roll(self) -> PointCycleResult:  # type: ignore[override]
        """Return a deterministic point-cycle result with a completed point."""
        roll = Roll(d1=1, d2=1)
        self.completed_points += 1
        return PointCycleResult(
            roll=roll,
            phase_before=self.phase,
            phase_after=self.phase,
            point_before=self.point,
            point_after=self.point,
            pass_line_outcome=PassLineOutcome.NONE,
            completed_point=True,
        )


def _make_config(points: int = 2) -> Config:
    """Create a simple config with a single flat-pass player."""
    sim_cfg = SimulationConfig(
        points=points,
        min_bankroll=0,
        max_bankroll=10_000,
        random_seed=None,
    )
    player_cfg = PlayerConfig(
        name="P1",
        starting_bankroll=200,
        strategy=STRATEGY_FLAT_PASS,
        can_be_shooter=True,
    )
    return Config(simulation=sim_cfg, players=[player_cfg])


def test_simulation_stops_when_max_points_reached() -> None:
    """Simulation stops due to reaching the configured number of points."""
    cfg = _make_config(points=3)
    engine = StubEngine()
    table = CrapsTable()

    sim = Simulation(cfg, engine=engine, table=table)
    result = sim.run(max_rolls=10)

    assert result.stop_reason == STOP_REASON_MAX_POINTS
    assert result.completed_points == cfg.simulation.points
    assert len(result.events) == cfg.simulation.points


def test_simulation_stops_immediately_when_bankroll_limits_met() -> None:
    """Simulation stops immediately if all players are already at limits."""
    cfg = _make_config(points=10)
    sim = Simulation(cfg)

    # Force the only player to be at the global minimum bankroll.
    sim.players[0].bankroll = cfg.simulation.min_bankroll

    result = sim.run(max_rolls=5)

    assert result.stop_reason == STOP_REASON_BANKROLL
    assert result.completed_points == 0
    assert not result.events


def test_simulation_respects_max_rolls_guard() -> None:
    """Simulation stops with max-rolls reason when the guard is hit first."""
    cfg = _make_config(points=100)
    engine = StubEngine()
    table = CrapsTable()

    sim = Simulation(cfg, engine=engine, table=table)
    result = sim.run(max_rolls=5)

    assert result.stop_reason == STOP_REASON_MAX_ROLLS
    assert result.completed_points == 5
    assert len(result.events) == 5
