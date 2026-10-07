"""Plateau d'Othello : état de la grille + règles du jeu (sans aucune IA)."""

from __future__ import annotations

import numpy as np

from constants import BOARD_SIZE, EMPTY, BLACK, WHITE, DIRECTIONS, Move


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
        raise NotImplementedError

    def copy(self) -> Board:
        """Copie indépendante du plateau (utile pour l'IA : explorer sans modifier l'original)."""
        raise NotImplementedError

    # --- Accès aux cases ------------------------------------------------------
    def is_on_board(self, row: int, col: int) -> bool:
        raise NotImplementedError

    def get(self, row: int, col: int) -> int:
        """Retourne le contenu d'une case (EMPTY, BLACK ou WHITE)."""
        raise NotImplementedError

    def count(self, color: int) -> int:
        """Nombre de pions d'une couleur sur le plateau."""
        raise NotImplementedError

    # --- Règles : coups -------------------------------------------------------
    def get_flips(self, move: Move, color: int) -> list[Move]:
        """Liste des cases qui seraient retournées si `color` jouait `move`.

        Pour chaque direction : suite de pions adverses fermée par un pion de `color`.
        Liste vide => le coup est illégal (ou la case est occupée).
        """
        raise NotImplementedError

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
