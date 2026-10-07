"""Point d'entrée : configure les joueurs et lance une partie."""

from constants import BLACK, WHITE
from game import Game
from player import HumanPlayer, RandomPlayer
from view import ConsoleView


def main() -> None:
    view = ConsoleView()
    black = HumanPlayer(BLACK, view, name="Noir")
    white = RandomPlayer(WHITE, name="Blanc")   # remplaçable par un autre HumanPlayer / une IA
    game = Game(black, white, view)
    game.run()


if __name__ == "__main__":
    main()
