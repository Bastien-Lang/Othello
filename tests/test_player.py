"""Tests des joueurs : contrat de Player, RandomPlayer, HumanPlayer, AIPlayer."""
import pytest

from board import Board
from constants import BLACK, WHITE, EMPTY
from player import Player, HumanPlayer, RandomPlayer, AIPlayer
from view import ConsoleView


def blocked_board() -> Board:
    """Position où Noir n'a aucun coup (et Blanc peut jouer en (0, 2))."""
    board = Board()
    board.grid.fill(EMPTY)
    board.grid[0, 0] = WHITE
    board.grid[0, 1] = BLACK
    return board


def test_player_is_abstract():
    with pytest.raises(TypeError):
        Player(WHITE)


def test_random_player_plays_legal_moves():
    board = Board()
    player = RandomPlayer(WHITE, "Aléa")
    for _ in range(30):
        assert player.choose_move(board) in board.get_legal_moves(WHITE)


def test_random_player_passes_when_blocked():
    assert RandomPlayer(BLACK, "N").choose_move(blocked_board()) is None


def test_human_retries_until_legal_move(monkeypatch, capsys):
    # 1re saisie : format invalide, 2e : bien formée mais illégale, 3e : légale
    answers = iter(["zz", "a1", "e3"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    player = HumanPlayer(WHITE, ConsoleView(), "Blanc")
    assert player.choose_move(Board()) == (2, 4)
    out = capsys.readouterr().out
    assert "Format invalide" in out
    assert "pas légal" in out
    assert "Coups possibles" in out


@pytest.mark.parametrize("quit_word", ["q", "Q", "quit", "quitter"])
def test_human_can_quit(monkeypatch, quit_word):
    monkeypatch.setattr("builtins.input", lambda _prompt: quit_word)
    with pytest.raises(KeyboardInterrupt):
        HumanPlayer(WHITE, ConsoleView(), "Blanc").choose_move(Board())


def test_human_passes_when_blocked():
    assert HumanPlayer(BLACK, ConsoleView(), "N").choose_move(blocked_board()) is None


def test_ai_player_returns_legal_move_and_stats():
    board = Board()
    player = AIPlayer(WHITE, depth=2, algorithm="alphabeta")
    assert player.choose_move(board) in board.get_legal_moves(WHITE)
    assert player.last_result.stats.nodes > 0


def test_ai_player_rejects_bad_arguments():
    with pytest.raises(ValueError):
        AIPlayer(WHITE, depth=0)
    with pytest.raises(ValueError):
        AIPlayer(WHITE, algorithm="inconnu")
