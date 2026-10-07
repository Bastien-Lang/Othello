"""Affichage et saisie en console (séparés de la logique du jeu)."""

from __future__ import annotations

from board import Board
from constants import Move, MaybeMove


class ConsoleView:
    """Interface console. Pourra être remplacée par une GUI sans toucher au reste."""

    def show_board(self, board: Board, legal_moves: list[Move] | None = None) -> None:
        """Affiche la grille avec coordonnées (a-h / 1-8), éventuellement avec les coups légaux marqués."""
        raise NotImplementedError

    def show_message(self, message: str) -> None:
        raise NotImplementedError

    def show_move(self, player_name: str, move: MaybeMove) -> None:
        """Annonce le coup joué (ou le passage de tour)."""
        raise NotImplementedError

    def show_result(self, score: dict[int, int], winner: int) -> None:
        raise NotImplementedError

    def ask_move(self, player_name: str) -> str:
        """Lit la saisie brute de l'utilisateur (ex. 'd3')."""
        raise NotImplementedError

    # --- Conversion notation <-> indices -------------------------------------
    @staticmethod
    def parse_move(text: str) -> Move | None:
        """'d3' -> (2, 3). Retourne None si le format est invalide."""
        raise NotImplementedError

    @staticmethod
    def format_move(move: Move) -> str:
        """(2, 3) -> 'd3'."""
        raise NotImplementedError
