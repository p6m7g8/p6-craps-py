"""Tests for the craps table and bet resolution logic."""

from p6_craps.engine import Bet, CrapsEngine, CrapsTable, Roll
from p6_craps.strategy import BET_TYPE_PASS_LINE


def test_pass_line_resolves_on_come_out_natural_win() -> None:
    """A pass-line bet wins on a natural 7 on the come-out roll."""
    engine = CrapsEngine()
    table = CrapsTable()
    bet = Bet(player_index=0, bet_type=BET_TYPE_PASS_LINE, base_amount=25)
    table.place_bet(bet)

    result = engine.apply_roll(Roll(d1=3, d2=4))  # total = 7
    resolved = table.resolve_on_point_cycle_result(result)

    assert len(resolved) == 1
    resolved_bet = resolved[0]
    assert resolved_bet.bet is bet
    assert resolved_bet.payout == 50
    assert resolved_bet.profit == 25
    assert not table.bets


def test_pass_line_resolves_on_come_out_craps_loss() -> None:
    """A pass-line bet loses on craps (2, 3, or 12) on the come-out roll."""
    engine = CrapsEngine()
    table = CrapsTable()
    bet = Bet(player_index=0, bet_type=BET_TYPE_PASS_LINE, base_amount=25)
    table.place_bet(bet)

    result = engine.apply_roll(Roll(d1=1, d2=1))  # total = 2
    resolved = table.resolve_on_point_cycle_result(result)

    assert len(resolved) == 1
    resolved_bet = resolved[0]
    assert resolved_bet.bet is bet
    assert resolved_bet.payout == 0
    assert resolved_bet.profit == -25
    assert not table.bets


def test_pass_line_carries_to_point_and_resolves_on_point_made() -> None:
    """A pass-line bet carries to the point and resolves when the point is made."""
    engine = CrapsEngine()
    table = CrapsTable()
    bet = Bet(player_index=0, bet_type=BET_TYPE_PASS_LINE, base_amount=25)
    table.place_bet(bet)

    # Establish point 4.
    first_result = engine.apply_roll(Roll(d1=2, d2=2))  # total = 4
    first_resolved = table.resolve_on_point_cycle_result(first_result)
    assert not first_resolved
    assert table.bets  # bet still active

    # Make the point 4 again.
    second_result = engine.apply_roll(Roll(d1=1, d2=3))  # total = 4
    second_resolved = table.resolve_on_point_cycle_result(second_result)

    assert len(second_resolved) == 1
    resolved_bet = second_resolved[0]
    assert resolved_bet.bet is bet
    assert resolved_bet.payout == 50
    assert resolved_bet.profit == 25
    assert not table.bets


def test_pass_line_resolves_on_seven_out_after_point() -> None:
    """A pass-line bet loses on a 7-out after a point is established."""
    engine = CrapsEngine()
    table = CrapsTable()
    bet = Bet(player_index=0, bet_type=BET_TYPE_PASS_LINE, base_amount=25)
    table.place_bet(bet)

    # Establish point 5.
    first_result = engine.apply_roll(Roll(d1=2, d2=3))  # total = 5
    first_resolved = table.resolve_on_point_cycle_result(first_result)
    assert not first_resolved
    assert table.bets

    # Seven out.
    second_result = engine.apply_roll(Roll(d1=3, d2=4))  # total = 7
    second_resolved = table.resolve_on_point_cycle_result(second_result)

    assert len(second_resolved) == 1
    resolved_bet = second_resolved[0]
    assert resolved_bet.bet is bet
    assert resolved_bet.payout == 0
    assert resolved_bet.profit == -25
    assert not table.bets
