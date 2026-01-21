"""Simulation loop for the craps CLI."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence

from p6_craps.enums import PassLineOutcome, Phase
from p6_craps.game import Game, GameConfig, PlayerState
from p6_craps.models import Bankroll, Player
from p6_craps.render import render_stats
from p6_craps.stats import TableStatsCollector
from p6_craps.strategy import (
    BetDecision,
    BettingState,
    BettingStrategy,
    FlatBetStrategy,
    MartingaleStrategy,
    ParoliStrategy,
)


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


def players_from_config(config: Mapping[str, Any]) -> tuple[PlayerState, ...]:
    """Build player states from configuration."""
    entries = config.get("players")
    if not entries:
        return default_players()
    if not isinstance(entries, list):
        raise ValueError("players must be a list")
    if len(entries) > 9:
        raise ValueError("players cannot exceed 9 seats")
    players: list[PlayerState] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("player entries must be objects")
        name = str(entry.get("name") or "").strip()
        if not name:
            raise ValueError("player name is required")
        bankroll = _require_int(entry.get("bankroll"), "bankroll", minimum=0)
        max_win = entry.get("max_win")
        if max_win is not None:
            max_win = _require_int(max_win, "max_win", minimum=1)
        can_shoot = bool(entry.get("can_shoot", True))
        base_bet = _require_int(entry.get("base_bet", 5), "base_bet", minimum=1)
        max_bet = entry.get("max_bet")
        if max_bet is not None:
            max_bet = _require_int(max_bet, "max_bet", minimum=1)
        strategy = _strategy_from_name(entry.get("strategy"))
        players.append(
            PlayerState(
                player=Player(name=name, bankroll=Bankroll(balance=bankroll, max_win=max_win)),
                can_shoot=can_shoot,
                strategy=strategy,
                base_bet=base_bet,
                max_bet=max_bet,
            )
        )
    return tuple(players)


def game_config_from_config(config: Mapping[str, Any], max_rolls: int | None) -> GameConfig:
    """Build game config with CLI overrides."""
    target_points = config.get("target_points")
    if target_points is not None:
        target_points = _require_int(target_points, "target_points", minimum=1)
    resolved_max_rolls = max_rolls
    if resolved_max_rolls is None and "max_rolls" in config:
        resolved_max_rolls = _require_int(config.get("max_rolls"), "max_rolls", minimum=1)
    return GameConfig(target_points=target_points, max_rolls=resolved_max_rolls)


def simulation_config_from_config(
    config: Mapping[str, Any],
    frame_delay: float,
    clear: bool,
) -> SimulationConfig:
    """Build simulation config with CLI overrides."""
    resolved_delay = frame_delay
    if "frame_delay" in config and frame_delay == 0.0:
        resolved_delay = float(config.get("frame_delay") or 0.0)
    resolved_clear = clear
    if "clear" in config:
        resolved_clear = bool(config.get("clear"))
    return SimulationConfig(frame_delay=resolved_delay, clear=resolved_clear)


def _render_frame(stats: TableStatsCollector, clear: bool) -> None:
    """Render a single stats frame to stdout."""
    if clear:
        print("\033[2J\033[H", end="")
    snapshot = stats.snapshot()
    print(render_stats(snapshot))


def _strategy_from_name(name: Any) -> BettingStrategy:
    """Resolve a strategy name to a strategy instance."""
    if name is None:
        return FlatBetStrategy()
    value = str(name).strip().lower()
    if value in {"flat", "flat_bet", "flatbet"}:
        return FlatBetStrategy()
    if value in {"martingale"}:
        return MartingaleStrategy()
    if value in {"paroli"}:
        return ParoliStrategy()
    raise ValueError(f"Unknown strategy {name!r}")


def _require_int(value: Any, label: str, minimum: int) -> int:
    """Return an int >= minimum or raise."""
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be an integer") from exc
    if parsed < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return parsed


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
