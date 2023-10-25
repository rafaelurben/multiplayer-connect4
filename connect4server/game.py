"""Game class"""

import typing

from connect4server.player import Player


class Game:
    games: typing.Dict[int, "Game"] = {}
    lastgameid: int = 0

    def __init__(self, p1: Player, p2: Player):
        Game.lastgameid += 1
        self.gameid: int = Game.lastgameid
        Game.games[self.gameid] = self

        self.p1: Player = p1
        self.p2: Player = p2

        # TODO: Add game state

    @property
    def id(self):
        return self.gameid

    def delete(self):
        del Game.games[self.gameid]

    # TODO: Create game model
    # TODO: Add method to get game state from p1/p2 perspective
