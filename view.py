"""Affichage et saisie en console (séparés de la logique du jeu)."""

from __future__ import annotations

from board import Board
from constants import BLACK, WHITE, EMPTY, BOARD_SIZE, Move, MaybeMove

SYMBOLS = {EMPTY: ".", BLACK: "B", WHITE: "W"}
LEGAL_MARK = "*"
class ConsoleView:
    """Interface console. Pourra être remplacée par une GUI sans toucher au reste."""
    
    def show_board(self, board: Board, legal_moves: list[Move] | None = None) -> None:
        """Affiche la grille avec coordonnées (a-h / 1-8), éventuellement avec les coups légaux marqués."""
        legal = set(legal_moves or [])
        letters = " ".join(chr(ord("a") + c) for c in range(board.size)) #
        lines = ["  " + letters]

        for row in range(board.size):
            cells = []
            for col in range(board.size):
                if (row, col) in legal:
                    cells.append(LEGAL_MARK)
                else:
                    cells.append(SYMBOLS[board.get(row, col)])
            lines.append(f"{row + 1} " + " ".join(cells))

        print()
        print("\n".join(lines))

    def show_message(self, message: str) -> None:
        print(message)

    def show_move(self, player_name: str, move: MaybeMove) -> None:
        """Annonce le coup joué (ou le passage de tour)."""
        if move is None:
            print(f"{player_name} passe son tour.")
        else:
            print(f"{player_name} joue {self.format_move(move)}.")

    def show_result(self, score: dict[int, int], winner: int) -> None:
        print(f"Score final : Noir {score[BLACK]} - {score[WHITE]} Blanc")
        if winner == BLACK:
            print("Victoire des Noirs !")
        elif winner == WHITE:
            print("Victoire des Blancs !")
        else:
            print("Égalité !")

    def ask_move(self, player_name: str) -> str:
        """Lit la saisie brute de l'utilisateur (ex. 'd3')."""
        return input(f"{player_name}, votre coup (ex. d3) : ")

    # --- Conversion notation <-> indices -------------------------------------
    @staticmethod
    def parse_move(text: str) -> Move | None:
        """'d3' -> (2, 3). Retourne None si le format est invalide."""
        text = text.strip().lower() #retire les espaces et met en minuscule
        if len(text) != 2: #2 caractères 
            return None

        letter, digit = text[0], text[1]
        col = ord(letter) - ord("a")
        if not digit.isdigit():
            return None
        row = int(digit) - 1

        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return None
        return (row, col)

    @staticmethod
    def format_move(move: Move) -> str:
        """(2, 3) -> 'd3'."""
        row, col = move
        return f"{chr(ord('a') + col)}{row + 1}" #transforme les indices en notation alphanumérique
