import websockets
import asyncio
import json

class Client:
    def __init__(self, url):
        self.url = url
        self.ws : websockets.WebSocketClientProtocol = None

    async def main(self):
        async with websockets.connect(self.url) as ws:
            self.ws = ws
            async for message in ws:
                try:
                    message_json = json.loads(message)
                    print("Incoming message:")
                    await self.recv_json(message_json)
                except json.JSONDecodeError:
                    print("Message couldn't be read as json:", message)

    async def send_json(self, data):
        "Send json message to server"

        await self.ws.send(json.dumps(data))

    async def recv_json(self, data):
        "Process incoming message from the server"

        ...

if __name__ == "__main__":
    client = Client("wss://socketsbay.com/wss/v2/1/demo/")
    asyncio.run(client.main())
