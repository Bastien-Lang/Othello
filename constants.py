"""Constantes globales et alias de types du projet Othello."""

from typing import Optional

# --- Plateau -----------------------------------------------------------------
BOARD_SIZE = 8

# --- Contenu d'une case ------------------------------------------------------
# Convention +1 / -1 : l'adversaire d'un joueur est simplement -color,
# ce qui simplifiera NegaMax plus tard.
EMPTY = 0
BLACK = 1
WHITE = -1

# Le sujet précise que les blancs débutent la partie
FIRST_PLAYER = WHITE

# --- Directions (d_row, d_col) pour parcourir le plateau ----------------------
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

# --- Alias de types ----------------------------------------------------------
Move = tuple[int, int]          # (row, col)
MaybeMove = Optional[Move]      # None = le joueur passe son tour


def opponent(color: int) -> int:
    """Retourne la couleur adverse."""
    return -color
