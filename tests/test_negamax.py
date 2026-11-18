"""Vérifier les changements de point de vue de NegaMax face à MinMax."""

import random
from unittest.mock import patch

from board import Board
from constants import BLACK, WHITE
from minmax import MinimaxEngine, minimax
from negamax import NegamaxEngine, negamax, choose_negamax_move


def test_matches_minimax_on_reachable_positions():
    board = Board(4)
    rng = random.Random(42)
    turn = WHITE
    for _ in range(12):
        original = board.to_key()
        for color in (BLACK, WHITE):
            for depth in (1, 2, 3):
                expected = MinimaxEngine().search(board, color, depth)
                actual = NegamaxEngine().search(board, color, depth)
                assert (actual.move, actual.score) == (expected.move, expected.score)
                assert negamax(board, depth, color) == minimax(board, depth, color, color)
        assert board.to_key() == original
        moves = board.get_legal_moves(turn)
        if moves:
            board.apply_move(rng.choice(moves), turn)
        turn = -turn


def test_pass_terminal_and_forced_loss():
    board = Board(4)
    board.grid.fill(BLACK)
    board.grid[0, 1] = WHITE
    board.grid[0, 2] = 0
    assert choose_negamax_move(board, WHITE) is None
    assert negamax(board, 1, WHITE) == -float('inf')
    assert negamax(board, 1, BLACK) == float('inf')
    board.grid[0, 0], board.grid[0, 1] = WHITE, BLACK
    result = NegamaxEngine().search(board, WHITE, 1)
    assert (result.move, result.score) == ((0, 2), -float('inf'))
    board.grid.fill(BLACK)
    assert negamax(board, 0, BLACK) == float('inf')
    assert negamax(board, 0, WHITE) == -float('inf')
    board.grid[:2, :] = WHITE
    assert negamax(board, 0, WHITE) == 0


def test_cache_and_timeout():
    board = Board(4)
    engine = NegamaxEngine()
    first = engine.search(board, WHITE, 3)
    second = engine.search(board, WHITE, 3)
    assert (first.move, first.score) == (second.move, second.score)
    assert second.stats.cache_hits > 0
    assert second.stats.nodes < first.stats.nodes
    engine.clear()
    expected = engine.search(board, WHITE, 1)
    engine.clear()

    def fake_time():
        return 2.0 if engine.stats.completed_depth == 1 else 0.0

    with patch('minmax.perf_counter', side_effect=fake_time):
        result = engine.search(board, WHITE, 4, time_limit=1)
    assert result.stats.timed_out
    assert result.stats.completed_depth == 1
    assert (result.move, result.score) == (expected.move, expected.score)
    assert all(depth == 0 for depth, _ in engine.table.values())
    fallback = engine.search(board, WHITE, 3, time_limit=0)
    assert fallback.move in board.get_legal_moves(WHITE)
    assert fallback.score is None
    assert fallback.stats.timed_out
    limited = NegamaxEngine(max_entries=2)
    assert limited.search(board, WHITE, 3).score == first.score
    assert len(limited.table) <= 2
