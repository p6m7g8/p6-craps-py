"""Tests for the terminal UI renderer."""

from io import StringIO

from p6_craps.config import Config, PlayerConfig, SimulationConfig
from p6_craps.constants import STRATEGY_FLAT_PASS
from p6_craps.engine import Bet, CrapsEngine, CrapsTable
from p6_craps.players import create_player_states
from p6_craps.ui.terminal import (
    PlayerRow,
    build_header_info,
    draw_frame,
    format_player_table,
    render_frame,
    snapshot_players,
)


def _make_single_player_config() -> Config:
    """Create a minimal configuration with a single flat-pass player."""
    sim_cfg = SimulationConfig(
        points=40,
        min_bankroll=0,
        max_bankroll=4000,
        random_seed=None,
    )
    player_cfg = PlayerConfig(
        name="Player 1",
        starting_bankroll=2000,
        strategy=STRATEGY_FLAT_PASS,
        can_be_shooter=True,
    )
    return Config(simulation=sim_cfg, players=[player_cfg])


def test_snapshot_players_includes_on_table_and_shooter_flag() -> None:
    """snapshot_players should calculate on-table amount and shooter flag."""
    cfg = _make_single_player_config()
    players = create_player_states(cfg)
    table = CrapsTable()

    # Place a single working bet for player 0.
    table.place_bet(Bet(player_index=0, bet_type="pass_line", base_amount=25))

    # Mark the player as shooter so the flag is visible.
    players[0].is_current_shooter = True

    rows = snapshot_players(players, table)
    assert len(rows) == 1

    row = rows[0]
    assert isinstance(row, PlayerRow)
    assert row.name == "Player 1"
    assert row.on_table == 25
    assert row.is_shooter is True


def test_format_player_table_renders_header_and_player_name() -> None:
    """format_player_table should emit a header and player row."""
    cfg = _make_single_player_config()
    players = create_player_states(cfg)
    table = CrapsTable()

    rows = snapshot_players(players, table)
    table_text = format_player_table(rows)

    assert "Player" in table_text
    assert "Bankroll" in table_text
    assert "Player 1" in table_text


def test_render_and_draw_frame_include_header_and_clear_sequence() -> None:
    """render_frame and draw_frame should include header text and optional clear sequence."""
    cfg = _make_single_player_config()
    players = create_player_states(cfg)
    table = CrapsTable()
    engine = CrapsEngine()

    # Build snapshot state.
    rows = snapshot_players(players, table)
    header_info = build_header_info(engine, roll_index=3, shooter_index=0, shooter_roll_index=1)

    frame = render_frame(header_info, rows)
    assert "Roll 3" in frame
    assert "Shooter 0" in frame

    # When clear=True, the ANSI clear sequence should be present.
    stream = StringIO()
    draw_frame(stream, frame, clear=True)
    output = stream.getvalue()
    assert "\x1b[2J\x1b[H" in output
    assert "Roll 3" in output

    # When clear=False, the ANSI clear sequence should not be present.
    stream_no_clear = StringIO()
    draw_frame(stream_no_clear, frame, clear=False)
    output_no_clear = stream_no_clear.getvalue()
    assert "\x1b[2J\x1b[H" not in output_no_clear
    assert "Roll 3" in output_no_clear
