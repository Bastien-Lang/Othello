"""Tests des règles (à lancer avec pytest depuis le dossier othello/)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from board import Board
from constants import BLACK, WHITE


def test_initial_position():
    """4 pions au centre, 2 de chaque couleur."""
    raise NotImplementedError


def test_initial_legal_moves():
    """4 coups légaux au départ pour le joueur qui commence."""
    raise NotImplementedError


def test_apply_move_flips_discs():
    raise NotImplementedError


def test_illegal_move_raises():
    raise NotImplementedError


def test_pass_when_no_legal_move():
    raise NotImplementedError


def test_game_over_and_winner():
    raise NotImplementedError


def test_copy_is_independent():
    raise NotImplementedError
