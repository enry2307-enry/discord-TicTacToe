import random


class TicTacToe:
    def __init__(self, players, empty_board=None):
        if empty_board is None:
            empty_board = ['', '', '', '', '', '', '', '', '']
        self.board = empty_board  # we need 9 slots for the board

        self.players = players

        self.signs = [players[0].sign, players[1].sign]

        self.turn = random.randint(0, 1)  # stores the index of the current player chosen randomly

        self.winner = None  # we store the winning player. If NONE there is no winner at that moment

    def __get_turn_sign(self):
        return self.players[self.turn].sign

    def get_player_turn(self):
        return self.players[self.turn]

    def get_player_from_sign(self, sign):
        return self.players[0] if self.players[0].sign == sign else self.players[1]

    def move(self, position):
        # This lambda checks if the corresponding "p" cell is taken up
        # by any sign inside self.signs
        is_board_cell_empty = lambda p: False if self.board[p] in self.signs else True
        player = self.get_player_turn()

        # if the cell is not empty we cannot perform the move
        if not is_board_cell_empty(position):
            return False

        # we execute the move.
        self.board[position] = player.sign

        """ we check if there is win """
        self.swap_signs()  # change turn

        self.winner = self.get_winner_if_win(player.sign)  # returns None if non winner

        return True

    def swap_signs(self):
        self.turn = 0 if self.turn == 1 else 1  # swapping the turn value, so makes the other player play

    def get_winner_if_win(self, sign):
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
                if sign not in self.board[cell]:
                    win = False

            if win:
                winning_sign = sign
                break

        winner = None
        if winning_sign:
            winner = self.get_player_from_sign(winning_sign)
        return winner

    def raw_print_board(self):
        print(self.board)

    def get_board_formatted_string(self):
        res = ''
        for i, s in enumerate(self.board):
            if i % 3 == 0:
                res += '\n'
            res += s

        return res
