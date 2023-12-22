class Lobby:
    def __init__(self):
        self.players = []

    def add(self, player) -> None:
        self.players.append(player)

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

    def empty(self) -> None:
        self.players = []