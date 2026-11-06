"""Orchestration d'une partie : alternance des joueurs, passes, historique, fin de partie."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from board import Board
from constants import BLACK, WHITE, FIRST_PLAYER, Move, MaybeMove, opponent
from player import Player
from view import ConsoleView
from constants import FIRST_PLAYER, BLACK, Move, MaybeMove, opponent


@dataclass
class MoveRecord:
    """Trace d'un coup (permet de rejouer la partie, de l'exporter, d'annuler)."""
    color: int
    move: MaybeMove                 # None = passage de tour
    flipped: list[Move] = field(default_factory=list)


class Game:
    """Gère le déroulement d'une partie entre deux joueurs."""

    def __init__(self, black: Player, white: Player, view: ConsoleView | None = None) -> None:
        if black.color != BLACK or white.color != WHITE:
            raise ValueError("Il faut un joueur noir et un joueur blanc, dans cet ordre.")
        self.board: Board = Board()
        self.players: dict[int, Player] = {black.color: black, white.color: white}
        self.current_color: int = FIRST_PLAYER
        self.view: ConsoleView | None = view
        self.history: list[MoveRecord] = []

    @property
    def current_player(self) -> Player:
        return self.players[self.current_color]

    def switch_player(self) -> None:
        self.current_color = opponent(self.current_color)

    def play_turn(self) -> None:
        """Un tour : coups légaux ? -> sinon passe ; sinon demande un coup au joueur,
        le valide, l'applique, l'enregistre dans l'historique, change de joueur."""
<<<<<<< HEAD
        if self.is_over():
            return
        player = self.current_player
        legal_moves = self.board.get_legal_moves(self.current_color)
        if self.view is not None:
            self.view.show_board(self.board, legal_moves)
        move = None
        flipped = []
        if legal_moves:
            move = player.choose_move(self.board)
            if move not in legal_moves:
                raise ValueError(f"Coup illégal proposé par {player.name} : {move}")
            flipped = self.board.apply_move(move, self.current_color)
        self.history.append(MoveRecord(self.current_color, move, flipped))
        if self.view is not None:
            self.view.show_move(player.name, move)
=======
        color = self.current_color
        player = self.current_player

        # Cas 1 : aucun coup possible -> passage de tour (règle du jeu)
        if not self.board.has_legal_move(color):
            self.history.append(MoveRecord(color, None))
            if self.view is not None:
                self.view.show_move(player.name, None)
            self.switch_player()
            return

        # Cas 2 : tour normal. On affiche le plateau avant que le joueur choisisse
        if self.view is not None:
            self.view.show_board(self.board)

        # On donne une COPIE : le joueur ne peut pas abîmer le vrai plateau
        move = player.choose_move(self.board.copy())

        # On ne fait pas confiance au joueur : coup None ou illégal = bug
        if move is None or not self.board.is_legal_move(move, color):
            raise ValueError(f"{player.name} a proposé un coup invalide : {move}")

        # On applique le coup et on garde les pions retournés pour l'historique
        flipped = self.board.apply_move(move, color)
        self.history.append(MoveRecord(color, move, flipped))

        if self.view is not None:
            self.view.show_move(player.name, move)

>>>>>>> ef4501c08295a27fe1d3b091eb7d112f1fcbc292
        self.switch_player()

    def is_over(self) -> bool:
        return self.board.is_game_over()

    def run(self) -> int:
        """Boucle principale. Retourne le gagnant (BLACK, WHITE ou EMPTY)."""
        while not self.is_over():
            self.play_turn()
<<<<<<< HEAD
        winner = self.board.get_winner()
        if self.view is not None:
            self.view.show_board(self.board)
            self.view.show_result(self.board.get_score(), winner)
=======

        winner = self.board.get_winner()

        if self.view is not None:
            self.view.show_board(self.board)
            self.view.show_result(self.board.get_score(), winner)

>>>>>>> ef4501c08295a27fe1d3b091eb7d112f1fcbc292
        return winner

    # --- Historique (extensions du sujet) ------------------------------------
    def save_history(self, path: str) -> None:
        """Écrit la liste des coups dans un fichier pour re-jouer la partie."""
<<<<<<< HEAD
        records = [
            {"color": record.color, "move": record.move, "flipped": record.flipped}
            for record in self.history
        ]
        Path(path).write_text(json.dumps(records, indent=2), encoding="utf-8")
=======
        with open(path, "w", encoding="utf-8") as f:
            for record in self.history:
                name = "B" if record.color == BLACK else "W"
                text = "pass" if record.move is None else ConsoleView.format_move(record.move)
                f.write(f"{name} {text}\n")
>>>>>>> ef4501c08295a27fe1d3b091eb7d112f1fcbc292
