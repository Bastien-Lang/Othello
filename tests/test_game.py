"""Parties et choix des adversaires utiles au TP."""
import pytest
from unittest.mock import patch

from board import Board
from constants import BLACK, WHITE, EMPTY
from game import Game
from main import main
from player import AIPlayer


@pytest.mark.parametrize('black_algo, white_algo', [
    ('minimax', 'minimax'), ('alphabeta', 'alphabeta'),
    ('minimax', 'alphabeta'), ('alphabeta', 'minimax'),
])
def test_complete_ai_games(black_algo, white_algo):
    """Vérifie la fin et la légalité d'une partie pour chaque paire d'IA."""
    # Jouer chaque paire d’IA puis reconstruire la partie depuis son historique.
    black = AIPlayer(BLACK, depth=1, algorithm=black_algo)
    white = AIPlayer(WHITE, depth=1, algorithm=white_algo)
    assert black.engine.table is not white.engine.table
    game = Game(black, white)
    winner = game.run()
    assert game.is_over()
    assert winner == game.board.get_winner()
    replay = Board()
    turn = WHITE
    for record in game.history:
        assert record.color == turn
        if record.move is None:
            assert not replay.has_legal_move(turn)
        else:
            assert replay.apply_move(record.move, turn) == record.flipped
        turn = -turn
    assert replay.to_key() == game.board.to_key()


def test_forced_pass_then_end():
    """Vérifie l'enregistrement d'une passe puis du dernier coup gagnant."""
    # Bloquer Blanc et laisser à Noir le dernier coup gagnant.
    game = Game(AIPlayer(BLACK), AIPlayer(WHITE))
    game.board.grid.fill(BLACK)
    game.board.grid[0, 1] = WHITE
    game.board.grid[0, 2] = EMPTY
    game.play_turn()
    assert game.history[0].move is None
    assert game.current_color == BLACK
    assert game.run() == BLACK
    assert len(game.history) == 2


@pytest.mark.parametrize('black_choice, white_choice', [('2', '2'), ('3', '3'), ('2', '3')])
def test_menu_launches_ai_match(capsys, black_choice, white_choice):
    """Vérifie que les choix du menu permettent d'aller jusqu'au score final."""
    # Chaque appel à input reçoit la réponse suivante de la liste.
    answers = [black_choice, '1', '0', white_choice, '1', '0']
    with patch('builtins.input', side_effect=answers):
        main()
    assert 'Score final' in capsys.readouterr().out


@pytest.mark.parametrize('human_color', [BLACK, WHITE])
def test_menu_human_against_ai(capsys, human_color):
    """Vérifie qu'un humain peut choisir chaque couleur et quitter à son tour."""
    # Choisir chaque couleur humaine, puis simuler q au premier tour.
    if human_color == BLACK:
        answers = ['1', '3', '1', '0', 'q']
    else:
        answers = ['2', '1', '0', '1', 'q']
    with patch('builtins.input', side_effect=answers):
        main()
    output = capsys.readouterr().out
    assert 'Coups possibles' in output
    assert 'Partie interrompue' in output
