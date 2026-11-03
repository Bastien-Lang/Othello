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
