"""Simulation loop for the craps CLI."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Sequence

from p6_craps.game import Game, GameConfig, PlayerState
from p6_craps.models import Bankroll, Player
from p6_craps.render import render_stats
from p6_craps.stats import TableStatsCollector


@dataclass(slots=True, frozen=True)
class SimulationConfig:
    """Configuration for running a simulation."""

    frame_delay: float = 0.0
    clear: bool = True

    def __post_init__(self) -> None:
        """Validate simulation configuration."""
        if self.frame_delay < 0:
            raise ValueError("frame_delay must be non-negative")


def run_simulation(
    players: Sequence[PlayerState],
    game_config: GameConfig,
    sim_config: SimulationConfig,
) -> int:
    """Run a simulation until stop conditions are met."""
    stats = TableStatsCollector()
    game = Game.from_players(players=tuple(players), config=game_config, stats=stats)
    while True:
        step = game.step()
        _render_frame(stats, clear=sim_config.clear)
        if step.stop_reason is not None:
            return 0
        if sim_config.frame_delay:
            time.sleep(sim_config.frame_delay)


def default_players() -> tuple[PlayerState, ...]:
    """Create default players for CLI usage."""
    players = [
        PlayerState(player=Player(name="Shooter", bankroll=Bankroll(balance=1000))),
        PlayerState(player=Player(name="Player 2", bankroll=Bankroll(balance=1000))),
    ]
    return tuple(players)


def _render_frame(stats: TableStatsCollector, clear: bool) -> None:
    """Render a single stats frame to stdout."""
    if clear:
        print("\033[2J\033[H", end="")
    snapshot = stats.snapshot()
    print(render_stats(snapshot))
