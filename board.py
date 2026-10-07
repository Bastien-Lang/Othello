"""Plateau d'Othello : état de la grille + règles du jeu (sans aucune IA)."""

from __future__ import annotations

import numpy as np

from constants import BOARD_SIZE, EMPTY, BLACK, WHITE, DIRECTIONS, Move, opponent


class Board:
    """Représente un plateau 8x8 et implémente les règles d'Othello.

    La grille est un tableau numpy d'entiers : EMPTY (0), BLACK (1), WHITE (-1).
    Indices : grid[row, col], (0, 0) en haut à gauche.
    """

    def __init__(self, size: int = BOARD_SIZE) -> None:
        self.size: int = size
        self.grid: np.ndarray = np.zeros((size, size), dtype=np.int8)
        self.reset()

    # --- Initialisation / copie ----------------------------------------------
    def reset(self) -> None:
        """Vide le plateau et place la position de départ (4 pions au centre)."""
        self.grid.fill(EMPTY)
        mid = self.size // 2
        self.grid[mid - 1, mid - 1] = WHITE
        self.grid[mid, mid] = WHITE
        self.grid[mid - 1, mid] = BLACK
        self.grid[mid, mid - 1] = BLACK
        
    def copy(self) -> Board:
        """Copie indépendante du plateau (utile pour l'IA : explorer sans modifier l'original)."""
        new_board = Board(self.size)
        new_board.grid = self.grid.copy()
        return new_board
    # --- Accès aux cases ------------------------------------------------------
    def is_on_board(self, row: int, col: int) -> bool:
        """Vrai si les coordonnées sont valides (0 <= row, col < size)."""
        return 0 <= row < self.size and 0 <= col < self.size

    def get(self, row: int, col: int) -> int:
        """Retourne le contenu d'une case (EMPTY, BLACK ou WHITE)."""
        if not self.is_on_board(row, col):
            raise IndexError(f"Case ({row}, {col}) hors plateau.")
        return self.grid[row, col]

    def count(self, color: int) -> int:
        """Nombre de pions d'une couleur sur le plateau."""
        return np.count_nonzero(self.grid == color) 

    # --- Règles : coups -------------------------------------------------------
    def get_flips(self, move: Move, color: int) -> list[Move]:
        row, col = move

        # 1. La case doit exister et être vide
        if not self.is_on_board(row, col) or self.grid[row, col] != EMPTY:
            return []

        enemy = opponent(color)
        flips: list[Move] = []

        # 2. On explore les 8 directions
        for dr, dc in DIRECTIONS:
            line: list[Move] = []          # pions adverses rencontrés dans CETTE direction
            r, c = row + dr, col + dc      # première case voisine

            # 3. On avance tant qu'on tombe sur des pions adverses
            while self.is_on_board(r, c) and self.grid[r, c] == enemy:
                line.append((r, c))
                r += dr
                c += dc

            # 4. La ligne n'est capturée que si elle est fermée par un pion à nous
            if line and self.is_on_board(r, c) and self.grid[r, c] == color:
                flips.extend(line)

        return flips

    def is_legal_move(self, move: Move, color: int) -> bool:
        raise NotImplementedError

    def get_legal_moves(self, color: int) -> list[Move]:
        """Tous les coups légaux de `color` dans la position actuelle."""
        raise NotImplementedError

    def has_legal_move(self, color: int) -> bool:
        raise NotImplementedError

    def apply_move(self, move: Move, color: int) -> list[Move]:
        """Joue le coup (pose le pion + retourne les pions capturés).

        Retourne la liste des cases retournées (utile pour l'historique / annuler un coup).
        Lève une ValueError si le coup est illégal.
        """
        raise NotImplementedError

    # --- Règles : fin de partie / score --------------------------------------
    def is_game_over(self) -> bool:
        """Vrai si aucun des deux joueurs ne peut jouer (plateau plein ou blocage)."""
        raise NotImplementedError

    def get_score(self) -> dict[int, int]:
        """Retourne {BLACK: nb_noirs, WHITE: nb_blancs}."""
        raise NotImplementedError

    def get_winner(self) -> int:
        """BLACK, WHITE, ou EMPTY en cas d'égalité (à appeler en fin de partie)."""
        raise NotImplementedError

    # --- Utilitaires (préparent l'IA) ----------------------------------------
    def to_key(self) -> bytes:
        """Représentation hachable de la position (clé de la future table de transposition)."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Représentation texte brute du plateau (le rendu soigné est dans view.py)."""
        raise NotImplementedError
