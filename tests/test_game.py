"""Intégration des joueurs, de Minimax et de la boucle de jeu."""
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
