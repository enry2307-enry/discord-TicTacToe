import random


class TicTacToe:
    def __init__(self, lobby, empty_board=None):
        if empty_board is None:
            empty_board = ['', '', '', '', '', '', '', '', '']
        self.board = empty_board  # we need 9 slots for the board
        self.executed_moves = 0  # counts the number of executed moves

        # Stores the players
        self.players = lobby.get_players()

        # Stores the signs of the players
        self.signs = [self.players[0].sign, self.players[1].sign]

        self.turn = random.randint(0, 1)  # stores the index of the current player chosen randomly

        """ STOPPING CONDITIONS"""
        # This variable just stores if the game is ended
        self.end = False

        # These variables basically contains the results of the game
        self.winner = None  # Stores the winner
        self.draw = False  # Changes to True if the game ends in draw

    def __get_turn_sign(self):
        return self.players[self.turn].sign

    def get_player_turn(self):
        return self.players[self.turn]

    def get_player_from_sign(self, sign):
        return self.players[0] if self.players[0].sign == sign else self.players[1]

    def is_user_turn(self, user):
        return True if self.get_player_turn().user == user else False

    def is_board_cell_empty(self, position):
        return False if self.board[position] in self.signs else True

    def move(self, position):
        # This lambda checks if the corresponding "p" cell is taken up
        # by any sign inside self.signs
        player = self.get_player_turn()

        # if the cell is not empty we cannot perform the move
        if not self.is_board_cell_empty(position):
            return False

        # we execute the move.
        self.board[position] = player.sign
        self.executed_moves += 1

        """ checking the win or draw """
        self.winner = self.get_winner_if_win()  # we set the winner. Returns None if no winner
        self.draw = self.is_draw()  # we set the game to drawn if draw conditions are true. Else it gets None
        self.end = self.is_end()  # we end the game if it's finished. Else it gets None

        self.swap_signs()  # change turn
        return True

    def swap_signs(self):
        self.turn = 0 if self.turn == 1 else 1  # swapping the turn value, so makes the other player play

    # this function returns if the game is finished. It doesn't take action. It just tells you
    def is_end(self):
        return True if self.winner or self.draw else False

    def is_draw(self):
        # if there is no winner and if 9 moves has been executed then it means
        # that the game is in draw
        return True if not self.winner and self.executed_moves == 9 else False

    def get_winner_if_win(self):
        sign = self.__get_turn_sign()  # we check the win for the current sign

        # array to store the cell's winning combinations
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
            winner = self.get_player_from_sign(sign)
        return winner

    # We use this function to debug the board
    def raw_print_board(self):
        print(self.board)

    # We use this function to return the formatted string of the board
    def get_board_formatted_string(self) -> str:
        res = ''
        for i, s in enumerate(self.board):
            if i % 3 == 0:
                res += '\n'
            res += s

        return res
