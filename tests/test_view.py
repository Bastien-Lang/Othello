"""Tests de la vue : conversion de notation et affichage console."""
import pytest

from board import Board
from constants import BLACK, WHITE
from view import ConsoleView


def test_format_move():
    assert ConsoleView.format_move((0, 0)) == "a1"
    assert ConsoleView.format_move((2, 3)) == "d3"
    assert ConsoleView.format_move((7, 7)) == "h8"


@pytest.mark.parametrize("text, expected", [
    ("d3", (2, 3)), ("D3", (2, 3)), (" d3 ", (2, 3)),
    ("a1", (0, 0)), ("h8", (7, 7)),
])
def test_parse_valid(text, expected):
    assert ConsoleView.parse_move(text) == expected


@pytest.mark.parametrize("text", ["", "d", "d33", "d 3", "z1", "i1", "a9", "a0", "3d", "!!", "11", "a²"])
def test_parse_invalid(text):
    assert ConsoleView.parse_move(text) is None


def test_parse_and_format_are_inverse():
    for row in range(8):
        for col in range(8):
            assert ConsoleView.parse_move(ConsoleView.format_move((row, col))) == (row, col)


def test_show_board_initial(capsys):
    ConsoleView().show_board(Board())
    lines = [line for line in capsys.readouterr().out.splitlines() if line]
    assert lines[0] == "  a b c d e f g h"
    assert len(lines) == 9                      # en-tête + 8 lignes
    assert lines[4] == "4 . . . W B . . ."
    assert lines[5] == "5 . . . B W . . ."


def test_show_board_marks_legal_moves(capsys):
    board = Board()
    ConsoleView().show_board(board, board.get_legal_moves(WHITE))
    out = capsys.readouterr().out
    assert out.count("*") == 4                  # un marqueur par coup légal
    lines = [line for line in out.splitlines() if line]
    assert lines[3] == "3 . . . . * . . ."      # e3
    assert lines[4] == "4 . . . W B * . ."      # f4


def test_show_move(capsys):
    view = ConsoleView()
    view.show_move("Blanc", (2, 4))
    view.show_move("Noir", None)
    out = capsys.readouterr().out
    assert "Blanc joue e3." in out
    assert "Noir passe son tour." in out


@pytest.mark.parametrize("winner, expected", [
    (BLACK, "Victoire des Noirs"), (WHITE, "Victoire des Blancs"), (0, "Égalité"),
])
def test_show_result(capsys, winner, expected):
    ConsoleView().show_result({BLACK: 40, WHITE: 24}, winner)
    out = capsys.readouterr().out
    assert "Noir 40 - 24 Blanc" in out
    assert expected in out


def test_ask_move_returns_raw_text(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "  D3 ")
    assert ConsoleView().ask_move("Noir") == "  D3 "     # pas de validation ici
