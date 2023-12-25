import random


class TicTacToe:
    def __init__(self, players, empty_board=None):
        if empty_board is None:
            empty_board = ['', '', '', '', '', '', '', '', '']
        self.board = empty_board  # we need 9 slots for the board
        self.executed_moves = 0  # counts the number of executed moves

        # Stores the players
        self.players = players

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

    def is_user_turn(self, user) -> bool:
        return True if self.get_player_turn().user == user else False

    def is_board_cell_empty(self, position):
        return False if self.board[position] in self.signs else True

    # Returns the last player that made a move on the board
    def get_last_player_moved(self):
        # The last player to move corresponds to the player who doesn't have their turn to play.
        return self.players[
            1 if self.turn == 0 else 0
        ]

    def get_last_sign_moved(self):
        return self.get_last_player_moved().sign

    def move(self, position) -> bool:
        """

        :param position: Value from [0; 9] representing the position on the board
        :return: returns True if the move is performed, False if not
        """
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

    # Swapping the turn value, so makes the other player play
    def swap_signs(self) -> None:
        self.turn = 0 if self.turn == 1 else 1

    # This function returns if the game is finished. It doesn't take action. It just tells you
    def is_end(self) -> bool:
        return True if self.winner or self.draw else False

    # This function returns if the game is draw. It doesn't take action. It just tells you
    def is_draw(self) -> bool:
        # if ( not winner ) and moves == 9 then it's draw
        return True if not self.winner and self.executed_moves == 9 else False

    def get_winner_if_win(self):
        """

        :return: Returns winner if game is finished and not drawn. Return None if anything else happens.
        """
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
    def raw_print_board(self) -> None:
        """
        Prints the board on the terminal just for debug purpose
        """
        print(self.board)

    def get_board_formatted_string(self) -> str:
        """

        :return: Returns a friendly formatted string of the board to print on discord message
        """
        res = ''
        for i, s in enumerate(self.board):
            if i % 3 == 0:
                res += '\n'
            res += s

        return res
