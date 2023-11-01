"""Game class"""

import typing

from connect4server.player import Player, tie


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
        self.p1.is_ready = False
        self.p2.gameid = self.gameid
        self.p2.is_ready = False

        self.is_finished: bool = False
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

        print(f"[Game #{self.id}] Created game with players: {p1.id} ({p1.name}) and {p2.id} ({p2.name})")

    @property
    def id(self):
        return self.gameid

    def delete(self):
        del Game.games[self.gameid]
        if self.p1.gameid == self.gameid:
            self.p1.gameid = None
        if self.p2.gameid == self.gameid:
            self.p2.gameid = None
        print(
            f"[Game #{self.id}] Deleted game with state finished={self.is_finished}, winning_nr={self.winning_nr}, "
            f"winning_name={self.winner.name if self.winner else None}")

    # Getters

    @property
    def winner(self) -> Player | None:
        if self.winning_nr == 0:
            return tie
        elif self.winning_nr == 1:
            return self.p1
        elif self.winning_nr == 2:
            return self.p2
        return None  # game not done

    # Helpers

    def get_pnum(self, player: Player) -> int | None:
        """Get the player number of a player in this game (1 or 2)"""
        if player.id == self.p1.id:
            return 1
        if player.id == self.p2.id:
            return 2
        return None

    # State

    def validate_turn(self, pnum: int, col: int) -> bool:
        """Checks if a turn is valid and currently allowed"""
        if self.is_finished:
            return False  # game already ended
        if not (1 <= pnum <= 2) or not (0 <= col < 7):
            return False  # invalid args
        if pnum != self.next_player:
            return False  # not your turn
        if self.board[0][col] != 0:
            return False  # free space
        return True

    def make_turn(self, pnum: int, col: int) -> bool:
        """Make a turn - note that this does not check if the turn is allowed!"""
        for row in range(5, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = pnum
                self.next_player = 3 - pnum
                self.check_for_winner(row, col)
                return True
        return False

    def _check_row_for_winner(self, row: list) -> bool:
        """Check if a row (list) contains a series of four 1s or 2s"""
        last_nr = 0
        streak = 0
        for nr in row:
            if nr == 0:  # an empty space occurred
                last_nr = 0
                streak = 0
            elif nr == last_nr:  # repeated same number
                streak += 1
                if streak == 4:
                    self.winning_nr = nr
                    self.is_finished = True
                    return True
            else:  # a number after an empty space
                last_nr = nr
                streak = 1
        return False

    def check_for_winner(self, row: int, col: int) -> bool:
        """Checks if game is ended - winner is stored in self.winning_nr"""
        b = self.board

        # Check row for winners
        rowlist = b[row]
        if self._check_row_for_winner(rowlist):
            return True
        # Check col for winners
        collist = [b[r][col] for r in range(6)]
        if self._check_row_for_winner(collist):
            return True
        # Check diagonal 1 for winners (top left to bottom right)
        startoff1 = min(row, col)  # shortest distance to top/left
        endoff1 = min(5 - row, 6 - col)  # shortest distance to bottom/right
        diag1 = [b[r][r + (col - row)] for r in range(row - startoff1, row + endoff1 + 1)]
        if self._check_row_for_winner(diag1):
            return True
        # Check diagonal 2 for winners (top right to bottom left)
        startoff2 = min(row, 6 - col)  # shortest distance to top/right
        endoff2 = min(5 - row, col)  # shortest distance to bottom/left
        diag2 = [b[r][col + startoff2 - r] for r in range(row - startoff2, row + endoff2 + 1)]
        if self._check_row_for_winner(diag2):
            return True

        # Check if board is full
        if 0 not in b[0]:
            self.winning_nr = 0
            self.is_finished = True
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
