import asyncio
import websockets
from typing import Set

class WebSocketManager:
    def __init__(self):
        self.clients: Set[websockets.WebSocketClientProtocol] = set()
    
    async def notify_clients(self, message: str):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])
    
    async def register_client(self, websocket: websockets.WebSocketClientProtocol):
        self.clients.add(websocket)

        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
        
