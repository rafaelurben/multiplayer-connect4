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

        self.next_player = 1  # 1 or 2
        self.board = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]

    @property
    def id(self):
        return self.gameid

    def delete(self):
        del Game.games[self.gameid]

    # State

    def validate_turn(self, pnum: int, col: int) -> bool:
        if not (1 <= pnum <= 2) or not (0 <= col < 7):
            return False  # invalid args
        if pnum != self.next_player:
            return False  # not your turn
        if self.board[0][col] != 0:
            return False  # free space
        return True

    def make_turn(self, pnum: int, col: int) -> bool:
        for row in range(-1, -7, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = pnum
                self.next_player = 3 - pnum
                return True
        return False

    def check_end(self):
        # TODO: check for end (full game, win)
        ...

    def p1board(self) -> str:
        """Get board as string from player 1 perspective"""
        return "\n".join(["".join(map(str, row)) for row in self.board])

    def p2board(self) -> str:
        """Get board as string from player 2 perspective"""
        def fn(x):
            return str(1 if x == 2 else 2 if x == 1 else x)
        return "\n".join(["".join(map(fn, row)) for row in self.board])

