"""Point d'entrée : configure les joueurs et lance une partie."""

from math import isfinite

from constants import BLACK, WHITE
from game import Game
from player import HumanPlayer, AIPlayer, RandomPlayer, Player
from view import ConsoleView


def read_input(prompt: str) -> str:
    """Permet de quitter aussi pendant la configuration de la partie."""
    answer = input(prompt).strip().lower()
    if answer in ("q", "quit", "quitter"):
        raise KeyboardInterrupt
    return answer


def choose_player(color: int, view: ConsoleView) -> Player:
    name = "Noir" if color == BLACK else "Blanc"
    view.show_message(f"\nJoueur {name} : 1. Humain | 2. MinMax | 3. Alpha-bêta | 4. Aléatoire")
    while True:
        choice = read_input("Votre choix (1-4) : ")
        if choice in ("1", "2", "3", "4"):
            break
        view.show_message("Choisissez un numéro de 1 à 4.")
    if choice == "1":
        return HumanPlayer(color, view, name=f"{name} (Humain)")
    if choice == "4":
        return RandomPlayer(color, name=f"{name} (Aléatoire)")

    while True:
        try:
            depth = int(read_input("Profondeur en demi-coups [2] (2 = un coup et une réponse) : ") or "2")
            if depth >= 1:
                break
        except ValueError:
            pass
        view.show_message("La profondeur doit être un entier supérieur ou égal à 1.")
    while True:
        try:
            seconds = float(read_input("Temps maximal par coup en secondes [2] (0 = sans limite) : ").replace(",", ".") or "2")
            if isfinite(seconds) and seconds >= 0:
                break
        except ValueError:
            pass
        view.show_message("Entrez un nombre fini positif ou nul.")
    algorithm, label = ("minimax", "MinMax") if choice == "2" else ("alphabeta", "Alpha-bêta")
    return AIPlayer(color, depth=depth, name=f"{name} ({label})",
                    time_limit=None if seconds == 0 else seconds, algorithm=algorithm)


def main() -> None:
    view = ConsoleView()
    try:
        view.show_message("Othello — choisissez chaque joueur. Tapez q pour quitter.")
        black = choose_player(BLACK, view)
        white = choose_player(WHITE, view)
        view.show_message(f"\n{black.name} contre {white.name}.")
        view.show_message("Les Blancs commencent. Les * indiquent les coups possibles.")
        Game(black, white, view).run()
    except (KeyboardInterrupt, EOFError):
        view.show_message("\nPartie interrompue.")


if __name__ == "__main__":
    main()
