"""Minimax avec élagage alpha-bêta et mémoire des valeurs exactes.

Même évaluation que Minimax ; délai et statistiques hérités de MinimaxEngine."""

from __future__ import annotations

from board import Board
from constants import MaybeMove
from minmax import MinimaxEngine, evaluate


class AlphaBetaEngine(MinimaxEngine):
    """Coupe les branches inutiles lorsque alpha >= beta.
    
    MAX relève alpha, MIN abaisse beta. Le moteur parent gère le délai,
    les statistiques et la progression des profondeurs."""

    def _minimax(self, board: Board, depth: int,
                 current_color: int, ai_color: int) -> float:
        """Évalue la position avec une fenêtre complète [-inf, +inf]."""
        return self._alphabeta(board, depth, current_color, ai_color,
                               -float("inf"), float("inf"))

    def _alphabeta(self, board: Board, depth: int, current_color: int,
                   ai_color: int, alpha: float, beta: float) -> float:
        """Explore les coups, coupe les branches inutiles et mémorise le résultat.
        
        current_color alterne ; ai_color reste le point de vue du score.
        depth compte les demi-coups restants, sans compter les passes."""
        self._check_time()
        self.stats.nodes += 1
        key = (board.size, board.to_key(), current_color, ai_color, depth)
        if key in self.table:
            self.stats.cache_hits += 1
            return self.table[key]

        initial_alpha, initial_beta = alpha, beta
        leaf = False
        if board.is_game_over():
            # La fin de partie prime sur la limite de profondeur.
            difference = evaluate(board, ai_color)
            if difference > 0:
                score = float("inf")
            elif difference < 0:
                score = -float("inf")
            else:
                score = 0
            leaf = True
        elif depth == 0:
            score = evaluate(board, ai_color)
            leaf = True
        else:
            moves = board.get_legal_moves(current_color)
            if not moves:
                # Passer le tour sans réduire la profondeur.
                score = self._alphabeta(board, depth, -current_color,
                                        ai_color, alpha, beta)
            else:
                maximizing = current_color == ai_color
                score = -float("inf") if maximizing else float("inf")
                for move in moves:
                    self._check_time()
                    child = board.copy()
                    child.apply_move(move, current_color)
                    value = self._alphabeta(child, depth - 1, -current_color,
                                            ai_color, alpha, beta)
                    if maximizing:
                        score = max(score, value)
                        alpha = max(alpha, score)
                    else:
                        score = min(score, value)
                        beta = min(beta, score)
                    if alpha >= beta:
                        # Les enfants restants ne peuvent améliorer la décision.
                        break

        self._check_time()  # Une recherche interrompue n'enregistre pas ce nœud.
        # Hors de la fenêtre initiale, le score peut n'être qu'une borne.
        # Pour simplifier le cache, on garde uniquement les valeurs exactes.
        if leaf or initial_alpha < score < initial_beta:
            if len(self.table) >= self.max_entries and key not in self.table:
                del self.table[next(iter(self.table))]
            self.table[key] = score
        return score

    def _best_move(self, board: Board, moves: list, ai_color: int,
                   depth: int) -> tuple[MaybeMove, float]:
        """Renvoie le meilleur coup et son score à une profondeur donnée.
        
        Le meilleur score devient alpha pour les coups suivants.
        À égalité, le premier coup est conservé."""
        best_move = moves[0]  # Coup légal même si tous les coups perdent.
        best_score = -float("inf")
        for move in moves:
            self._check_time()
            child = board.copy()
            child.apply_move(move, ai_color)
            score = self._alphabeta(child, depth - 1, -ai_color, ai_color,
                                    best_score, float("inf"))
            if score > best_score:
                best_move = move
                best_score = score
            if best_score == float("inf"):
                break  # Une victoire certaine ne peut pas être améliorée.
        self._check_time()
        return best_move, best_score


def alphabeta(board: Board, depth: int, current_color: int, ai_color: int) -> float:
    """Évalue une position à profondeur fixe, avec un moteur neuf sans délai."""
    if not isinstance(depth, int) or depth < 0:
        raise ValueError("La profondeur doit être un entier positif ou nul.")
    return AlphaBetaEngine()._minimax(board, depth, current_color, ai_color)


def choose_alphabeta_move(board: Board, ai_color: int, depth: int = 2,
                          *, time_limit: float | None = None,
                          engine: AlphaBetaEngine | None = None) -> MaybeMove:
    """Renvoie un coup ou None si aucun coup légal.
    
    Réutiliser engine conserve le cache ; time_limit est en secondes."""
    if engine is None:
        engine = AlphaBetaEngine()
    return engine.search(board, ai_color, depth, time_limit).move
