import random


class TicTacToe:
    def __init__(self, id1, id2, sign1='x', sign2='o', empty_board=None):
        if empty_board is None:
            empty_board = ['', '', '', '', '', '', '', '', '']
        self.board = empty_board  # we need 9 slots for the board
        self.players = [id1, id2]
        self.signs = [sign1, sign2]
        self.turn = random.randint(0, 1)  # stores the index of the current player

    def move(self, position):
        # This lambda checks if the corresponding "p" cell is taken up
        # by any sign inside self.signs
        is_board_cell_empty = lambda p: False if self.board[p] in self.signs else True

        if is_board_cell_empty(position):
            self.board[position] = self.signs[self.turn]
            self.turn = 0 if self.turn == 1 else 1  # swapping the turn value, so makes the other player play
            return True  # the move has been executed properly
        else:
            return False  # we could perform the move because that cell is not empty

    def raw_print_board(self):
        print(self.board)

    def get_board_formatted_string(self):
        res = ''
        for i, s in enumerate(self.board):
            if i % 3 == 0:
                res += '\n'
            res += s

        return res
