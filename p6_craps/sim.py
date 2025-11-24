"""Simulation orchestration for the craps simulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from .config import Config
from .constants import (
    ACTION_PLACE,
    BET_TYPE_PASS_LINE,
    GAME_STATE_HAS_PASS_LINE_BET,
    GAME_STATE_PHASE,
    STOP_REASON_BANKROLL,
    STOP_REASON_MAX_POINTS,
    STOP_REASON_MAX_ROLLS,
)
from .engine import Bet, CrapsEngine, CrapsTable, PointCycleResult, ResolvedBet
from .players import PlayerState, create_player_states
from .strategy import BetDecision, Strategy, get_strategy_by_name


@dataclass(slots=True)
class SimulationEvent:
    """A single roll event recorded during a simulation."""

    roll_index: int
    shooter_index: int
    shooter_roll_index: int
    point_cycle: PointCycleResult
    resolved_bets: Sequence[ResolvedBet]


@dataclass(slots=True)
class SimulationResult:
    """Final outcome of a simulation run."""

    events: Sequence[SimulationEvent]
    completed_points: int
    stop_reason: str


class Simulation:
    """Orchestrate a craps simulation for configured players and limits."""

    def __init__(
        self,
        cfg: Config,
        engine: Optional[CrapsEngine] = None,
        table: Optional[CrapsTable] = None,
    ) -> None:
        """Initialize the simulation with configuration and core components."""
        self._cfg = cfg
        self.engine: CrapsEngine = engine or CrapsEngine()
        self.table: CrapsTable = table or CrapsTable()
        self.players: List[PlayerState] = create_player_states(cfg)
        self._strategies: List[Strategy] = [get_strategy_by_name(player.config.strategy) for player in self.players]

        self._current_shooter_index: int = self._select_initial_shooter()
        self.players[self._current_shooter_index].is_current_shooter = True

        self._roll_index: int = 0
        self._shooter_roll_index: int = 0

    def _select_initial_shooter(self) -> int:
        """Return the index of the first eligible shooter."""
        for index, player in enumerate(self.players):
            if player.can_be_shooter:
                return index
        return 0

    def _advance_shooter(self) -> None:
        """Rotate the shooter to the next eligible player."""
        num_players = len(self.players)
        current = self._current_shooter_index
        self.players[current].is_current_shooter = False

        for offset in range(1, num_players + 1):
            candidate = (current + offset) % num_players
            if self.players[candidate].can_be_shooter:
                self._current_shooter_index = candidate
                self.players[candidate].is_current_shooter = True
                break

        self._shooter_roll_index = 0

    def _player_at_global_limits(self, player: PlayerState) -> bool:
        """Return True if the player has reached global bankroll limits."""
        sim_cfg = self._cfg.simulation
        if player.bankroll <= sim_cfg.min_bankroll:
            return True
        if player.bankroll >= sim_cfg.max_bankroll:
            return True
        return False

    def _all_players_at_limits(self) -> bool:
        """Return True if every player is at the global bankroll limits."""
        return all(self._player_at_global_limits(player) for player in self.players)

    def _should_stop(self) -> Optional[str]:
        """Return a stop reason if the simulation should end, else None."""
        if self.engine.completed_points >= self._cfg.simulation.points:
            return STOP_REASON_MAX_POINTS
        if self._all_players_at_limits():
            return STOP_REASON_BANKROLL
        return None

    def _apply_bet_decisions(
        self,
        decisions: Sequence[BetDecision],
        player_index: int,
        player_state: PlayerState,
    ) -> None:
        """Apply bet decisions for a single player."""
        for decision in decisions:
            if decision.action != ACTION_PLACE:
                continue

            if decision.bet_type == BET_TYPE_PASS_LINE:
                amount = decision.amount
                if amount <= 0 or player_state.bankroll < amount:
                    continue

                player_state.debit(amount)
                self.table.place_bet(
                    Bet(
                        player_index=player_index,
                        bet_type=decision.bet_type,
                        base_amount=amount,
                    )
                )

    def run(self, max_rolls: Optional[int] = None) -> SimulationResult:
        """Run the simulation until points, bankroll limits, or max rolls are reached."""
        events: List[SimulationEvent] = []

        # Immediate stop check before any rolls.
        initial_reason = self._should_stop()
        if initial_reason is not None:
            return SimulationResult(
                events=tuple(events),
                completed_points=self.engine.completed_points,
                stop_reason=initial_reason,
            )

        stop_reason: Optional[str] = None

        while True:
            # Max-rolls guard before taking another roll.
            if max_rolls is not None and self._roll_index >= max_rolls:
                stop_reason = STOP_REASON_MAX_ROLLS
                break

            # Let each player act according to their strategy.
            for index, (player, strategy) in enumerate(zip(self.players, self._strategies)):
                if self._player_at_global_limits(player):
                    continue

                game_state = {
                    GAME_STATE_PHASE: self.engine.phase,
                    GAME_STATE_HAS_PASS_LINE_BET: self.table.has_pass_line_bet(index),
                }
                decisions = strategy.decide(game_state, player)
                self._apply_bet_decisions(decisions, index, player)

            # Perform a roll.
            self._roll_index += 1
            self._shooter_roll_index += 1

            point_cycle: PointCycleResult = self.engine.roll()
            resolved_bets: List[ResolvedBet] = self.table.resolve_on_point_cycle_result(point_cycle)

            # Apply payouts to player bankrolls.
            for resolved in resolved_bets:
                player = self.players[resolved.bet.player_index]
                if resolved.payout > 0:
                    player.credit(resolved.payout)

            # Handle shooter rotation on completed point cycles.
            if point_cycle.completed_point:
                self.players[self._current_shooter_index].points_played_as_shooter += 1
                self._advance_shooter()

            events.append(
                SimulationEvent(
                    roll_index=self._roll_index,
                    shooter_index=self._current_shooter_index,
                    shooter_roll_index=self._shooter_roll_index,
                    point_cycle=point_cycle,
                    resolved_bets=tuple(resolved_bets),
                )
            )

            stop_reason = self._should_stop()
            if stop_reason is not None:
                break

        # Fallback (should not be hit, but keeps type checkers happy).
        if stop_reason is None:
            stop_reason = STOP_REASON_MAX_POINTS

        return SimulationResult(
            events=tuple(events),
            completed_points=self.engine.completed_points,
            stop_reason=stop_reason,
        )
