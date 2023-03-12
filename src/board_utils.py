import chess
from chess import Board
from random import random
from typing import List

try:
    from config import BOARD_SCORES, END_SCORES
except ModuleNotFoundError:
    from .config import BOARD_SCORES, END_SCORES


NAME_TO_SQUARE_BOARD = dict(zip(chess.SQUARE_NAMES, chess.SQUARES))


def square_name(move):
    return move.uci()[:2]


def turn_side(board):
    return "White" if board.turn else "Black"


def eval_board_state(board: Board, player: bool, board_scores_policy: dict) -> float:
    total_score = random()

    for piece, score in board_scores_policy.items():
        piece = getattr(chess, piece)

        true_score = len(board.pieces(piece, player)) * score
        false_score = -len(board.pieces(piece, not player)) * score

        total_score += true_score + false_score
    
    return total_score


def game_over(board: Board, claim_draw: bool = False) -> bool:
    if board.is_game_over(claim_draw=claim_draw):
        return True
    
    return False


def check_win(board: Board, player: bool) -> bool:
    if board.is_checkmate() and board.turn == (not player):
        return True
    return False


def check_tie(board: Board, claim_draw: bool = False) -> bool:
    tie = board.is_stalemate() or board.is_fivefold_repetition() or board.is_insufficient_material()

    if claim_draw:
        tie = tie or board.can_claim_draw()
    
    return tie


def game_score(board, player, end_scores_policy=END_SCORES, board_scores_policy=BOARD_SCORES) -> float:
    score = None

    if check_tie(board):
        score = end_scores_policy["TIE"]
    elif check_win(board, player):
        score = end_scores_policy["WIN"]
    elif check_win(board, not player):
        score = end_scores_policy["LOSE"]
    else:
        score = eval_board_state(board, player, board_scores_policy)
    
    return score


def sorted_moves(board: Board) -> List[str]:
    moves = list(board.legal_moves)

    squares = [NAME_TO_SQUARE_BOARD[name] for name in map(square_name, moves)]
    pieces = [board.piece_type_at(square) for square in squares]

    moves = sorted(zip(moves, pieces), key=lambda x: x[1], reverse=True)
    return moves
