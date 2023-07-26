import random
from player import Player

class TicTacToe:
    def __init__(self, id1, id2, sign1='x', sign2='o', empty_board=None):
        if empty_board is None:
            empty_board = ['', '', '', '', '', '', '', '', '']
        self.board = empty_board  # we need 9 slots for the board
        self.players = [id1, id2]
        self.signs = [sign1, sign2]

        self.turn = random.randint(0, 1)  # stores the index of the current player

        self.winner_id = None  # we store the ID of the winning player. If NONE there is no win

    def __get_turn_sign(self):
        return self.signs[self.turn]

    def move(self, position):
        # This lambda checks if the corresponding "p" cell is taken up
        # by any sign inside self.signs
        is_board_cell_empty = lambda p: False if self.board[p] in self.signs else True

        # if the cell is not empty we cannot perform the move
        if not is_board_cell_empty(position):
            return False

        # we execute the move.
        self.board[position] = self.signs[self.turn]

        """ we check if there is win """
        winner_sign = self.get_winner()  # if win returns the winning sign else returns None
        self.swap_signs()  # change turn

        i = self.signs.index(winner_sign)  # we get the index of the player sign
        self.winner_id = self.players[i]  # we now set the winner of the game

        return True
    def swap_signs(self):
        self.turn = 0 if self.turn == 1 else 1  # swapping the turn value, so makes the other player play

    def get_winner(self, sign):
        # array to store winning combinations
        WINNING_C = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],

            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],

            [0, 4, 8],
            [2, 4, 6]
        ]
        winning_sign = None
        for combination in WINNING_C:
            win = True
            for cell in combination:
                if not sign in self.board[cell]:
                    win = False

            if win:
                winning_sign = sign
                break

        return winning_sign

    def raw_print_board(self):
        print(self.board)

    def get_board_formatted_string(self):
        res = ''
        for i, s in enumerate(self.board):
            if i % 3 == 0:
                res += '\n'
            res += s

        return res
