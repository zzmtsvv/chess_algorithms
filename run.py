import numpy as np
import pandas as pd

from src.player import HumanPlayer, MiniMaxPlayer
from src.game import Game

if __name__ == "__main__":

    game = Game()
    result = game.start_game(HumanPlayer, MiniMaxPlayer, visual=True, pause=0.1)