<<<<<<< HEAD
﻿"""Intégration des joueurs, de Minimax et de la boucle de jeu."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from board import Board
from constants import BLACK, WHITE, EMPTY
from game import Game
from main import main
from player import AIPlayer, HumanPlayer
from view import ConsoleView

class GameTests(unittest.TestCase):
    def make_game(self):
        return Game(AIPlayer(BLACK, depth=1), AIPlayer(WHITE, depth=1))

    def test_first_turn(self):
        game = self.make_game()
        self.assertEqual(game.current_player.color, WHITE)
        game.play_turn()
        self.assertEqual(game.current_color, BLACK)
        self.assertEqual(game.history[0].color, WHITE)
        self.assertEqual(game.board.get_score(), {BLACK: 1, WHITE: 4})

    def test_pass_then_end(self):
        game = self.make_game()
        game.board = Board(4)
        game.board.grid.fill(BLACK)
        game.board.grid[0, 1] = WHITE
        game.board.grid[0, 2] = EMPTY
        with patch.object(game.current_player, 'choose_move') as choose:
            game.play_turn()
            choose.assert_not_called()
        self.assertIsNone(game.history[0].move)
        self.assertEqual(game.run(), BLACK)
        self.assertEqual(len(game.history), 2)
        game.play_turn()
        self.assertEqual(len(game.history), 2)

    def test_invalid_move_does_not_advance_turn(self):
        game = self.make_game()
        before = game.board.to_key()
        with patch.object(game.current_player, 'choose_move', return_value=None):
            with self.assertRaises(ValueError):
                game.play_turn()
        self.assertEqual(game.board.to_key(), before)
        self.assertEqual(game.current_color, WHITE)
        self.assertEqual(game.history, [])

    def test_complete_minimax_game_and_history(self):
        game = self.make_game()
        winner = game.run()
        self.assertTrue(game.is_over())
        self.assertEqual(winner, game.board.get_winner())
        replay = Board()
        color = WHITE
        for record in game.history:
            self.assertEqual(record.color, color)
            if record.move is None:
                self.assertFalse(replay.has_legal_move(color))
            else:
                self.assertEqual(replay.apply_move(record.move, color), record.flipped)
            color = -color
        self.assertEqual(replay.to_key(), game.board.to_key())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'partie.json'
            game.save_history(str(path))
            self.assertEqual(len(json.loads(path.read_text())), len(game.history))

    def test_human_retries_invalid_input(self):
        view = Mock(spec=ConsoleView)
        view.parse_move = ConsoleView.parse_move
        view.format_move = ConsoleView.format_move
        view.ask_move.side_effect = ['x', 'a1', 'e3']
        player = HumanPlayer(WHITE, view)
        self.assertEqual(player.choose_move(Board()), (2, 4))

    def test_main_starts_minimax_then_accepts_quit(self):
        with patch('builtins.input', return_value='q'), patch('builtins.print') as output:
            main()
        messages = [str(call.args[0]) for call in output.call_args_list if call.args]
        self.assertTrue(any('Blanc (MinMax) joue' in message for message in messages))
        self.assertTrue(any('Partie interrompue' in message for message in messages))
=======
"""Tests de la partie complète."""

import pytest

from constants import BLACK, WHITE, EMPTY
from game import Game
from player import Player, RandomPlayer


class BadPlayer(Player):
    """Joueur volontairement fautif : propose toujours une case illégale."""
    def choose_move(self, board):
        return (0, 0)


def play_random_game() -> Game:
    game = Game(RandomPlayer(BLACK, "N"), RandomPlayer(WHITE, "B"))   # sans vue
    game.run()
    return game


def test_random_games_finish():
    for _ in range(50):
        game = play_random_game()
        assert game.is_over()
        assert game.board.get_winner() in (BLACK, WHITE, EMPTY)


def test_white_plays_first():
    assert play_random_game().history[0].color == WHITE


def test_players_alternate_except_after_pass():
    game = play_random_game()
    for prev, cur in zip(game.history, game.history[1:]):
        assert prev.color != cur.color     # même une passe change le joueur


def test_disc_count_matches_history():
    # Chaque coup réel ajoute exactement 1 pion, les passes n'en ajoutent aucun
    for _ in range(50):
        game = play_random_game()
        real_moves = sum(1 for r in game.history if r.move is not None)
        assert game.board.count(BLACK) + game.board.count(WHITE) == 4 + real_moves


def test_pass_turn_is_recorded():
    game = Game(RandomPlayer(BLACK, "N"), RandomPlayer(WHITE, "B"))
    # Position fabriquée : Noir n'a aucun coup, Blanc peut jouer en (0, 2)
    game.board.grid.fill(EMPTY)
    game.board.grid[0, 0] = WHITE
    game.board.grid[0, 1] = BLACK
    game.current_color = BLACK

    game.play_turn()

    assert game.history[-1].color == BLACK
    assert game.history[-1].move is None
    assert game.current_color == WHITE


def test_invalid_move_raises():
    game = Game(BadPlayer(BLACK, "x"), BadPlayer(WHITE, "y"))
    with pytest.raises(ValueError):
        game.play_turn()


def test_game_with_view_prints_result(capsys):
    from view import ConsoleView
    Game(RandomPlayer(BLACK, "N"), RandomPlayer(WHITE, "B"), ConsoleView()).run()
    assert "Score final" in capsys.readouterr().out


def test_save_history(tmp_path):
    game = play_random_game()
    path = tmp_path / "partie.txt"
    game.save_history(str(path))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(game.history)
    assert lines[0].startswith("W ")
>>>>>>> ef4501c08295a27fe1d3b091eb7d112f1fcbc292
