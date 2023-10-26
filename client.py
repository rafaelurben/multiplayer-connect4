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

        match data["action"]:
            case 'connected':  # server has confirmed websocket connection
                self.playerid = data["id"]
                await self.send_json({"action": "join_room", "mode": "player", "name": self.name})
            case 'game_joined':
                ...
            case 'game_left':
                ...
            case 'turn_request':  # a turn is requested
                ...
                # TODO: implement state parsing & function call


if __name__ == "__main__":
    client = WSClient("ws://localhost:80/ws", name=None)  # TODO: Enter your name
    asyncio.run(client.main())
