"""Joueurs : classe abstraite + implémentations (humain, aléatoire, IA plus tard)."""

from __future__ import annotations

from abc import ABC, abstractmethod
import random

from board import Board
from constants import MaybeMove
from view import ConsoleView


class Player(ABC):
    """Interface commune à tous les joueurs.

    Game ne connaît que cette interface : humain, IA ou joueur aléatoire
    sont interchangeables.
    """

    def __init__(self, color: int, name: str = "Joueur") -> None:
        self.color: int = color
        self.name: str = name

    @abstractmethod
    def choose_move(self, board: Board) -> MaybeMove:
        """Retourne le coup choisi (row, col), ou None si aucun coup n'est possible."""


class HumanPlayer(Player):
    """Joueur humain : demande son coup via la vue."""

    def __init__(self, color: int, view: ConsoleView, name: str = "Humain") -> None:
        super().__init__(color, name)
        self.view: ConsoleView = view

    def choose_move(self, board: Board) -> MaybeMove:
        """Boucle jusqu'à obtenir un coup légal saisi par l'utilisateur."""
        #Coups légaux de CE joueur dans la position actuelle
        legal_moves = board.get_legal_moves(self.color)

        #Aucun coup possible : passage de tour
        if not legal_moves:
            return None

        #On rappelle les coups possibles, convertis en notation 'd3'
        names = ", ".join(self.view.format_move(m) for m in legal_moves)
        self.view.show_message(f"Coups possibles : {names}")

        #On redemande tant que la saisie n'est pas un coup légal
        while True:
            #Texte tapé par l'utilisateur
            text = self.view.ask_move(self.name)
            #Conversion en (row, col), ou None si le format est invalide
            move = self.view.parse_move(text)

            if move is None:
                self.view.show_message("Format invalide : tapez une lettre a-h puis un chiffre 1-8 (ex. d3).")
            elif move not in legal_moves:
                self.view.show_message("Ce coup n'est pas légal, réessayez.")
            else:
                return move


class RandomPlayer(Player):
    """Joue un coup légal au hasard : pratique pour tester le moteur de jeu sans IA."""

    def choose_move(self, board: Board) -> MaybeMove:
        # Liste des coups légaux pour la couleur de CE joueur
        moves = board.get_legal_moves(self.color)
        # Aucun coup possible alors passage de tour
        if not moves:
            return None
        # Sinon on en tire un au hasard dans la liste
        return random.choice(moves)


# todo :
# class AIPlayer(Player):
#     def __init__(self, color, strategy, algorithm, depth, time_limit): ...
