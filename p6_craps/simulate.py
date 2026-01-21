"""Simulation loop for the craps CLI."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Sequence

from p6_craps.enums import PassLineOutcome, Phase
from p6_craps.game import Game, GameConfig, PlayerState
from p6_craps.models import Bankroll, Player
from p6_craps.render import render_stats
from p6_craps.stats import TableStatsCollector
from p6_craps.strategy import BetDecision, BettingState


@dataclass(slots=True, frozen=True)
class SimulationConfig:
    """Configuration for running a simulation."""

    frame_delay: float = 0.0
    clear: bool = True

    def __post_init__(self) -> None:
        """Validate simulation configuration."""
        if self.frame_delay < 0:
            raise ValueError("frame_delay must be non-negative")


@dataclass(slots=True)
class BettingTracker:
    """Track an active bet and strategy state."""

    state: BettingState
    active_bet: int = 0


def run_simulation(
    players: Sequence[PlayerState],
    game_config: GameConfig,
    sim_config: SimulationConfig,
) -> int:
    """Run a simulation until stop conditions are met."""
    stats = TableStatsCollector()
    game = Game.from_players(players=tuple(players), config=game_config, stats=stats)
    trackers = _init_trackers(game.player_states())
    while True:
        _place_bets(game, trackers)
        step = game.step()
        _settle_bets(game, trackers, step.roll_result.pass_line_outcome)
        _render_frame(stats, clear=sim_config.clear)
        if step.stop_reason is not None:
            return 0
        if sim_config.frame_delay:
            time.sleep(sim_config.frame_delay)


def run_until_complete(
    players: Sequence[PlayerState],
    game_config: GameConfig,
) -> tuple[int, int]:
    """Run a simulation without rendering; return roll count and points made."""
    stats = TableStatsCollector()
    game = Game.from_players(players=tuple(players), config=game_config, stats=stats)
    trackers = _init_trackers(game.player_states())
    while True:
        _place_bets(game, trackers)
        step = game.step()
        _settle_bets(game, trackers, step.roll_result.pass_line_outcome)
        if step.stop_reason is not None:
            return game.snapshot()


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


def _init_trackers(players: Sequence[PlayerState | None]) -> Dict[int, BettingTracker]:
    """Initialize betting trackers for each seat."""
    trackers: Dict[int, BettingTracker] = {}
    for seat_index, state in enumerate(players):
        if state is None:
            continue
        trackers[seat_index] = BettingTracker(
            state=BettingState(
                bankroll=state.player.bankroll.balance,
                base_bet=state.base_bet,
                max_bet=state.max_bet,
            ),
        )
    return trackers


def _place_bets(game: Game, trackers: Dict[int, BettingTracker]) -> None:
    """Place bets for a new come-out roll."""
    if game.phase != Phase.COME_OUT:
        return
    for seat_index, state in enumerate(game.player_states()):
        if state is None:
            continue
        tracker = trackers.get(seat_index)
        if tracker is None:
            continue
        if tracker.active_bet > 0:
            continue
        if not state.has_bankroll() or state.reached_max_win():
            continue
        decision = state.strategy.next_bet(tracker.state)
        amount = _cap_bet(decision, tracker.state.bankroll)
        tracker.active_bet = amount


def _settle_bets(game: Game, trackers: Dict[int, BettingTracker], outcome: PassLineOutcome) -> None:
    """Settle active bets when a pass line outcome resolves."""
    if outcome == PassLineOutcome.PUSH:
        return
    for seat_index, state in enumerate(game.player_states()):
        if state is None:
            continue
        tracker = trackers.get(seat_index)
        if tracker is None or tracker.active_bet <= 0:
            continue
        delta = tracker.active_bet if outcome == PassLineOutcome.WIN else -tracker.active_bet
        updated_bankroll = state.player.bankroll.apply(delta)
        updated_player = Player(name=state.player.name, bankroll=updated_bankroll)
        updated_state = PlayerState(
            player=updated_player,
            can_shoot=state.can_shoot,
            strategy=state.strategy,
            base_bet=state.base_bet,
            max_bet=state.max_bet,
        )
        game.update_player_state(seat_index, updated_state)
        tracker.state = _update_betting_state(tracker.state, updated_bankroll.balance, outcome)
        tracker.active_bet = 0


def _cap_bet(decision: BetDecision, bankroll: int) -> int:
    """Cap bet decisions to available bankroll."""
    if decision.amount <= 0 or bankroll <= 0:
        return 0
    return min(decision.amount, bankroll)


def _update_betting_state(
    state: BettingState,
    bankroll: int,
    outcome: PassLineOutcome,
) -> BettingState:
    """Update betting state after an outcome resolves."""
    if outcome == PassLineOutcome.WIN:
        wins = state.consecutive_wins + 1
        losses = 0
    else:
        wins = 0
        losses = state.consecutive_losses + 1
    return BettingState(
        bankroll=bankroll,
        base_bet=state.base_bet,
        max_bet=state.max_bet,
        consecutive_wins=wins,
        consecutive_losses=losses,
        last_outcome=outcome,
    )
