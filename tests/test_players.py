from p6_craps.config import Config, PlayerConfig, SimulationConfig
from p6_craps.players import PlayerState, create_player_states


def test_player_state_credit_and_debit_update_profit() -> None:
    cfg = PlayerConfig(
        name="Player 1",
        starting_bankroll=2000,
        strategy="flat_pass",
        can_be_shooter=True,
    )
    state = PlayerState(config=cfg, bankroll=cfg.starting_bankroll)

    state.credit(200)
    assert state.bankroll == 2200
    assert state.total_profit == 200

    state.debit(100)
    assert state.bankroll == 2100
    assert state.total_profit == 100


def test_player_state_shooter_profit_tracks_only_when_shooting() -> None:
    cfg = PlayerConfig(
        name="Shooter",
        starting_bankroll=2000,
        strategy="flat_pass",
        can_be_shooter=True,
    )
    state = PlayerState(config=cfg, bankroll=cfg.starting_bankroll)

    # Not the shooter yet: shooter_profit should remain zero.
    state.credit(100)
    assert state.shooter_profit == 0

    # Now mark as current shooter and apply debits/credits.
    state.is_current_shooter = True
    state.credit(50)
    state.debit(20)
    assert state.shooter_profit == 30  # +50 - 20


def test_create_player_states_builds_state_from_config() -> None:
    player_cfg = PlayerConfig(
        name="Config Player",
        starting_bankroll=1500,
        strategy="flat_pass",
        can_be_shooter=True,
    )
    sim_cfg = SimulationConfig(
        points=40,
        min_bankroll=0,
        max_bankroll=4000,
        random_seed=None,
    )
    cfg = Config(simulation=sim_cfg, players=[player_cfg])

    states = create_player_states(cfg)
    assert len(states) == 1

    state = states[0]
    assert state.name == "Config Player"
    assert state.bankroll == 1500
    assert state.total_profit == 0
    assert state.shooter_profit == 0
    assert state.strategy_name == "flat_pass"
    assert state.can_be_shooter is True
