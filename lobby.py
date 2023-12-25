from tictactoe import TicTacToe
from datetime import datetime


class Lobby:
    def __init__(self):
        self.players = []
        self.game = None
        self.updated_time = None  # stores the time last changes are made ( for afk usage )

    # when ring we set new updated time value
    def set_time(self):
        self.updated_time = datetime.now()

    def unset_time(self):
        self.updated_time = None

    def update_game(self, game):
        self.game = game
        self.set_time()

    def start_game(self):
        self.game = TicTacToe(
            self.get_players(),
            empty_board=[':one:', ':two:', ':three:', ':four:',
                         ':five:', ':six:', ':seven:', ':eight:', ':nine:']
        )
        self.set_time()
        return self.game

    def stop_game(self) -> None:
        self.game = None

    def add(self, player) -> None:
        self.players.append(player)
        self.set_time()

    def is_ready(self) -> bool:
        return True if len(self.players) == 2 else False

    def is_empty(self) -> bool:
        return True if len(self.players) == 0 else False

    def get_players(self):
        return self.players

    def get_player(self, index):
        return self.players[index]

    def is_user_in_lobby(self, user) -> bool:
        result = False
        for p in self.players:
            if p.user == user:
                result = True
                break

        return result

    def size(self) -> int:
        return len(self.players)
