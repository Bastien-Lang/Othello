"""Recherche Minimax : les simulations ne modifient jamais le plateau fourni.

La profondeur compte les demi-coups (actions individuelles) : depth=2
correspond à un coup de l'IA puis une réponse adverse, soit 1 dans le TP.
Une passe ne consomme pas de profondeur.
"""

from board import Board
from constants import MaybeMove


def evaluate(board: Board, ai_color: int) -> int:
    """Avance en nombre de pions, toujours du point de vue de l'IA."""
    my_discs = board.count(ai_color)
    opponent_discs = board.count(-ai_color)
    return my_discs - opponent_discs


def minimax(board: Board, depth: int, current_color: int, ai_color: int) -> float:
    """Retourne la valeur d'une position, pas le coup à jouer.

    current_color alterne à chaque tour ; ai_color reste fixe.
    MAX représente l'IA et MIN représente son adversaire.
    """
    if depth < 0:
        raise ValueError("La profondeur ne peut pas être négative.")

    # Une fin de partie simulée donne un résultat certain, même à profondeur 0.
    if board.is_game_over():
        difference = evaluate(board, ai_color)
        if difference > 0:
            return float("inf")
        if difference < 0:
            return -float("inf")
        return 0

    # Sinon, à la limite de recherche, on estime seulement la position.
    if depth == 0:
        return evaluate(board, ai_color)

    moves = board.get_legal_moves(current_color)
    if not moves:
        # Un seul joueur est bloqué : il passe, la partie continue.
        return minimax(board, depth, -current_color, ai_color)

    if current_color == ai_color:
        best_score = -float("inf")
        for move in moves:
            child = board.copy()
            child.apply_move(move, current_color)
            score = minimax(child, depth - 1, -current_color, ai_color)
            best_score = max(best_score, score)
        return best_score

    else:
        best_score = float("inf")
        for move in moves:
            child = board.copy()
            child.apply_move(move, current_color)
            score = minimax(child, depth - 1, -current_color, ai_color)
            best_score = min(best_score, score)
        return best_score


def choose_minimax_move(board: Board, ai_color: int, depth: int = 2) -> MaybeMove:
    """Choisit le meilleur coup ; retourne None si le joueur doit passer.

    En cas d'égalité, conserve le premier coup dans l'ordre du plateau.
    """
    if depth < 1:
        raise ValueError("La profondeur de choix doit être au moins 1.")

    moves = board.get_legal_moves(ai_color)
    if not moves:
        return None

    # Garantit un coup légal même si tous les scores valent moins l'infini.
    best_move = moves[0]
    best_score = -float("inf")
    for move in moves:
        child = board.copy()
        child.apply_move(move, ai_color)
        # Le premier coup vient d'être simulé : il consomme un niveau.
        score = minimax(child, depth - 1, -ai_color, ai_color)
        if score > best_score:
            best_score = score
            best_move = move
    return best_move
