"""
Manual client for ICT Campus connect4 Python competition

`python -m pip install -U pip websockets`

Preset by: Rafael Urben - 2023
Implementation: Rafael Urben - 2023
"""

from client_base import WSConnect4Client

NAME = None  # TODO: Enter your name
URL = "ws://localhost:80/ws"  # TODO: Replace with server URL


class ManualClient(WSConnect4Client):
    async def process_turn(self, board: str) -> int:
        """
        Function that processes the current game board and calculates the
        best possible column (number from 0 to 6) for player 1.

        Board format: "0000000\n0000000\n0000000\n0000000\n0010000\n0120200"
        """

        col = None
        while True:
            try:
                col = int(input("Deine Spalte [0-6]: "))
                if (not 0 <= col <= 6) or board[col] != '0':
                    continue
                break
            except ValueError:
                continue
        return col

    async def wait_for_ready(self):
        """Wait until user is ready to play again"""
        return input("Press enter to play again...")


if __name__ == "__main__":
    client = ManualClient(url=URL, name=NAME)
    client.start()
