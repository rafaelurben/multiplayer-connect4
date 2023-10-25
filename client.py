import websockets
import asyncio
import json


async def send_json(data):
    "Send json message to server"

    await ws.send(json.dumps(data))

async def recv_json(data):
    "Process incoming message from the server"

    ...

async def main(ws):
    async with ws:
        async for message in ws:
            try:
                message_json = json.loads(message)
                print("Incoming message:")
                recv_json(message_json)
            except json.JSONDecodeError:
                print("Message couldn't be read as json:", message)

if __name__ == "__main__":
    ws = websockets.connect("ws://localhost")
    asyncio.run(main(ws))
