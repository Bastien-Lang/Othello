"""Joueurs : classe abstraite + implémentations (humain, aléatoire, IA plus tard)."""

from __future__ import annotations

from abc import ABC, abstractmethod

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
        raise NotImplementedError


class RandomPlayer(Player):
    """Joue un coup légal au hasard : pratique pour tester le moteur de jeu sans IA."""

    def choose_move(self, board: Board) -> MaybeMove:
        raise NotImplementedError


# Plus tard (phase 2) :
# class AIPlayer(Player):
#     def __init__(self, color, strategy, algorithm, depth, time_limit): ...
