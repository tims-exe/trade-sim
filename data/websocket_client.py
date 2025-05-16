import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self, url, callback):
        self.url = url
        self.callback = callback
        self.websocket = None
        self.running = False

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.url)
            logger.info(f"Connected to {self.url}")
            self.running = True
        except Exception as e:
            logger.error(f"Connection Failed : {e}")
            return False
    
    async def get_data(self):
        if not self.websocket:
            logger.error("WebSocket not connected")
            return

        try:
            while self.running:
                msg = await self.websocket.recv()
                data = json.loads(msg)
                await self.callback(data)
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
    
    async def disconnect(self):
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket disconnected")

    def start(self):
        asyncio.run(self.connect())
