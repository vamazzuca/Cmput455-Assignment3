#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, PASS
from board import GoBoard
from board_score import winner
from ucb import runUcb
from simulation_util import writeMoves, select_best_move
from pattern_based_probabilistic import select_move
from gtp_connection import point_to_coord, format_point
import argparse
import sys

# The following functions are adapted from the Go3 program provided in the assignment 3 sample code
class Go0:
    def __init__(self, sim, move_select, sim_rule, size=7, limit=100):
        """
        NoGo player that selects moves randomly from the set of legal moves.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "Go0"
        self.version = 1.0
        self.sim = sim
        self.limit = limit
        self.use_ucb = False if move_select == "rr" else True
        self.random_simulation = True if sim_rule == "random" else False
        self.use_pattern = not self.random_simulation
        
    
    def simulate(self, board, move, toplay):
        """
        Run a simulated game for a given move.
        """
        cboard = board.copy()
        cboard.play_move(move, toplay)
        opp = GoBoardUtil.opponent(toplay)
        return self.playGame(cboard, opp)

    def simulateMove(self, board, move, toplay):
        """
        Run simulations for a given move.
        """
        wins = 0
        for _ in range(self.sim):
            result = self.simulate(board, move, toplay)
            if result == toplay:
                wins += 1
            if result == None:
                wins += 0.5
    
        return wins

    def get_move(self, board, color):
        """
        Run one-ply MC simulations to get a move to play.
        """
        cboard = board.copy()
        emptyPoints = board.get_empty_points()
        moves = []
        for p in emptyPoints:
            if board.is_legal(p, color):
                moves.append(p)
        if not moves:
            return None
        if self.use_ucb:
            C = 0.4  # sqrt(2) is safe, this is more aggressive
            best = runUcb(self, cboard, C, moves, color)
            return best
        else:
            moveWins = []
            for move in moves:
                wins = self.simulateMove(cboard, move, color)
                moveWins.append(wins)
            writeMoves(cboard, moves, moveWins, self.sim)
            return select_best_move(board, moves, moveWins)
    
    def playGame(self, board, color):
        """
        Run a simulation game.
        """
        for _ in range(self.limit):
            color = board.current_player
            if self.random_simulation:
                move = GoBoardUtil.generate_random_move(board, color, False)
            else:
                prob_movelist, move = select_move(board, color)
            board.play_move(move, color)
            if move == PASS:
                break
        winner_pt = winner(board)
        return winner_pt

    def setPolicy(self, sim_rule):
        self.random_simulation = True if sim_rule == "random" else False
        

    def setSelection(self, move_select):
        self.use_ucb = False if move_select == "rr" else True

    def getMovelist(self, board, color):
        movelist = []
        emptyPoints = board.get_empty_points()
        moves = []
        for p in emptyPoints:
            if board.is_legal(p, color):
                moves.append(p)
        if not moves:
            return None
        for i in range(len(moves)):
            x, y = point_to_coord(moves[i], board.size)
            move_string = format_point((x, y))
            movelist.append(move_string.lower())
        movelist.sort()
        return movelist, self.random_simulation

    def patternProbability(self, board, color):
        prob_movelist, move = select_move(board, color)
        return prob_movelist



def run(sim, move_select, sim_rule, move_filter):
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Go0(sim, move_select, sim_rule, move_filter), board)
    con.start_connection()

def parse_args():
    """
    Parse the arguments of the program.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--sim",
        type=int,
        default=10,
        help="number of simulations per move, so total playouts=sim*legal_moves",
    )
    parser.add_argument(
        "--moveselect",
        type=str,
        default="rr",
        help="type of move selection: rr or ucb",
    )
    parser.add_argument(
        "--simrule",
        type=str,
        default="random",
        help="type of simulation policy: random or rulebased",
    )
    parser.add_argument(
        "--movefilter",
        action="store_true",
        default=False,
        help="whether use move filter or not",
    )

    args = parser.parse_args()
    sim = args.sim
    move_select = args.moveselect
    sim_rule = args.simrule
    move_filter = args.movefilter

    if move_select != "rr" and move_select != "ucb":
        print("moveselect must be simple or ucb")
        sys.exit(0)
    if sim_rule != "random" and sim_rule != "rulebased":
        print("simrule must be random or rulebased")
        sys.exit(0)

    return sim, move_select, sim_rule, move_filter


if __name__ == "__main__":
    sim, move_select, sim_rule, move_filter = parse_args()
    run(sim, move_select, sim_rule, move_filter)
