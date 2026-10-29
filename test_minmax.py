"""Tests Minimax : python -m unittest test_minmax -v (Python avec NumPy)."""

import unittest
from unittest.mock import patch

from board import Board
from constants import BLACK, WHITE
from player import AIPlayer
from minmax import MinimaxEngine, choose_minimax_move, minimax


def reference(board, depth, turn, ai):
    """Oracle sans mémoire ni délai pour comparer les valeurs à faible profondeur."""
    # Cette version volontairement simple sert de point de comparaison :
    # les optimisations du moteur doivent conserver le résultat de Minimax.
    # Elle ne suffit pas à prouver toutes les règles ; les cas particuliers
    # ci-dessous vérifient aussi directement des résultats connus.
    if board.is_game_over():
        difference = board.count(ai) - board.count(-ai)
        return 0 if difference == 0 else (float('inf') if difference > 0 else -float('inf'))
    if depth == 0:
        return board.count(ai) - board.count(-ai)
    moves = board.get_legal_moves(turn)
    if not moves:
        return reference(board, depth, -turn, ai)
    values = []
    for move in moves:
        child = board.copy()
        child.apply_move(move, turn)
        values.append(reference(child, depth - 1, -turn, ai))
    return (max if turn == ai else min)(values)


class MinimaxTests(unittest.TestCase):
    def test_matches_reference_and_preserves_board(self):
        """Vérifie le score optimal, le coup associé et l'intégrité du plateau."""
        # Un plateau 4x4 accélère l'exploration exhaustive. Après un premier
        # coup, on compare les deux couleurs aux profondeurs 1, 2 et 3.
        # On vérifie aussi la valeur du coup réellement retourné : obtenir
        # le bon score sans retourner le bon coup ne suffirait pas.
        board = Board(4)
        board.apply_move(board.get_legal_moves(WHITE)[0], WHITE)
        original = board.to_key()
        for color in (BLACK, WHITE):
            for depth in (1, 2, 3):
                result = MinimaxEngine().search(board, color, depth)
                self.assertEqual(result.score, reference(board, depth, color, color))
                child = board.copy()
                child.apply_move(result.move, color)
                self.assertEqual(reference(child, depth - 1, -color, color), result.score)
                self.assertEqual(result.stats.completed_depth, depth)
        self.assertEqual(board.to_key(), original)

    def test_terminal_results_at_depth_zero(self):
        """Vérifie que la fin de partie prime sur la limite de profondeur."""
        # Plateau rempli de noirs : victoire noire (+inf), défaite blanche
        # (-inf), même à depth=0. Puis moitié blanc/moitié noir : égalité (0).
        # Sur un plateau plein, aucun coup ne doit être proposé.
        board = Board(4)
        board.grid.fill(BLACK)
        self.assertEqual(minimax(board, 0, WHITE, BLACK), float('inf'))
        self.assertEqual(minimax(board, 0, BLACK, WHITE), -float('inf'))
        board.grid[:2, :] = WHITE
        self.assertEqual(minimax(board, 0, BLACK, WHITE), 0)
        self.assertIsNone(choose_minimax_move(board, WHITE))

    def test_pass_and_forced_loss(self):
        """Vérifie une passe obligatoire puis un coup légal malgré une défaite."""
        # Premier scénario : les blancs sont bloqués, mais les noirs peuvent
        # encore jouer. La recherche doit passer le tour et voir la défaite.
        # Deuxième scénario : les blancs ont un coup légal qui perd ; ils
        # doivent le jouer, et non retourner None parce que son score est -inf.
        board = Board(4)
        board.grid.fill(BLACK)
        board.grid[0, 1] = WHITE
        board.grid[0, 2] = 0
        self.assertFalse(board.is_game_over())
        self.assertIsNone(choose_minimax_move(board, WHITE))
        self.assertEqual(minimax(board, 1, WHITE, WHITE), -float('inf'))
        # Une position différente où les blancs peuvent jouer mais perdent.
        board.grid.fill(BLACK)
        board.grid[0, 0] = WHITE
        board.grid[0, 2] = 0
        result = MinimaxEngine().search(board, WHITE, 1)
        self.assertEqual(result.move, (0, 2))
        self.assertEqual(result.score, -float('inf'))

    def test_cache_reuse_and_separation_of_depth_and_perspective(self):
        """Vérifie la réutilisation du cache sans changer les résultats."""
        # Une seconde recherche identique doit retrouver des entrées, visiter
        # moins de nœuds et choisir le même coup avec le même score.
        # On change ensuite profondeur et couleur : le cache ne doit pas
        # remplacer leur résultat par une valeur calculée dans un autre contexte.
        board = Board(4)
        engine = MinimaxEngine()
        first = engine.search(board, WHITE, 3)
        second = engine.search(board, WHITE, 3)
        self.assertEqual((first.move, first.score), (second.move, second.score))
        self.assertGreater(second.stats.cache_hits, 0)
        self.assertLess(second.stats.nodes, first.stats.nodes)
        for color in (BLACK, WHITE):
            result = engine.search(board, color, 1)
            self.assertEqual(result.score, reference(board, 1, color, color))

    def test_reuse_on_a_later_turn(self):
        """Vérifie que la mémoire sert encore après deux coups réellement joués."""
        # On analyse quatre demi-coups, puis joue un coup blanc et un noir.
        # À profondeur 2, des sous-arbres correspondent à l'analyse précédente.
        # Le moteur persistant doit en profiter et rester équivalent à un neuf.
        board = Board(4)
        engine = MinimaxEngine()
        first = engine.search(board, WHITE, 4)
        board.apply_move(first.move, WHITE)
        moves = board.get_legal_moves(BLACK)
        self.assertTrue(moves)
        board.apply_move(moves[0], BLACK)
        later = engine.search(board, WHITE, 2)
        self.assertGreater(later.stats.cache_hits, 0)
        fresh = MinimaxEngine().search(board, WHITE, 2)
        self.assertEqual((later.move, later.score), (fresh.move, fresh.score))

    def test_zero_budget_returns_legal_fallback(self):
        """Vérifie le secours lorsque le délai ne permet aucune recherche."""
        # Le moteur doit retourner un coup légal, annoncer une interruption
        # et profondeur=0. score=None signifie que le secours n'a pas été
        # évalué : ce n'est ni une égalité ni une victoire annoncée.
        board = Board()
        result = MinimaxEngine().search(board, WHITE, 4, time_limit=0)
        self.assertIn(result.move, board.get_legal_moves(WHITE))
        self.assertIsNone(result.score)
        self.assertEqual(result.stats.completed_depth, 0)
        self.assertTrue(result.stats.timed_out)

    def test_timeout_keeps_last_complete_iteration(self):
        """Vérifie qu'une interruption abandonne seulement l'itération partielle."""
        # On calcule d'abord le résultat attendu à profondeur 1. Une fausse
        # horloge expire ensuite au début de la profondeur 2 : on doit garder
        # le coup ET le score du niveau 1 et ne pas mémoriser de parent incomplet.
        # Une reprise sans délai vérifie que cette mémoire reste utilisable.
        board = Board(4)
        expected = MinimaxEngine().search(board, WHITE, 1)
        clock = [0.0]
        engine = MinimaxEngine()
        real_minimax = engine._minimax

        def expire_in_second_iteration(*args, **kwargs):
            # Expire pendant le premier sous-arbre du niveau 2, après qu'une
            # itération complète ait publié son résultat. Pas de sleep fragile.
            if engine.stats.completed_depth == 1:
                clock[0] = 2.0
            return real_minimax(*args, **kwargs)

        with patch('minmax.perf_counter', side_effect=lambda: clock[0]), \
                patch.object(engine, '_minimax', side_effect=expire_in_second_iteration):
            result = engine.search(board, WHITE, 4, time_limit=1.0)
        self.assertTrue(result.stats.timed_out)
        self.assertEqual(result.stats.completed_depth, 1)
        self.assertEqual((result.move, result.score), (expected.move, expected.score))
        # Seuls les nœuds complets à profondeur 0 ont pu être enregistrés.
        self.assertTrue(all(key[-1] == 0 for key in engine.table))
        resumed = engine.search(board, WHITE, 2)
        self.assertEqual(resumed.score, reference(board, 2, WHITE, WHITE))

    def test_iterative_deepening_reaches_requested_depth(self):
        """Vérifie la progression jusqu'au maximum quand le délai n'expire pas."""
        # L'horloge figée supprime la dépendance à la vitesse de l'ordinateur.
        # Le moteur doit terminer le niveau 3 et obtenir la valeur de référence,
        # sans annoncer de time-out. Ce test ne mesure pas un temps réel.
        board = Board(4)
        with patch('minmax.perf_counter', return_value=0.0):
            result = MinimaxEngine().search(board, WHITE, 3, time_limit=1)
        self.assertFalse(result.stats.timed_out)
        self.assertEqual(result.stats.completed_depth, 3)
        self.assertEqual(result.score, reference(board, 3, WHITE, WHITE))

    def test_memory_limit_and_independent_players(self):
        """Vérifie la capacité du cache, son isolation entre IA et sa remise à zéro."""
        # Un cache de deux entrées force les suppressions : elles ne doivent
        # pas changer le résultat. Deux joueurs doivent ensuite posséder des
        # dictionnaires différents ; réfléchir avec l'un ne remplit pas l'autre.
        # clear() doit vider le moteur et effacer son dernier résultat.
        board = Board(4)
        engine = MinimaxEngine(max_entries=2)
        result = engine.search(board, WHITE, 3)
        self.assertLessEqual(len(engine.table), 2)
        self.assertEqual(result.score, reference(board, 3, WHITE, WHITE))
        first, second = AIPlayer(WHITE), AIPlayer(BLACK)
        self.assertIsNot(first.engine.table, second.engine.table)
        self.assertIn(first.choose_move(board), board.get_legal_moves(WHITE))
        self.assertTrue(first.engine.table)
        self.assertFalse(second.engine.table)
        self.assertIsNotNone(first.last_result)
        first.engine.clear()
        self.assertFalse(first.engine.table)
        self.assertIsNone(first.engine.last_result)

    def test_invalid_parameters(self):
        """Vérifie le refus des profondeurs, délais et capacités invalides."""
        # Le choix de coup exige une profondeur entière >=1 ; minimax accepte
        # 0 mais pas -1. Les délais négatifs, infinis et NaN sont refusés.
        # Un cache de capacité zéro n'aurait aucune entrée à retirer : refusé.
        for depth in (0, -1, 1.5):
            with self.assertRaises(ValueError):
                MinimaxEngine().search(Board(), WHITE, depth)
        for delay in (-1, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                MinimaxEngine().search(Board(), WHITE, time_limit=delay)
        with self.assertRaises(ValueError):
            minimax(Board(), -1, WHITE, WHITE)
        with self.assertRaises(ValueError):
            MinimaxEngine(max_entries=0)


if __name__ == '__main__':
    unittest.main()
