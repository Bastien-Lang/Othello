"""Tests de la vue : conversion de notation et affichage."""

from board import Board
from constants import WHITE
from view import ConsoleView


def test_format_move():
    assert ConsoleView.format_move((0, 0)) == "a1"
    assert ConsoleView.format_move((2, 3)) == "d3"
    assert ConsoleView.format_move((7, 7)) == "h8"


def test_parse_valid():
    assert ConsoleView.parse_move("d3") == (2, 3)
    assert ConsoleView.parse_move(" D3 ") == (2, 3)
    assert ConsoleView.parse_move("a1") == (0, 0)
    assert ConsoleView.parse_move("h8") == (7, 7)


def test_parse_invalid():
    for bad in ["", "d", "d33", "z1", "a9", "a0", "3d", "!!"]:
        assert ConsoleView.parse_move(bad) is None


def test_parse_and_format_are_inverse():
    for row in range(8):
        for col in range(8):
            move = (row, col)
            assert ConsoleView.parse_move(ConsoleView.format_move(move)) == move


def test_show_board_marks_legal_moves(capsys):
    b = Board()
    ConsoleView().show_board(b, b.get_legal_moves(WHITE))
    out = capsys.readouterr().out.splitlines()
    out = [line for line in out if line]          # on ignore la ligne vide
    assert out[0] == "  a b c d e f g h"
    assert out[3] == "3 . . . . * . . ."           # e3
    assert out[4] == "4 . . . W B * . ."           # f4


def test_show_move(capsys):
    view = ConsoleView()
    view.show_move("Blanc", (2, 4))
    view.show_move("Noir", None)
    out = capsys.readouterr().out
    assert "Blanc joue e3." in out
    assert "Noir passe son tour." in out
