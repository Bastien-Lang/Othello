"""Tests Minimax : python -m pytest tests/test_minmax.py (Python avec NumPy)."""

from unittest.mock import patch

from board import Board
from constants import BLACK, WHITE
from player import AIPlayer
from minmax import MinimaxEngine, choose_minimax_move, minimax


def reference(board, depth, turn, ai):
    """Oracle sans mémoire ni délai pour comparer les valeurs à faible profondeur."""
    if board.is_game_over():
        difference = board.count(ai) - board.count(-ai)
        if difference > 0:
            return float('inf')
        if difference < 0:
            return -float('inf')
        return 0
    if depth == 0:
        return board.count(ai) - board.count(-ai)
    moves = board.get_legal_moves(turn)
    if not moves:
        return reference(board, depth, -turn, ai)
    values = []
    for move in moves:
        child = board.copy()
        child.apply_move(move, turn)
        values.append(reference(child, depth - 1, -turn, ai))
    if turn == ai:
        return max(values)
    return min(values)


def test_matches_reference_and_preserves_board():
    """Vérifie le score optimal, le coup associé et l'intégrité du plateau."""
    # Comparer à la référence en 4x4 et vérifier le coup choisi ainsi que la grille.
    board = Board(4)
    board.apply_move(board.get_legal_moves(WHITE)[0], WHITE)
    original = board.to_key()
    for color in (BLACK, WHITE):
        for depth in (1, 2, 3):
            result = MinimaxEngine().search(board, color, depth)
            assert result.score == reference(board, depth, color, color)
            child = board.copy()
            child.apply_move(result.move, color)
            assert reference(child, depth - 1, -color, color) == result.score
            assert result.stats.completed_depth == depth
    assert board.to_key() == original

def test_terminal_results_at_depth_zero():
    """Vérifie que la fin de partie prime sur la limite de profondeur."""
    # Vérifier les scores +inf, -inf et 0 sur des plateaux terminés.
    board = Board(4)
    board.grid.fill(BLACK)
    assert minimax(board, 0, WHITE, BLACK) == float('inf')
    assert minimax(board, 0, BLACK, WHITE) == -float('inf')
    board.grid[:2, :] = WHITE
    assert minimax(board, 0, BLACK, WHITE) == 0
    assert choose_minimax_move(board, WHITE) is None

def test_pass_and_forced_loss():
    """Vérifie une passe obligatoire puis un coup légal malgré une défaite."""
    # Tester une passe forcée, puis un coup légal qui conduit à une défaite.
    board = Board(4)
    board.grid.fill(BLACK)
    board.grid[0, 1] = WHITE
    board.grid[0, 2] = 0
    assert not board.is_game_over()
    assert choose_minimax_move(board, WHITE) is None
    assert minimax(board, 1, WHITE, WHITE) == -float('inf')
    board.grid.fill(BLACK)
    board.grid[0, 0] = WHITE
    board.grid[0, 2] = 0
    result = MinimaxEngine().search(board, WHITE, 1)
    assert result.move == (0, 2)
    assert result.score == -float('inf')

def test_cache_reuse_and_separation_of_depth_and_perspective():
    """Vérifie la réutilisation du cache sans changer les résultats."""
    # Répéter la recherche, puis changer la profondeur et la couleur.
    board = Board(4)
    engine = MinimaxEngine()
    first = engine.search(board, WHITE, 3)
    second = engine.search(board, WHITE, 3)
    assert (first.move, first.score) == (second.move, second.score)
    assert second.stats.cache_hits > 0
    assert second.stats.nodes < first.stats.nodes
    for color in (BLACK, WHITE):
        result = engine.search(board, color, 1)
        assert result.score == reference(board, 1, color, color)

def test_reuse_on_a_later_turn():
    """Vérifie que la mémoire sert encore après deux coups réellement joués."""
    # Jouer deux coups et comparer le moteur conservé à un moteur neuf.
    board = Board(4)
    engine = MinimaxEngine()
    first = engine.search(board, WHITE, 4)
    board.apply_move(first.move, WHITE)
    moves = board.get_legal_moves(BLACK)
    assert moves
    board.apply_move(moves[0], BLACK)
    later = engine.search(board, WHITE, 2)
    assert later.stats.cache_hits > 0
    fresh = MinimaxEngine().search(board, WHITE, 2)
    assert (later.move, later.score) == (fresh.move, fresh.score)

def test_zero_budget_returns_legal_fallback():
    """Vérifie le secours lorsque le délai ne permet aucune recherche."""
    # Avec zéro seconde, attendre un coup légal mais aucun score calculé.
    board = Board()
    result = MinimaxEngine().search(board, WHITE, 4, time_limit=0)
    assert result.move in board.get_legal_moves(WHITE)
    assert result.score is None
    assert result.stats.completed_depth == 0
    assert result.stats.timed_out

def test_timeout_keeps_last_complete_iteration():
    """Vérifie qu'une interruption abandonne seulement l'itération partielle."""
    # Simuler un délai dépassé au niveau 2, puis vérifier le résultat et le cache.
    board = Board(4)
    expected = MinimaxEngine().search(board, WHITE, 1)
    engine = MinimaxEngine()

    def fake_time():
        """Le délai expire dès que le niveau 1 est terminé."""
        if engine.stats.completed_depth == 1:
            return 2.0
        return 0.0

    with patch('minmax.perf_counter', side_effect=fake_time):
        result = engine.search(board, WHITE, 4, time_limit=1.0)
    assert result.stats.timed_out
    assert result.stats.completed_depth == 1
    assert (result.move, result.score) == (expected.move, expected.score)
    assert all((key[-1] == 0 for key in engine.table))
    resumed = engine.search(board, WHITE, 2)
    assert resumed.score == reference(board, 2, WHITE, WHITE)


def test_memory_limit_and_independent_players():
    """Vérifie la capacité du cache, son isolation entre IA et sa remise à zéro."""
    # Limiter le cache, vérifier son isolation entre joueurs puis le vider.
    board = Board(4)
    engine = MinimaxEngine(max_entries=2)
    result = engine.search(board, WHITE, 3)
    assert len(engine.table) <= 2
    assert result.score == reference(board, 3, WHITE, WHITE)
    first, second = AIPlayer(WHITE), AIPlayer(BLACK)
    assert first.engine.table is not second.engine.table
    assert first.choose_move(board) in board.get_legal_moves(WHITE)
    assert first.engine.table
    assert not second.engine.table
    assert first.last_result is not None
    first.engine.clear()
    assert not first.engine.table
    assert first.engine.last_result is None
