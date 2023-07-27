class Lobby:
    def __init__(self):
        self.players = []

    def add(self, player):
        self.players.append(player)

    def is_ready(self):
        return True if len(self.players) == 2 else False

    def is_empty(self):
        return True if len(self.players) == 0 else False

    def get_players(self):
        return self.players

    def get_player(self, index):
        return self.players[0]

    def is_user_in_lobby(self, user):
        result = False
        for p in self.players:
            if p.user == user:
                result = True
                break

        return result

    def size(self):
        return len(self.players)

    def empty(self):
        self.players = []