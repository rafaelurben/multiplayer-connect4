"""
Random client for ICT Campus connect4 Python competition

`python -m pip install -U pip websockets`

Preset by: Rafael Urben - 2023
Implementation: Rafael Urben - 2023
"""

import random
from client_base import WSConnect4Client

NAME = None  # TODO: Enter your name
URL = "ws://localhost:80/ws"  # TODO: Replace with server URL


class RandomClient(WSConnect4Client):
    async def process_turn(self, board: str) -> int:
        """
        Function that processes the current game board and calculates the
        best possible column (number from 0 to 6) for player 1.

        Board format: "0000000\n0000000\n0000000\n0000000\n0010000\n0120200"
        """

        col = 7
        while board[col] != '0':
            col = random.randint(0, 6)
        return col


if __name__ == "__main__":
    client = RandomClient(url=URL, name=NAME)
    client.start()
