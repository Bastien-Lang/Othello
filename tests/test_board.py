"""Règles indispensables du plateau Othello."""
import pytest
from board import Board
from constants import BLACK, WHITE, EMPTY

def test_initial_position_and_moves():
    """Vérifie les pions et les coups autorisés au début d'une partie."""
    # Comparer les pions et les coups initiaux aux valeurs attendues.
    board = Board()
    assert board.get_score() == {BLACK: 2, WHITE: 2}
    assert board.count(EMPTY) == 60
    assert set(board.get_legal_moves(WHITE)) == {(2, 4), (3, 5), (4, 2), (5, 3)}
    assert set(board.get_legal_moves(BLACK)) == {(2, 3), (3, 2), (4, 5), (5, 4)}

def test_apply_move_flips_discs():
    """Vérifie qu'un coup pose un pion et retourne le pion encadré."""
    # Jouer e3 puis vérifier la capture et le score.
    board = Board()
    assert board.apply_move((2, 4), WHITE) == [(3, 4)]
    assert board.get_score() == {BLACK: 1, WHITE: 4}

def test_illegal_move_preserves_board():
    """Vérifie qu'un coup interdit est refusé sans modifier la grille."""
    # Essayer plusieurs coups interdits et comparer la grille avant/après.
    board = Board()
    before = board.to_key()
    for move in ((0, 0), (3, 3), (-1, 0), (8, 4)):
        with pytest.raises(ValueError):
            board.apply_move(move, WHITE)
        assert board.to_key() == before

def test_pass_when_no_legal_move():
    """Vérifie qu'un joueur bloqué ne suffit pas à terminer la partie."""
    # Construire une position où seul Noir peut encore jouer.
    board = Board(4)
    board.grid.fill(BLACK)
    board.grid[0, 1] = WHITE
    board.grid[0, 2] = EMPTY
    assert not board.has_legal_move(WHITE)
    assert board.get_legal_moves(BLACK) == [(0, 2)]
    assert not board.is_game_over()

def test_game_over_and_winner():
    """Vérifie une victoire sur plateau bloqué puis une égalité."""
    # Tester un plateau bloqué, puis un partage égal des pions.
    board = Board(4)
    board.grid.fill(BLACK)
    board.grid[0, 0] = EMPTY
    assert board.is_game_over()
    assert board.get_winner() == BLACK
    board.grid[0, 0] = BLACK
    board.grid[:2, :] = WHITE
    assert board.get_winner() == EMPTY

def test_copy_is_independent():
    """Vérifie qu'une simulation sur une copie préserve le vrai plateau."""
    # Jouer sur la copie et vérifier que l’original reste intact.
    board = Board()
    copy = board.copy()
    copy.apply_move((2, 4), WHITE)
    assert board.get_score() == {BLACK: 2, WHITE: 2}
    assert copy.to_key() != board.to_key()


def test_flips_in_several_directions():
    """Vérifie qu'un seul coup retourne tous les pions encadrés dans deux axes."""
    # Placer deux lignes à capturer, puis jouer à leur intersection.
    b = Board()
    b.grid.fill(EMPTY)
    b.grid[0, 2] = WHITE      # ferme la ligne vers le haut
    b.grid[1, 2] = BLACK      # à capturer (haut)
    b.grid[2, 0] = WHITE      # ferme la ligne vers la gauche
    b.grid[2, 1] = BLACK      # à capturer (gauche)
    assert set(b.get_flips((2, 2), WHITE)) == {(1, 2), (2, 1)}
    b.apply_move((2, 2), WHITE)
    assert b.get(1, 2) == WHITE and b.get(2, 1) == WHITE


def test_no_capture_without_closing_disc():
    """Vérifie qu'une ligne adverse non fermée ne produit aucune capture."""
    # Aligner des noirs sans blanc pour fermer la ligne.
    b = Board()
    b.grid.fill(EMPTY)
    b.grid[2, 1] = BLACK
    b.grid[2, 2] = BLACK
    assert b.get_flips((2, 0), WHITE) == []
