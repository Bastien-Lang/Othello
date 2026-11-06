"""Comparaison alpha-bêta / Minimax et cas particuliers du cache."""

import random
from unittest.mock import patch

import pytest

from alphabeta import AlphaBetaEngine, alphabeta, choose_alphabeta_move
from board import Board
from constants import BLACK, WHITE
from minmax import MinimaxEngine, minimax


def test_same_values_and_optimal_moves_on_reachable_positions():
    """Compare les choix d'alpha-bêta à Minimax sur des positions légales."""
    # Comparer coups et scores sur plusieurs positions reproductibles en 4x4.
    rng = random.Random(42)
    board = Board(4)
    engine = AlphaBetaEngine()
    turn = WHITE
    for _ in range(12):
        original = board.to_key()
        for color in (BLACK, WHITE):
            for depth in (1, 2, 3):
                expected = MinimaxEngine().search(board, color, depth)
                actual = engine.search(board, color, depth)
                assert (actual.move, actual.score) == (expected.move, expected.score)
                if actual.move is not None:
                    child = board.copy()
                    child.apply_move(actual.move, color)
                    assert minimax(child, depth - 1, -color, color) == actual.score
        assert board.to_key() == original
        moves = board.get_legal_moves(turn)
        if moves:
            board.apply_move(rng.choice(moves), turn)
        turn = -turn


def test_pruning_reduces_nodes_and_cache_is_reused():
    """Vérifie le gain d'élagage puis le gain de mémoire sur la même position."""
    # Comparer les nœuds explorés, puis relancer alpha-bêta avec son cache.
    board = Board()
    engine = AlphaBetaEngine()
    expected = MinimaxEngine().search(board, WHITE, 4)
    first = engine.search(board, WHITE, 4)
    second = engine.search(board, WHITE, 4)
    assert (first.move, first.score) == (expected.move, expected.score)
    assert first.stats.nodes < expected.stats.nodes
    assert second.score == first.score
    assert second.stats.cache_hits > 0
    assert second.stats.nodes < first.stats.nodes


@pytest.mark.parametrize('alpha, beta', [(-10, -9), (9, 10)])
def test_bound_is_not_saved(alpha, beta):
    """Vérifie qu'une recherche limitée par une fenêtre ne corrompt pas le cache."""
    # Calculer une borne avec une fenêtre étroite, puis rechercher la valeur exacte.
    board = Board(4)
    engine = AlphaBetaEngine()
    engine._alphabeta(board, 3, WHITE, WHITE, alpha, beta)
    key = (board.size, board.to_key(), WHITE, WHITE, 3)
    assert key not in engine.table
    assert engine._minimax(board, 3, WHITE, WHITE) == minimax(board, 3, WHITE, WHITE)


def test_pass_terminal_draw_and_forced_loss():
    """Vérifie les passes, les défaites forcées et les scores de fin de partie."""
    # Construire successivement une passe, une défaite, une victoire et une égalité.
    board = Board(4)
    board.grid.fill(BLACK)
    board.grid[0, 1] = WHITE
    board.grid[0, 2] = 0
    assert choose_alphabeta_move(board, WHITE) is None
    assert alphabeta(board, 1, WHITE, WHITE) == -float('inf')
    board.grid[0, 0], board.grid[0, 1] = WHITE, BLACK
    result = AlphaBetaEngine().search(board, WHITE, 1)
    assert result.move == (0, 2)
    assert result.score == -float('inf')
    board.grid.fill(BLACK)
    assert alphabeta(board, 0, WHITE, BLACK) == float('inf')
    board.grid[:2, :] = WHITE
    assert alphabeta(board, 0, WHITE, WHITE) == 0


def test_timeout_keeps_last_completed_iteration():
    """Vérifie que le délai conserve le dernier choix entièrement calculé."""
    # Simuler l’expiration au niveau 2 et vérifier que le choix du niveau 1 reste.
    board = Board(4)
    expected = AlphaBetaEngine().search(board, WHITE, 1)
    engine = AlphaBetaEngine()

    def fake_time():
        """Le délai expire dès que le niveau 1 est terminé."""
        if engine.stats.completed_depth == 1:
            return 2.0
        return 0.0

    with patch('minmax.perf_counter', side_effect=fake_time):
        result = engine.search(board, WHITE, 4, time_limit=1)
    assert result.stats.timed_out
    assert result.stats.completed_depth == 1
    assert (result.move, result.score) == (expected.move, expected.score)
    assert all(key[-1] == 0 for key in engine.table)
    assert engine.search(board, WHITE, 3).score == minimax(board, 3, WHITE, WHITE)


def test_zero_budget_memory_limit_and_clear():
    """Vérifie le coup de secours, la taille du cache et sa remise à zéro."""
    # Tester un délai nul, un cache de deux entrées puis clear().
    board = Board(4)
    engine = AlphaBetaEngine(max_entries=2)
    fallback = engine.search(board, WHITE, 4, time_limit=0)
    assert fallback.move in board.get_legal_moves(WHITE)
    assert fallback.score is None
    assert fallback.stats.timed_out
    assert engine.search(board, WHITE, 3).score == minimax(board, 3, WHITE, WHITE)
    assert len(engine.table) <= 2
    engine.clear()
    assert not engine.table
    assert engine.last_result is None


