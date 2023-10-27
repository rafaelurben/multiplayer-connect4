"""Client preset for BA py4connect competition

`python -m pip install -U pip websockets`

Preset by: Rafael Urben - 2023
Implementation: YOUR NAME - YEAR
"""

import websockets
import asyncio
import json
import random
import string

NAME = None  # TODO: Enter your name
URL = "ws://localhost:80/ws"  # TODO: Replace with server URL


def print_board(board):
    print("*" * 6)
    print(board)
    print("*" * 6)


async def process_turn(board) -> int:
    """
    Function that processes the current game board and calculates the
    best possible column (number from 0 to 6) for player 1.

    Board format: "0000000\n0000000\n0000000\n0000000\n0010000\n0120200"
    """

    # TODO: Replace this function body with your custom implementation!

    col = None
    while True:
        try:
            col = int(input("Deine Spalte [0-6]: "))
            if not 0 <= col <= 6:
                continue
            break
        except ValueError:
            continue
    return col


class WSClient:
    def __init__(self, url, name=None):
        self.url = url
        self.name = name or ''.join(random.choices(string.ascii_uppercase, k=10))
        self.ws: websockets.WebSocketClientProtocol | None = None

        self.playerid: int | None = None

        print("Created WSClient with name", self.name)

    async def main(self):
        async with websockets.connect(self.url) as ws:
            self.ws = ws
            async for message in ws:
                try:
                    message_json = json.loads(message)
                    print("Incoming message:", message_json)
                    await self.recv_json(message_json)
                except json.JSONDecodeError:
                    print("Message couldn't be read as json:", message)

    async def send_json(self, data: dict):
        """Send json message to server"""

        print("Outgoing message:", data)
        await self.ws.send(json.dumps(data))

    async def recv_json(self, data: dict):
        """Process incoming message from the server"""

        action = data.pop("action")
        match action:
            case 'connected':  # server has confirmed websocket connection
                self.playerid = data["id"]
                await self.send_json({
                    "action": "join_room", "mode": "player", "name": self.name
                })
            case 'game_joined':
                print("Game joined!", data)
            case 'game_left':
                print("Game left!", data)
            case 'turn_request':  # a turn is requested
                print("Turn requested!")

                print_board(data["board"])
                col = await process_turn(data["board"])
                await self.send_json({
                    'action': 'turn', 'gameid': data['gameid'], 'column': col
                })
            case 'turn_accepted':
                print("The turn has been accepted! Yay!")

                print_board(data["board"])
            case 'invalid_turn':
                print("Invalid turn! Reason:", data["reason"])
            case _:  # default case
                print(f"Action not implemented!")


if __name__ == "__main__":
    client = WSClient(url=URL, name=NAME)
    asyncio.run(client.main())
