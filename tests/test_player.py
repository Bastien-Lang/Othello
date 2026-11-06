"""Tests des joueurs."""

import pytest

from board import Board
from constants import BLACK, WHITE, EMPTY
from player import Player, HumanPlayer, RandomPlayer
from view import ConsoleView


def test_player_is_abstract():
    with pytest.raises(TypeError):
        Player(WHITE)


def test_random_player_plays_legal_move():
    board = Board()
    player = RandomPlayer(WHITE, "Aléa")
    for _ in range(20):
        assert player.choose_move(board) in board.get_legal_moves(WHITE)


def test_random_player_returns_none_when_blocked():
    b = Board()
    b.grid.fill(EMPTY)
    b.grid[0, 0] = WHITE
    b.grid[0, 1] = BLACK
    assert RandomPlayer(BLACK, "N").choose_move(b) is None


def test_human_retries_until_legal(monkeypatch):
    # 1re saisie : format invalide, 2e : bien formée mais illégale, 3e : légale
    answers = iter(["zz", "a1", "e3"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    player = HumanPlayer(WHITE, ConsoleView(), "Blanc")
    assert player.choose_move(Board()) == (2, 4)


def test_human_returns_none_when_blocked():
    b = Board()
    b.grid.fill(EMPTY)
    b.grid[0, 0] = WHITE
    b.grid[0, 1] = BLACK
    assert HumanPlayer(BLACK, ConsoleView(), "N").choose_move(b) is None
