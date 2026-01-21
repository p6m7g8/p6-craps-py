"""Craps simulation core package."""

from p6_craps.dice import Dice, Roll
from p6_craps.engine import CrapsEngine, RollResult
from p6_craps.enums import PassLineOutcome, Phase
from p6_craps.game import Game, GameConfig, GameStep, GameStopReason, PlayerState
from p6_craps.models import Bankroll, Player, Table
from p6_craps.stats import StatsSnapshot, TableStatsCollector, percent
from p6_craps.strategy import (
    BetDecision,
    BettingState,
    FlatBetStrategy,
    MartingaleStrategy,
    ParoliStrategy,
)

__all__ = [
    "Bankroll",
    "BetDecision",
    "BettingState",
    "CrapsEngine",
    "Dice",
    "FlatBetStrategy",
    "Game",
    "GameConfig",
    "GameStep",
    "GameStopReason",
    "MartingaleStrategy",
    "PassLineOutcome",
    "Phase",
    "ParoliStrategy",
    "PlayerState",
    "Player",
    "Roll",
    "RollResult",
    "StatsSnapshot",
    "Table",
    "TableStatsCollector",
    "percent",
]
