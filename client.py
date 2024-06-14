import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri, close_timeout=120) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(listen())