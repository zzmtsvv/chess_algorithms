from chess import Board
from time import time, sleep
from itertools import count
from IPython.display import display, HTML, clear_output
from random import choice
from tqdm.auto import tqdm
import pandas as pd

try:
    from board_utils import eval_board_state, game_over, check_tie, check_win
    from config import BOARD_SCORES
except ModuleNotFoundError:
    from .board_utils import eval_board_state, game_over, check_tie, check_win
    from .config import BOARD_SCORES


class Game:
    def __init__(self, board: Board = None) -> None:

        if board is not None:
            self.board = board
        else:
            self.board = Board()
    
    def game(self, white_player, black_player, visual=False, pause=1):
        board = self.board.copy()
        result = None
        start_time = time()

        try:
            for i in count():
                if visual:
                    display(board)

                    white_score = eval_board_state(board, True, BOARD_SCORES)
                    black_score = eval_board_state(board, False, BOARD_SCORES)

                    display(HTML(f'<div>WHITE: {white_player.solver}  SCORE: {white_score}</div>'))
                    display(HTML(f'<div>BLACK: {black_player.solver} SCORE: {black_score}</div>'))
                    sleep(pause)
                
                if game_over(board, claim_draw=True):
                    break

                if board.turn:
                    move = white_player.move(board)
                else:
                    move = black_player.move(board)
                
                board.push_uci(move)
                if visual:
                    clear_output(wait=True)

        except KeyboardInterrupt:
            print("Game stopped")
        
        if check_tie(board, claim_draw=True):
            result = -1
        else:
            result = int(check_win(board, True))
        
        if visual:
            display(HTML(f"<div>RESULT: {result}</div>"))
        
        result_stats = {
            "white": white_player.solver,
            "black": black_player.solver,
            "FEN": board.fen(),
            "last_move": board.peek(),
            "moves_history": [move.uci() for move in board.move_stack],
            "moves": i,
            "time": round(time() - start_time, 2),
            "result": result
        }

        return result_stats
    
    def start_game(self, player1_cls, player2_cls, visual=True, pause=1):
        white_first = choice([True, False])

        if white_first:
            result = self.game(player1_cls(True), player2_cls(False), visual=visual, pause=pause)
        else:
            result = self.game(player2_cls(True), player1_cls(False), visual=visual, pause=pause)
        
        return result
    
    def start_games(self, player1_cls, player2_cls, n=10):
        results = dict()

        for i in tqdm(range(n)):
            result = self.start_game(player1_cls, player2_cls, visual=False)
            results[i] = result
        
        return pd.DataFrame.from_dict(results, orient="index")
