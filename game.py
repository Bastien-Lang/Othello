"""Orchestration d'une partie : alternance des joueurs, passes, historique, fin de partie."""

from __future__ import annotations

from dataclasses import dataclass, field

from board import Board
from constants import FIRST_PLAYER, Move, MaybeMove
from player import Player
from view import ConsoleView


@dataclass
class MoveRecord:
    """Trace d'un coup (permet de rejouer la partie, de l'exporter, d'annuler)."""
    color: int
    move: MaybeMove                 # None = passage de tour
    flipped: list[Move] = field(default_factory=list)


class Game:
    """Gère le déroulement d'une partie entre deux joueurs."""

    def __init__(self, black: Player, white: Player, view: ConsoleView | None = None) -> None:
        self.board: Board = Board()
        self.players: dict[int, Player] = {black.color: black, white.color: white}
        self.current_color: int = FIRST_PLAYER
        self.view: ConsoleView | None = view
        self.history: list[MoveRecord] = []

    @property
    def current_player(self) -> Player:
        raise NotImplementedError

    def switch_player(self) -> None:
        raise NotImplementedError

    def play_turn(self) -> None:
        """Un tour : coups légaux ? -> sinon passe ; sinon demande un coup au joueur,
        le valide, l'applique, l'enregistre dans l'historique, change de joueur."""
        raise NotImplementedError

    def is_over(self) -> bool:
        raise NotImplementedError

    def run(self) -> int:
        """Boucle principale. Retourne le gagnant (BLACK, WHITE ou EMPTY)."""
        raise NotImplementedError

    # --- Historique (extensions du sujet) ------------------------------------
    def save_history(self, path: str) -> None:
        """Écrit la liste des coups dans un fichier pour re-jouer la partie."""
        raise NotImplementedError
