from abc import ABC, abstractmethod
from chess import Board, Move
from itertools import zip_longest
from random import choice
from math import inf
import logging
from time import time

try:
    from board_utils import eval_board_state, game_over, game_score, sorted_moves, turn_side
    from config import BOARD_SCORES, END_SCORES, PIECES
except ModuleNotFoundError:
    from .board_utils import eval_board_state, game_over, game_score, sorted_moves, turn_side
    from .config import BOARD_SCORES, END_SCORES, PIECES


logging.basicConfig(level=logging.INFO, 
                    format='%(levelname)s - %(asctime)s - %(message)s',
                    datefmt='%H:%M:%S') 


class Player(ABC):
    def __init__(self, player: bool, solver: str = None) -> None:
        self.player = player
        self.solver = solver
    
    @abstractmethod
    def move(self):
        pass


class HumanPlayer(Player):
    def __init__(self, player: bool) -> None:
        super().__init__(player, "human")
    
    def get_move(self, board: Board) -> str:
        uci = input(f"({turn_side(board)}) turn. Choose move in uci: ")

        try:
            Move.from_uci(uci)
        except ValueError:
            uci = None
        
        return uci
    
    @staticmethod
    def print_moves(moves):
        iters = [iter(moves)] * 4
        iters = zip_longest(*iters)

        for group in iters:
            print(" | ".join(move for move in group if move is not None))
    
    def move(self, board: Board):
        assert board.turn == self.player, "Not your turn"

        legal_moves = [move.uci() for move in board.legal_moves]

        move = self.get_move(board)

        while move is None:
            print("Invalid uci move, try again")
            move = self.get_move(board)
        
        while move not in legal_moves:
            print("Not a legal move. Available moves:\n")
            self.print_moves(legal_moves)
            move = self.get_move(board)
        
        return move


class RandomPlayer(Player):
    def __init__(self, player: bool) -> None:
        super().__init__(player, "random")

    def move(self, board: Board) -> str:
        assert board.turn == self.player, "Not random_bot turn"

        moves = list(board.legal_moves)
        move = choice(moves).uci()

        return move


class GreedyPlayer(Player):
    def __init__(self, player: bool) -> None:
        super().__init__(player, "greedy")
    
    def move(self, board: Board) -> str:
        moves = list(board.legal_moves)

        for move in moves:
            test_board = board.copy()

            test_board.push(move)
            move.score = eval_board_state(test_board, self.player, BOARD_SCORES)
        
        moves = sorted(moves, key=lambda move: move.score, reverse=True)
        return moves[0].uci()


class MiniMaxPlayer(Player):
    def __init__(self, player: bool, depth=3, verbose=False) -> None:
        super().__init__(player, "minimax")

        self.depth = depth
        self.verbose = verbose
    
    def minimax(self, board: Board, player: bool, depth: int, alpha: float = -inf, beta: float = inf) -> str:
        if depth == 0 or game_over(board):
            return [game_score(board, self.player, END_SCORES, BOARD_SCORES), None]
        
        if len(board.move_stack) == 0:
            return choice(("e2e4", "d2d4", "c2c4", "g1f3"))
        
        moves = sorted_moves(board)

        if board.turn == self.player:
            max_score, best_move = -inf, None

            for move, piece in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self.minimax(test_board, not player, depth - 1, alpha, beta)

                if self.verbose:
                    logging.info(f"{turn_side(test_board)}, m{len(moves)}, d{depth}, {PIECES[piece]}:{move} - score: {score}")
                
                alpha = max(alpha, score[0])
                if beta <= alpha:
                    break

                if score[0] >= max_score:
                    max_score = score[0]
                    best_move = move
            
            return [max_score, best_move]
        
        else:
            min_score, best_move = inf, None

            for move, piece in moves:
                test_board = board.copy()
                test_board.push(move)

                score = self.minimax(test_board, player, depth - 1, alpha, beta)

                if self.verbose:
                    logging.info(f"{turn_side(test_board)}, m{len(moves)}, d{depth}, {PIECES[piece]}:{move} - score: {score}")
                
                beta = min(beta, score[0])
                if beta <= alpha:
                    break

                if score[0] <= min_score:
                    min_score = score[0]
                    best_move = move
            
            return [min_score, best_move]
    
    def move(self, board: Board):
        best_move = self.minimax(board, self.player, self.depth)

        return best_move[1].uci()


if __name__ == "__main__":
    test_board = Board()
    test_bot = GreedyPlayer(player=True)

    start_time = time()
    print(test_bot.move(test_board))
    print(time() - start_time)
