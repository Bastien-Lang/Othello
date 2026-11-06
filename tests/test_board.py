<<<<<<< HEAD
﻿"""Tests des règles du plateau."""
import unittest
from board import Board
from constants import BLACK, WHITE, EMPTY

class BoardTests(unittest.TestCase):
    def test_initial_position_and_moves(self):
        board = Board()
        self.assertEqual(board.get_score(), {BLACK: 2, WHITE: 2})
        self.assertEqual(board.count(EMPTY), 60)
        self.assertEqual(set(board.get_legal_moves(WHITE)), {(2, 4), (3, 5), (4, 2), (5, 3)})
        self.assertEqual(set(board.get_legal_moves(BLACK)), {(2, 3), (3, 2), (4, 5), (5, 4)})

    def test_apply_move_flips_discs(self):
        board = Board()
        self.assertEqual(board.apply_move((2, 4), WHITE), [(3, 4)])
        self.assertEqual(board.get_score(), {BLACK: 1, WHITE: 4})

    def test_illegal_move_preserves_board(self):
        board = Board()
        before = board.to_key()
        for move in ((0, 0), (3, 3), (-1, 0), (8, 4)):
            with self.assertRaises(ValueError):
                board.apply_move(move, WHITE)
            self.assertEqual(board.to_key(), before)

    def test_pass_when_no_legal_move(self):
        board = Board(4)
        board.grid.fill(BLACK)
        board.grid[0, 1] = WHITE
        board.grid[0, 2] = EMPTY
        self.assertFalse(board.has_legal_move(WHITE))
        self.assertEqual(board.get_legal_moves(BLACK), [(0, 2)])
        self.assertFalse(board.is_game_over())

    def test_game_over_and_winner(self):
        board = Board(4)
        board.grid.fill(BLACK)
        board.grid[0, 0] = EMPTY
        self.assertTrue(board.is_game_over())
        self.assertEqual(board.get_winner(), BLACK)
        board.grid[0, 0] = BLACK
        board.grid[:2, :] = WHITE
        self.assertEqual(board.get_winner(), EMPTY)

    def test_copy_is_independent(self):
        board = Board()
        copy = board.copy()
        copy.apply_move((2, 4), WHITE)
        self.assertEqual(board.get_score(), {BLACK: 2, WHITE: 2})
        self.assertNotEqual(copy.to_key(), board.to_key())
=======
"""Tests des règles du plateau."""

import pytest

from board import Board
from constants import BLACK, WHITE, EMPTY


def test_initial_position():
    b = Board()
    assert b.get(3, 3) == WHITE
    assert b.get(4, 4) == WHITE
    assert b.get(3, 4) == BLACK
    assert b.get(4, 3) == BLACK
    assert b.get_score() == {BLACK: 2, WHITE: 2}


def test_is_on_board():
    b = Board()
    assert b.is_on_board(0, 0)
    assert b.is_on_board(7, 7)
    assert not b.is_on_board(8, 0)
    assert not b.is_on_board(0, -1)


def test_get_out_of_board_raises():
    with pytest.raises(IndexError):
        Board().get(8, 0)


def test_initial_legal_moves():
    b = Board()
    assert b.get_legal_moves(WHITE) == [(2, 4), (3, 5), (4, 2), (5, 3)]
    assert b.get_legal_moves(BLACK) == [(2, 3), (3, 2), (4, 5), (5, 4)]


def test_get_flips():
    b = Board()
    assert b.get_flips((2, 4), WHITE) == [(3, 4)]
    assert b.get_flips((0, 0), WHITE) == []     # rien à capturer
    assert b.get_flips((3, 3), WHITE) == []     # case occupée


def test_apply_move_flips_discs():
    b = Board()
    assert b.apply_move((2, 4), WHITE) == [(3, 4)]
    assert b.get(2, 4) == WHITE                 # pion posé
    assert b.get(3, 4) == WHITE                 # pion retourné
    assert b.get_score() == {BLACK: 1, WHITE: 4}


def test_illegal_move_raises_and_board_unchanged():
    b = Board()
    before = b.grid.copy()
    with pytest.raises(ValueError):
        b.apply_move((0, 0), WHITE)
    assert (b.grid == before).all()


def test_flips_in_several_directions():
    # Un seul coup qui capture dans deux directions à la fois
    b = Board()
    b.grid.fill(EMPTY)
    b.grid[0, 2] = WHITE      # ferme la ligne vers le haut
    b.grid[1, 2] = BLACK      # à capturer (haut)
    b.grid[2, 0] = WHITE      # ferme la ligne vers la gauche
    b.grid[2, 1] = BLACK      # à capturer (gauche)
    # Les blancs jouent en (2, 2) : captures dans deux directions
    assert set(b.get_flips((2, 2), WHITE)) == {(1, 2), (2, 1)}
    b.apply_move((2, 2), WHITE)
    assert b.get(1, 2) == WHITE and b.get(2, 1) == WHITE


def test_no_capture_without_closing_disc():
    # Pions adverses alignés mais jamais fermés par un pion à nous : pas de capture
    b = Board()
    b.grid.fill(EMPTY)
    b.grid[2, 1] = BLACK
    b.grid[2, 2] = BLACK
    assert b.get_flips((2, 0), WHITE) == []


def test_has_legal_move_and_pass_position():
    b = Board()
    b.grid.fill(EMPTY)
    b.grid[0, 0] = WHITE
    b.grid[0, 1] = BLACK
    assert b.has_legal_move(WHITE)        # Blanc peut jouer en (0, 2)
    assert not b.has_legal_move(BLACK)    # Noir est bloqué
    assert not b.is_game_over()           # un seul bloqué : la partie continue


def test_game_over_full_board_black_wins():
    b = Board()
    b.grid.fill(BLACK)
    assert b.is_game_over()
    assert b.get_winner() == BLACK


def test_game_over_draw():
    b = Board()
    b.grid[:4, :] = BLACK
    b.grid[4:, :] = WHITE
    assert b.is_game_over()
    assert b.get_score() == {BLACK: 32, WHITE: 32}
    assert b.get_winner() == EMPTY


def test_copy_is_independent():
    b = Board()
    c = b.copy()
    c.apply_move((2, 4), WHITE)
    assert b.get_score() == {BLACK: 2, WHITE: 2}     # l'original n'a pas bougé
    assert c.get_score() == {BLACK: 1, WHITE: 4}


def test_to_key():
    b = Board()
    assert b.to_key() == b.copy().to_key()
    c = b.copy()
    c.apply_move((2, 4), WHITE)
    assert b.to_key() != c.to_key()
    hash(b.to_key())                                  # doit être hachable


def test_str():
    lines = str(Board()).split("\n")
    assert len(lines) == 8
    assert lines[3] == ". . . W B . . ."
    assert lines[4] == ". . . B W . . ."
>>>>>>> ef4501c08295a27fe1d3b091eb7d112f1fcbc292
