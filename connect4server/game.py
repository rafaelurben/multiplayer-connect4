"Game class"

import typing

class Game:
    games : typing.Dict[int, "Game"] = {}
    lastgameid : int = 0

    def __init__(self, p1id, p2id):
        Game.lastgameid += 1
        self.gameid : int = Game.lastgameid
        Game.games[self.gameid] = self

        self.p1id = p1id
        self.p2id = p2id
    
    @property
    def id(self):
        return self.gameid

    def delete(self):
        del Game.games[self.gameid]

    # TODO: Create game model
