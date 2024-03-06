"""
Base client for ICT Campus connect4 Python competition

`python -m pip install -U pip websockets`

Created by Rafael Urben - 2023
"""

import random
import asyncio
import websockets
import json
import string
from abc import ABC, abstractmethod


class WSConnect4Client(ABC):
    def __init__(self, url, name=None):
        self.url = url
        self.name = name or ''.join(random.choices(string.ascii_uppercase, k=10))
        self.ws: websockets.WebSocketClientProtocol | None = None

        self.playerid: int | None = None

        print("Created WSClient with name", self.name)

    @classmethod
    def print_board(cls, board: str):
        print("0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣")
        print(board.replace("0", "🔵").replace("1", "🟡").replace("2", "🔴"))
        print("-- You are: 🟡 --")

    @abstractmethod
    async def process_turn(self, board: str) -> int:
        """
        Function that processes the current game board and calculates the
        best possible column (number from 0 to 6) for player 1.

        Board format: "0000000\n0000000\n0000000\n0000000\n0010000\n0120200"
        """
        ...

    async def wait_for_ready(self):
        """By default, the client is not automatically ready to play!"""
        return input("Press enter to play again!")

    async def main(self):
        try:
            async with websockets.connect(self.url) as ws:
                self.ws = ws
                async for message in ws:
                    try:
                        message_json = json.loads(message)
                        print("Incoming message:", message_json)
                        await self.recv_json(message_json)
                    except json.JSONDecodeError:
                        print("Message couldn't be read as json:", message)
        except websockets.exceptions.ConnectionClosedError:
            print("ERROR: The connection to the server was lost!")

    def start(self):
        """Start the client"""

        asyncio.run(self.main())

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
                await self.send_json({'action': 'ready'})
            case 'game_joined':
                print("Game joined!", data)
            case 'game_result':
                self.print_board(data["board"])
                print("Game result:", data)
            case 'game_left':
                print("Game left!", data)

                await self.wait_for_ready()
                await self.send_json({'action': 'ready'})
            case 'turn_request':  # a turn is requested
                print("Turn requested!")

                self.print_board(data["board"])
                col = await self.process_turn(data["board"])
                await self.send_json({
                    'action': 'turn', 'gameid': data['gameid'], 'column': col
                })
            case 'turn_accepted':
                print("The turn has been accepted! Yay!")

                self.print_board(data["board"])
            case 'invalid_turn':
                print("Invalid turn! Reason:", data["reason"])
            case 'ping':
                ...
            case 'ready_response':
                ...
            case _:  # default case
                print(f"Action {action} not implemented!")
