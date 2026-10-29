"""Minimax avec profondeur maximale, délai, mémoire et statistiques.

depth compte les demi-coups : 2 = un coup de l'IA puis une réponse adverse
(profondeur 1 du TP). Une passe ne consomme pas de profondeur.
Chaque AIPlayer garde son moteur entre les tours, avec sa propre mémoire.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from time import perf_counter

from board import Board
from constants import MaybeMove


def evaluate(board: Board, ai_color: int) -> int:
    """Avance en pions : positive pour l'IA, négative pour son adversaire."""
    # BLACK=1, WHITE=-1 : -ai_color désigne la couleur adverse.
    # Une avance dans une partie en cours ne garantit pas la victoire.
    return board.count(ai_color) - board.count(-ai_color)


@dataclass
class SearchStats:
    """Compteurs d'une décision, cumulés sur toutes ses itérations."""

    nodes: int = 0              # Appels récursifs, accès au cache compris.
    cache_hits: int = 0         # Valeurs retrouvées sans recalcul.
    completed_depth: int = 0    # Dernière profondeur entièrement terminée.
    elapsed_seconds: float = 0.0
    timed_out: bool = False


@dataclass
class SearchResult:
    """Résultat : coup, valeur et mesures. None signifie une valeur inconnue."""

    move: MaybeMove
    score: float | None
    stats: SearchStats


class SearchTimeout(Exception):
    """Interrompt une recherche trop longue, pas la partie."""


class MinimaxEngine:
    """Organise Minimax et conserve les positions analysées entre les tours.

    Le moteur contient directement mémoire, délai et statistiques : il n'y a
    plus d'objet de contexte à transmettre à chaque appel récursif.
    Un moteur sert à une seule recherche à la fois ; chaque IA a le sien.
    """

    def __init__(self, max_entries: int = 100_000) -> None:
        if not isinstance(max_entries, int) or max_entries < 1:
            raise ValueError("La capacité du cache doit être un entier positif.")
        self.max_entries = max_entries
        self.table = {}
        self.deadline = None
        self.stats = SearchStats()
        self.last_result = None

    def clear(self) -> None:
        """Repartir sans analyses précédentes, par exemple pour une comparaison."""
        self.table.clear()
        self.deadline = None
        self.stats = SearchStats()
        self.last_result = None

    def _check_time(self) -> None:
        # L'horloge mesure une durée, indépendamment de l'heure civile.
        if self.deadline is not None and perf_counter() >= self.deadline:
            raise SearchTimeout

    def _minimax(self, board: Board, depth: int,
                 current_color: int, ai_color: int) -> float:
        """Calcule une valeur : ai_color reste fixe, current_color alterne."""
        self._check_time()
        self.stats.nodes += 1

        # La grille seule ne suffit pas : joueur au trait, point de vue et
        # profondeur restante peuvent changer le résultat. On réutilise une
        # valeur seulement au même horizon. L'évaluation reste toujours absolue.
        key = (board.size, board.to_key(), current_color, ai_color, depth)
        if key in self.table:
            self.stats.cache_hits += 1
            return self.table[key]

        if board.is_game_over():
            difference = evaluate(board, ai_color)
            score = 0
            if difference > 0:
                score = float("inf")
            elif difference < 0:
                score = -float("inf")
            # C'est is_game_over() qui constate la fin. Les infinis servent
            # à classer une victoire/défaite certaine au-dessus/en dessous
            # d'une simple estimation. Toutes les victoires ont même valeur.
        elif depth == 0:
            # Partie encore en cours : on estime, sans prétendre savoir qui gagne.
            score = evaluate(board, ai_color)
        else:
            moves = board.get_legal_moves(current_color)
            if not moves:
                # Passe : autre joueur, même plateau et même profondeur.
                # Si les deux étaient bloqués, le test de fin aurait déjà servi.
                score = self._minimax(board, depth, -current_color, ai_color)
            else:
                maximizing = current_color == ai_color
                score = -float("inf") if maximizing else float("inf")
                # Une seule boucle pour les deux joueurs : seules les opérations
                # max et min diffèrent. Ces infinis initialisent la comparaison,
                # ils ne désignent pas ici un résultat terminal déjà constaté.
                for move in moves:
                    self._check_time()
                    child = board.copy()
                    child.apply_move(move, current_color)
                    value = self._minimax(child, depth - 1, -current_color, ai_color)
                    if maximizing:
                        score = max(score, value)
                    else:
                        score = min(score, value)

        # Point unique de sauvegarde : un nœud interrompu n'arrive jamais ici.
        # Les enfants terminés restent utilisables ; aucun parent partiel n'est
        # présenté comme exact. Exact signifie « pour cet horizon de recherche ».
        self._check_time()
        if len(self.table) >= self.max_entries and key not in self.table:
            del self.table[next(iter(self.table))]  # Retirer la plus ancienne entrée.
        self.table[key] = score
        return score

    def _best_move(self, board: Board, moves: list, ai_color: int,
                   depth: int) -> tuple[MaybeMove, float]:
        """Examiner tous les coups à UNE profondeur, ou lever SearchTimeout."""
        # Garder un coup légal même si toutes les possibilités valent -inf.
        best_move = moves[0]
        best_score = -float("inf")
        for move in moves:
            self._check_time()
            child = board.copy()
            child.apply_move(move, ai_color)
            # Le premier coup a déjà consommé un niveau ; l'adversaire joue.
            score = self._minimax(child, depth - 1, -ai_color, ai_color)
            if score > best_score:  # En cas d'égalité, garder le premier coup.
                best_move, best_score = move, score
        self._check_time()
        return best_move, best_score

    def search(self, board: Board, ai_color: int, depth: int = 2,
               time_limit: float | None = None) -> SearchResult:
        """Choisir un coup ; délai en secondes, None pour une profondeur fixe.

        Le contrôle du temps est coopératif : une opération Board en cours
        finit avant le prochain contrôle, donc un léger dépassement est possible.
        """
        if not isinstance(depth, int) or depth < 1:
            raise ValueError("La profondeur de choix doit être un entier positif.")
        if time_limit is not None and (not isfinite(time_limit) or time_limit < 0):
            raise ValueError("Le délai doit être fini et positif ou nul, ou None.")

        started = perf_counter()
        self.deadline = None if time_limit is None else started + time_limit
        self.stats = SearchStats()  # Nouveaux compteurs ; la table est conservée.
        moves = board.get_legal_moves(ai_color)
        best_move = moves[0] if moves else None
        best_score = None

        if moves:
            # Sans délai : directement la profondeur demandée.
            # Avec délai : 1, 2, 3... pour disposer rapidement d'un choix complet.
            depths = [depth] if time_limit is None else range(1, depth + 1)
            try:
                for current_depth in depths:
                    # Cette affectation n'a lieu que si _best_move termine.
                    # Si le délai expire, le choix du niveau précédent reste intact.
                    best_move, best_score = self._best_move(
                        board, moves, ai_color, current_depth
                    )
                    self.stats.completed_depth = current_depth
            except SearchTimeout:
                self.stats.timed_out = True
                # Si aucun niveau n'a terminé : premier coup légal de secours,
                # score=None et profondeur=0. Aucun score n'est inventé.

        # Aucun coup légal : move=None, score=None, aucune recherche nécessaire.
        self.stats.elapsed_seconds = perf_counter() - started
        self.last_result = SearchResult(best_move, best_score, self.stats)
        return self.last_result


def minimax(board: Board, depth: int, current_color: int, ai_color: int) -> float:
    """Évaluer directement une position à profondeur fixe, sans délai."""
    if not isinstance(depth, int) or depth < 0:
        raise ValueError("La profondeur doit être un entier positif ou nul.")
    return MinimaxEngine()._minimax(board, depth, current_color, ai_color)


def choose_minimax_move(board: Board, ai_color: int, depth: int = 2,
                        *, time_limit: float | None = None,
                        engine: MinimaxEngine | None = None) -> MaybeMove:
    """Retourner seulement le coup. Réutiliser engine pour garder sa mémoire."""
    if engine is None:
        engine = MinimaxEngine()
    return engine.search(board, ai_color, depth, time_limit).move
