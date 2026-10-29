"""Recherche Minimax : les simulations ne modifient jamais le plateau fourni.

La profondeur compte les demi-coups (actions individuelles) : depth=2
correspond à un coup de l'IA puis une réponse adverse, soit 1 dans le TP.
Une passe ne consomme pas de profondeur.
Le moteur gère une limite de temps et conserve les analyses entre les tours.

Exemple : moteur = MinimaxEngine()
          resultat = moteur.search(board, color, depth=6, time_limit=2.0)
          coup = resultat.move ; mesures = resultat.stats
Réutiliser le même moteur au tour suivant pour profiter de sa mémoire.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from time import perf_counter

from board import Board  # Plateau et règles : coups légaux, copies, captures, fin.
from constants import MaybeMove  # Un couple (ligne, colonne), ou None pour passer.


def evaluate(board: Board, ai_color: int) -> int:
    """Avance en nombre de pions, toujours du point de vue de l'IA."""
    # ai_color désigne l'IA pour laquelle on réfléchit, pas forcément le joueur
    # dont c'est actuellement le tour dans la simulation.
    my_discs = board.count(ai_color)
    # BLACK=1 et WHITE=-1 : changer le signe donne la couleur adverse.
    # On change le signe de la couleur, PAS celui du nombre de pions.
    opponent_discs = board.count(-ai_color)
    # Exemple : 10 pions contre 6 donnent +4. Une avance pendant la partie
    # n'est pas une victoire : l'adversaire peut encore retourner des pions.
    return my_discs - opponent_discs


@dataclass
class SearchStats:
    """Mesures d'un choix de coup, cumulées sur toutes ses itérations."""

    nodes: int = 0              # Appels récursifs visités, cache compris.
    cache_hits: int = 0         # Résultats retrouvés sans recalcul des enfants.
    completed_depth: int = 0    # Dernière profondeur ENTIÈREMENT terminée.
    elapsed_seconds: float = 0.0
    timed_out: bool = False


@dataclass
class SearchResult:
    """Coup choisi, valeur et mesures ; score=None si seul le secours est connu."""

    move: MaybeMove
    score: float | None
    stats: SearchStats


class SearchTimeout(Exception):
    """Signal interne : abandonner l'itération en cours, pas la partie."""


# Même grille ne signifie pas même problème : le joueur au trait, le point
# de vue de l'IA et la profondeur restante influencent la valeur calculée.
# On inclut aussi la taille pour distinguer les formats de plateau.
# La fonction d'évaluation reste fixe (absolue) dans cette implémentation.
# Une valeur à profondeur 4 ne remplace PAS une valeur à profondeur 2 :
# leurs horizons d'évaluation peuvent produire des scores différents.
# Si l'on change de fonction d'évaluation plus tard, il faudra vider le cache
# ou ajouter l'identité de l'évaluation à la clé.
PositionKey = tuple[int, bytes, int, int, int]


@dataclass
class _SearchContext:
    """Informations partagées par tous les appels d'une même recherche."""

    table: dict[PositionKey, float]
    stats: SearchStats
    deadline: float | None = None
    max_entries: int = 100_000

    def check_time(self) -> None:
        # perf_counter est une horloge adaptée aux durées : un changement
        # de l'heure civile ne déplace pas notre échéance.
        if self.deadline is not None and perf_counter() >= self.deadline:
            raise SearchTimeout

    def save(self, key: PositionKey, score: float) -> float:
        # Ne mémoriser qu'un nœud terminé : une interruption ne doit jamais
        # transformer une valeur partielle en résultat exact réutilisable.
        self.check_time()
        if len(self.table) >= self.max_entries and key not in self.table:
            # Limite mémoire simple : retirer la plus ancienne entrée.
            # Cela change la vitesse de recherche, pas la valeur du résultat.
            del self.table[next(iter(self.table))]
        self.table[key] = score
        return score


def minimax(board: Board, depth: int, current_color: int, ai_color: int,
            *, _context: _SearchContext | None = None) -> float:
    """Retourne la valeur d'une position, pas le coup à jouer.

    current_color alterne à chaque tour ; ai_color reste fixe.
    MAX représente l'IA et MIN représente son adversaire.

    board : position à analyser (réelle à l'entrée, puis copies simulées).
    depth : nombre de coups encore autorisés dans la recherche ; 0 est valide.
    Le résultat est numérique : estimation entière, ou +/- infini en fin.
    L'annotation -> float ne convertit pas automatiquement les valeurs.
    """
    # Une profondeur négative serait une erreur d'utilisation de la fonction.
    if not isinstance(depth, int) or depth < 0:
        raise ValueError("La profondeur doit être un entier positif ou nul.")

    # Un appel direct reste possible comme avant, sans limite de temps.
    # Dans le joueur IA, le moteur fournit un contexte avec sa mémoire durable.
    context = _context if _context is not None else _SearchContext({}, SearchStats())
    context.check_time()
    context.stats.nodes += 1
    key = (board.size, board.to_key(), current_color, ai_color, depth)
    if key in context.table:
        context.stats.cache_hits += 1
        return context.table[key]

    # Une fin de partie simulée donne un résultat certain, même à profondeur 0.
    if board.is_game_over():
        difference = evaluate(board, ai_color)
        # C'est is_game_over() qui constate la fin, pas la valeur infinie.
        # Une victoire certaine doit être préférée à une simple avance de +12
        # dans une autre branche où la partie n'est pas encore terminée.
        if difference > 0:
            return context.save(key, float("inf"))
        # Inversement, une défaite certaine reçoit la valeur la plus basse.
        if difference < 0:
            return context.save(key, -float("inf"))
        # Partie terminée avec autant de pions de chaque couleur : égalité.
        return context.save(key, 0)

    # Sinon, à la limite de recherche, on estime seulement la position.
    # Ce test vient APRÈS la fin de partie : même à depth=0, une vraie fin
    # simulée doit être reconnue comme un résultat définitif.
    if depth == 0:
        return context.save(key, evaluate(board, ai_color))

    # On explore uniquement les coups autorisés par les règles du plateau.
    moves = board.get_legal_moves(current_color)
    if not moves:
        # Un seul joueur est bloqué : il passe, la partie continue.
        # Même plateau et même profondeur car aucun pion n'est posé.
        # Si les deux joueurs étaient bloqués, is_game_over() aurait déjà
        # arrêté la recherche : pas de boucle infinie de passes.
        score = minimax(board, depth, -current_color, ai_color, _context=context)
        return context.save(key, score)

    if current_color == ai_color:
        # MAX : l'IA garde la plus grande valeur des réponses analysées.
        # Ici -inf est une valeur de départ, PAS une défaite déjà constatée.
        best_score = -float("inf")
        for move in moves:
            context.check_time()
            # Chaque candidat part d'une copie indépendante du même plateau.
            # Ni la partie réelle ni les autres candidats ne sont modifiés.
            child = board.copy()
            child.apply_move(move, current_color)
            # Appel récursif : analyser la suite après ce coup.
            # Un niveau est consommé, l'adversaire joue, ai_color reste fixe.
            # L'appel se termine avant que la comparaison suivante soit faite.
            score = minimax(child, depth - 1, -current_color, ai_color, _context=context)
            best_score = max(best_score, score)
        # On remonte seulement la valeur ; le choix du coup se fait plus bas.
        return context.save(key, best_score)

    else:
        # MIN : l'adversaire cherche le score le plus faible POUR L'IA.
        # Les scores ne changent jamais de point de vue dans cette version.
        # +inf initialise la recherche d'un minimum ; ce n'est pas une victoire.
        best_score = float("inf")
        for move in moves:
            context.check_time()
            # Même simulation que pour MAX, mais on conserve le minimum.
            child = board.copy()
            child.apply_move(move, current_color)
            score = minimax(child, depth - 1, -current_color, ai_color, _context=context)
            best_score = min(best_score, score)
        return context.save(key, best_score)


def choose_minimax_move(board: Board, ai_color: int, depth: int = 2,
                        *, time_limit: float | None = None,
                        engine: MinimaxEngine | None = None) -> MaybeMove:
    """Choisit le meilleur coup ; retourne None si le joueur doit passer.

    En cas d'égalité, conserve le premier coup dans l'ordre du plateau.
    depth inclut le premier coup choisi ici : 2 = IA puis réponse adverse
    (hors passes). Le plateau fourni reste intact ; Game jouera le résultat.
    """
    # Façade compatible avec l'ancien appel à trois arguments.
    # Fournir le même moteur entre les tours permet de conserver ses analyses.
    search_engine = engine if engine is not None else MinimaxEngine()
    return search_engine.search(board, ai_color, depth, time_limit).move


class MinimaxEngine:
    """Mémoire privée d'une IA, conservée entre ses tours (aucun Alpha-Bêta).

    On conserve les valeurs des sous-arbres via leurs positions, sans arbre
    explicite de liens parents/enfants. Au tour suivant, les positions communes
    à la même profondeur restante peuvent être retrouvées sans recalcul.
    Pour une comparaison de performances, préciser si le cache est vide ou
    déjà alimenté ; clear() permet de repartir avec une mémoire vide.
    """

    def __init__(self, max_entries: int = 100_000) -> None:
        if not isinstance(max_entries, int) or max_entries < 1:
            raise ValueError("La capacité du cache doit être un entier positif.")
        self.max_entries = max_entries
        self.table: dict[PositionKey, float] = {}
        self.last_result: SearchResult | None = None

    def clear(self) -> None:
        """Oublier les analyses, par exemple pour commencer une expérience neuve."""
        self.table.clear()
        self.last_result = None

    def search(self, board: Board, ai_color: int, depth: int = 2,
               time_limit: float | None = None) -> SearchResult:
        """Chercher jusqu'à depth demi-coups ; time_limit est exprimé en secondes.

        Sans délai : recherche directement à profondeur fixe (comparaisons TP).
        Avec délai : profondeurs 1, 2, ... jusqu'à depth, sans dépasser volontairement
        l'échéance. Le contrôle est coopératif : une opération Board en cours
        finit avant de rendre la main, donc une petite marge est possible.
        """
        if not isinstance(depth, int) or depth < 1:
            raise ValueError("La profondeur de choix doit être un entier positif.")
        if time_limit is not None and (not isfinite(time_limit) or time_limit < 0):
            raise ValueError("Le délai doit être fini et positif ou nul, ou None.")

        started = perf_counter()
        stats = SearchStats()
        context = _SearchContext(self.table, stats,
                                 None if time_limit is None else started + time_limit,
                                 self.max_entries)
        # Obtenir au moins un coup de secours, même si le budget vaut zéro.
        # Cette préparation est incluse dans le temps mesuré, mais ne peut pas
        # être interrompue au milieu d'un appel à get_legal_moves().
        moves = board.get_legal_moves(ai_color)
        best_move = moves[0] if moves else None
        best_score = None

        if moves:
            depths = [depth] if time_limit is None else range(1, depth + 1)
            try:
                for current_depth in depths:
                    context.check_time()
                    candidate_move = moves[0]
                    candidate_score = -float("inf")
                    for move in moves:
                        context.check_time()
                        child = board.copy()
                        child.apply_move(move, ai_color)
                        score = minimax(child, current_depth - 1, -ai_color,
                                        ai_color, _context=context)
                        if score > candidate_score:
                            candidate_score, candidate_move = score, move
                    context.check_time()
                    # Publication atomique : on remplace le choix précédent
                    # seulement après avoir examiné TOUS les coups à ce niveau.
                    # Sinon, les premiers coups auraient un avantage injustifié.
                    best_move, best_score = candidate_move, candidate_score
                    stats.completed_depth = current_depth
            except SearchTimeout:
                # Les sous-arbres terminés restent en mémoire, mais le choix
                # partiel de cette itération est abandonné. Si aucun niveau
                # n'a fini, on retourne le secours avec score=None, profondeur=0.
                stats.timed_out = True

        # Aucun coup légal signifie une passe (ou une partie déjà terminée).
        # Le choix est None ; aucune recherche n'est nécessaire dans ce cas.
        stats.elapsed_seconds = perf_counter() - started
        result = SearchResult(best_move, best_score, stats)
        self.last_result = result
        return result
