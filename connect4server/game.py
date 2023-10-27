"""Game class"""

import typing

from connect4server.player import Player


class Game:
    games: typing.Dict[int, "Game"] = {}
    _last_gameid: int = 0

    def __init__(self, p1: Player, p2: Player):
        Game._last_gameid += 1
        self.gameid: int = Game._last_gameid
        Game.games[self.gameid] = self

        self.p1: Player = p1
        self.p2: Player = p2
        self.p1.gameid = self.gameid
        self.p2.gameid = self.gameid

        self.winning_nr: int | None = None

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
        if self.p1.gameid == self.gameid:
            self.p1.gameid = None
        if self.p2.gameid == self.gameid:
            self.p2.gameid = None

    # Getters

    @property
    def rows(self):
        return self.board
    
    @property
    def columns(self):
        cols = []
        for colnr in range(7):
            col = []
            for rownr in range(6):
                col.append(self.board[rownr][colnr])
            cols.append(col)
        return cols

    @property
    def diagonals(self):
        return ... # TODO: add diagonals

    # State

    def validate_turn(self, pnum: int, col: int) -> bool:
        if self.winning_nr is not None:
            return False  # game already ended
        if not (1 <= pnum <= 2) or not (0 <= col < 7):
            return False  # invalid args
        if pnum != self.next_player:
            return False  # not your turn
        if self.board[0][col] != 0:
            return False  # free space
        return True

    def make_turn(self, pnum: int, col: int) -> bool:
        """Make a turn - note that this does not check if the turn is valid!"""
        for row in range(-1, -7, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = pnum
                self.next_player = 3 - pnum
                return True
        return False

    def _check_row_for_winner(self, row) -> int:
        for i_start in range(0, len(range)-3):
            if row[i_start] != 0 and row[i_start] == row[i_start+1] == row[i_start+2] == row[i_start+3]:
                winner = row[i_start]
                print("Winner:", winner)
                return winner
        return 0

    def check_for_end(self) -> bool:
        """Checks if game is ended - winner is stored in self.winning_nr"""

        for row in self.rows + self.columns + self.diagonals:
            nr = self._check_row_for_winner(row)
            if nr != 0:
                self.winning_nr = nr
                return True

        if 0 not in self.board[0]:  # board is full
            self.winning_nr = 0
            return True
        return False  # game not ended yet

    def p1board(self) -> str:
        """Get board as string from player 1 perspective"""
        return "\n".join(["".join(map(str, row)) for row in self.board])

    def p2board(self) -> str:
        """Get board as string from player 2 perspective"""
        def fn(x):
            return str(1 if x == 2 else 2 if x == 1 else x)
        return "\n".join(["".join(map(fn, row)) for row in self.board])

