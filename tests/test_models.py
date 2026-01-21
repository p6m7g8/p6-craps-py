"""Tests for player and table models."""

from __future__ import annotations

import pytest

from p6_craps.models import Bankroll, Player, Table


class TestBankroll:
    """Test suite for Bankroll."""

    def test_rejects_negative_balance(self) -> None:
        """Bankroll balance must be non-negative."""
        with pytest.raises(ValueError, match="negative"):
            Bankroll(balance=-1)

    def test_rejects_non_positive_max_win(self) -> None:
        """Max win must be positive when provided."""
        with pytest.raises(ValueError, match="max_win"):
            Bankroll(balance=10, max_win=0)

    def test_apply_updates_balance(self) -> None:
        """Applying delta returns a new bankroll."""
        bankroll = Bankroll(balance=100)
        updated = bankroll.apply(-25)
        assert updated.balance == 75


class TestPlayer:
    """Test suite for Player."""

    def test_rejects_empty_name(self) -> None:
        """Player name must be non-empty."""
        with pytest.raises(ValueError, match="name"):
            Player(name="   ", bankroll=Bankroll(balance=10))


class TestTable:
    """Test suite for Table."""

    def test_empty_table_has_nine_seats(self) -> None:
        """Empty table should have nine open seats."""
        table = Table.empty()
        assert len(table.seats) == 9
        assert all(seat is None for seat in table.seats)

    def test_seat_player_updates_table(self) -> None:
        """Seating a player returns a new table."""
        table = Table.empty()
        player = Player(name="Shooter", bankroll=Bankroll(balance=100))
        updated = table.seat_player(0, player)
        assert updated.seats[0] == player

    def test_seat_player_rejects_invalid_index(self) -> None:
        """Seat index must be within range."""
        table = Table.empty()
        player = Player(name="Player", bankroll=Bankroll(balance=100))
        with pytest.raises(IndexError, match="Seat index"):
            table.seat_player(9, player)

    def test_seat_player_rejects_occupied_seat(self) -> None:
        """Seat must be open to add a player."""
        table = Table.empty()
        player = Player(name="Player", bankroll=Bankroll(balance=100))
        seated = table.seat_player(0, player)
        with pytest.raises(ValueError, match="occupied"):
            seated.seat_player(0, player)
