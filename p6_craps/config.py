from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigError(Exception):
    """Raised when the craps simulator configuration is invalid."""


@dataclass(slots=True)
class PlayerConfig:
    """Static configuration for a single simulated player."""

    name: str
    starting_bankroll: int
    strategy: str
    can_be_shooter: bool = True
    min_bankroll: Optional[int] = None
    max_bankroll: Optional[int] = None


@dataclass(slots=True)
class SimulationConfig:
    """Global simulation parameters."""

    points: int
    min_bankroll: int
    max_bankroll: int
    random_seed: Optional[int] = None


@dataclass(slots=True)
class Config:
    """Top-level configuration for a craps simulation run."""

    simulation: SimulationConfig
    players: List[PlayerConfig]


def _require_key(mapping: Dict[str, Any], key: str, ctx: str) -> Any:
    try:
        return mapping[key]
    except KeyError as exc:
        raise ConfigError(f"Missing key '{key}' in {ctx}") from exc


def load_config(path: str | Path = "config.json") -> Config:
    """
    Load and validate the craps simulator configuration.

    The default path is ``config.json`` in the current working directory.
    """
    file_path = Path(path)

    if not file_path.is_file():
        raise ConfigError(f"Config file not found: {file_path}")

    try:
        raw: Dict[str, Any] = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config file {file_path}") from exc

    simulation_raw = _require_key(raw, "simulation", "config root")
    players_raw = _require_key(raw, "players", "config root")

    if not isinstance(players_raw, list) or not players_raw:
        raise ConfigError("Config must define at least one player.")

    simulation = SimulationConfig(
        points=int(_require_key(simulation_raw, "points", "simulation")),
        min_bankroll=int(_require_key(simulation_raw, "min_bankroll", "simulation")),
        max_bankroll=int(_require_key(simulation_raw, "max_bankroll", "simulation")),
        random_seed=simulation_raw.get("random_seed"),
    )

    players: List[PlayerConfig] = []
    for index, player_raw in enumerate(players_raw):
        ctx = f"players[{index}]"
        if not isinstance(player_raw, dict):
            raise ConfigError(f"{ctx} must be an object.")

        player = PlayerConfig(
            name=str(_require_key(player_raw, "name", ctx)),
            starting_bankroll=int(_require_key(player_raw, "starting_bankroll", ctx)),
            strategy=str(_require_key(player_raw, "strategy", ctx)),
            can_be_shooter=bool(player_raw.get("can_be_shooter", True)),
            min_bankroll=(int(player_raw["min_bankroll"]) if "min_bankroll" in player_raw else None),
            max_bankroll=(int(player_raw["max_bankroll"]) if "max_bankroll" in player_raw else None),
        )
        players.append(player)

    if len(players) > 8:
        raise ConfigError(f"Config defines {len(players)} players; maximum supported is 8.")

    if not any(player.can_be_shooter for player in players):
        raise ConfigError("Config must define at least one player with 'can_be_shooter' set to true.")

    return Config(simulation=simulation, players=players)
