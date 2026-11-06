"""Tests des règles du plateau."""
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
