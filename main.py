"""Point d'entrée : configure les joueurs et lance une partie."""

from constants import BLACK, WHITE
from game import Game
from player import HumanPlayer, AIPlayer
from view import ConsoleView


def main() -> None:
    view = ConsoleView()
    black = HumanPlayer(BLACK, view, name="Noir")
    white = AIPlayer(WHITE, depth=2, name="Blanc (MinMax)", time_limit=2.0)
    view.show_message("Othello : vous jouez les Noirs (B), MinMax joue les Blancs (W).")
    view.show_message("Les Blancs commencent. Les * indiquent les coups possibles. Tapez q pour quitter.")
    game = Game(black, white, view)
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        view.show_message("\nPartie interrompue.")


if __name__ == "__main__":
    main()
