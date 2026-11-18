"""NegaMax : chaque joueur maximise le score de son propre point de vue.

Sans élagage alpha-bêta. Le moteur parent fournit le délai, la recherche
progressive, les statistiques et la mémoire conservée entre les tours.
"""

from __future__ import annotations

from board import Board
from constants import MaybeMove
from minmax import MinimaxEngine, evaluate


class NegamaxEngine(MinimaxEngine):
    """Même raisonnement que MinMax, avec une seule maximisation."""

    def _negamax(self, board: Board, depth: int, current_color: int) -> float:
        """Retourner une valeur du point de vue du joueur au trait.

        depth compte les demi-coups ; une passe ne consomme aucun niveau.
        """
        self._check_time()
        self.stats.nodes += 1
        # Le point de vue est toujours current_color : pas besoin d'ai_color.
        key = (board.size, board.to_key(), current_color)
        cached = self._lookup(key, depth)
        if cached is not None:
            self.stats.cache_hits += 1
            return cached

        stored_depth = depth
        if board.is_game_over():
            stored_depth = float("inf")
            difference = evaluate(board, current_color)
            score = 0
            if difference > 0:
                score = float("inf")
            elif difference < 0:
                score = -float("inf")
        elif depth == 0:
            score = evaluate(board, current_color)
        else:
            moves = board.get_legal_moves(current_color)
            if not moves:
                # Même plateau, mais nouveau point de vue : inverser le signe.
                score = -self._negamax(board, depth, -current_color)
            else:
                score = -float("inf")
                for move in moves:
                    self._check_time()
                    child = board.copy()
                    child.apply_move(move, current_color)
                    # L'enfant donne le score adverse. Son opposé est le nôtre.
                    value = -self._negamax(child, depth - 1, -current_color)
                    score = max(score, value)

        # Un calcul interrompu ne doit pas être mémorisé comme terminé.
        self._check_time()
        self._store(key, stored_depth, score)
        return score

    def _best_move(self, board: Board, moves: list, ai_color: int,
                   depth: int) -> tuple[MaybeMove, float]:
        """Choisir le premier meilleur coup, même si tous valent -inf."""
        best_move = moves[0]
        best_score = -float("inf")
        for move in moves:
            self._check_time()
            child = board.copy()
            child.apply_move(move, ai_color)
            score = -self._negamax(child, depth - 1, -ai_color)
            if score > best_score:
                best_move, best_score = move, score
        self._check_time()
        return best_move, best_score


def negamax(board: Board, depth: int, current_color: int) -> float:
    """Évaluer une position pour current_color, sans délai et avec un cache neuf."""
    if not isinstance(depth, int) or depth < 0:
        raise ValueError("La profondeur doit être un entier positif ou nul.")
    return NegamaxEngine()._negamax(board, depth, current_color)


def choose_negamax_move(board: Board, ai_color: int, depth: int = 2,
                        *, time_limit: float | None = None,
                        engine: NegamaxEngine | None = None) -> MaybeMove:
    """Retourner seulement le coup ; réutiliser engine pour garder sa mémoire."""
    if engine is None:
        engine = NegamaxEngine()
    return engine.search(board, ai_color, depth, time_limit).move
