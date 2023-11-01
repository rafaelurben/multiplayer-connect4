"""
Client preset for ICT Campus connect4 Python competition

`python -m pip install -U pip websockets`

Preset by: Rafael Urben - 2023
Implementation: YOUR NAME - YEAR
"""

from client_base import WSConnect4Client

NAME = None  # TODO: Enter your name
URL = "ws://localhost:80/ws"  # TODO: Replace with server URL


class CustomClient(WSConnect4Client):
    async def process_turn(self, board: str) -> int:
        """
        Function that processes the current game board and calculates the
        best possible column (number from 0 to 6) for player 1.

        Board format: "0000000\n0000000\n0000000\n0000000\n0010000\n0120200"
        """

        # TODO: Replace this function body with your custom implementation!

        ...


if __name__ == "__main__":
    client = CustomClient(url=URL, name=NAME)
    client.start()
