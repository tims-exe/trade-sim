"""
WebSocket client for connecting to exchange orderbook streams.

This module provides an asynchronous WebSocket client that connects to the specified
exchange endpoint and processes incoming orderbook data.
"""

import asyncio
import json
import logging
import time
from typing import Callable, Dict, Optional, Any

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

class WebSocketClient:
    """Client for connecting to and consuming WebSocket market data feeds."""
    
    def __init__(self, 
                 uri: str,
                 on_message: Callable[[Dict[str, Any]], None],
                 heartbeat_interval: float = 30.0,
                 reconnect_delay: float = 5.0,
                 max_reconnect_attempts: int = 10):
        """
        Initialize the WebSocket client.
        
        Args:
            uri (str): The WebSocket endpoint URL
            on_message (callable): Callback function for processing messages
            heartbeat_interval (float): Time in seconds between heartbeats
            reconnect_delay (float): Time in seconds to wait before reconnecting
            max_reconnect_attempts (int): Maximum number of reconnection attempts
        """
        self.uri = uri
        self.on_message = on_message
        self.heartbeat_interval = heartbeat_interval
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self.websocket = None
        self.running = False
        self.last_message_time = 0
        self.connection_task = None
        self.processing_latency = []  # List to store message processing times
    
    async def connect(self) -> None:
        """Establish connection to the WebSocket endpoint."""
        logger.info(f"Connecting to WebSocket: {self.uri}")
        
        attempts = 0
        while attempts < self.max_reconnect_attempts:
            try:
                self.websocket = await websockets.connect(self.uri)
                logger.info("WebSocket connection established")
                self.running = True
                return
            except Exception as e:
                attempts += 1
                logger.error(f"Connection attempt {attempts} failed: {str(e)}")
                if attempts >= self.max_reconnect_attempts:
                    logger.critical("Maximum reconnection attempts reached")
                    raise
                await asyncio.sleep(self.reconnect_delay)
    
    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        if self.websocket:
            self.running = False
            await self.websocket.close()
            logger.info("WebSocket connection closed")
    
    async def send_heartbeat(self) -> None:
        """Send periodic heartbeat messages to keep the connection alive."""
        while self.running:
            try:
                if self.websocket and self.websocket.open:
                    # Many exchanges have specific heartbeat formats
                    # This is a generic example - adjust as needed for your exchange
                    heartbeat_msg = json.dumps({"type": "heartbeat", "timestamp": time.time()})
                    await self.websocket.send(heartbeat_msg)
                    logger.debug("Heartbeat sent")
                
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error sending heartbeat: {str(e)}")
    
    async def _process_message(self, message: str) -> None:
        """Process incoming message and measure processing latency."""
        start_time = time.time()
        
        try:
            # Parse JSON message
            data = json.loads(message)
            
            # Basic validation
            if not all(key in data for key in ["timestamp", "exchange", "symbol", "asks", "bids"]):
                logger.warning(f"Invalid message format: {message[:100]}...")
                return
            
            # Call the message handler
            self.on_message(data)
            
            # Record processing latency
            latency = time.time() - start_time
            self.processing_latency.append(latency)
            
            # Keep only the last 1000 measurements
            if len(self.processing_latency) > 1000:
                self.processing_latency.pop(0)
                
            # Update last message time
            self.last_message_time = time.time()
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message as JSON: {message[:100]}...")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    async def receive_messages(self) -> None:
        """Continuously receive and process messages from the WebSocket."""
        while self.running:
            try:
                if not self.websocket:
                    await self.connect()
                
                message = await self.websocket.recv()
                await self._process_message(message)
                
            except ConnectionClosed:
                logger.warning("WebSocket connection closed unexpectedly")
                await self.reconnect()
            except Exception as e:
                logger.error(f"Error receiving messages: {str(e)}")
                await self.reconnect()
    
    async def reconnect(self) -> None:
        """Attempt to reconnect to the WebSocket endpoint."""
        if not self.running:
            return
            
        logger.info("Attempting to reconnect...")
        try:
            if self.websocket:
                await self.websocket.close()
            await self.connect()
        except Exception as e:
            logger.error(f"Reconnection failed: {str(e)}")
    
    async def start(self) -> None:
        """Start the WebSocket client."""
        await self.connect()
        
        # Create tasks for receiving messages and sending heartbeats
        receive_task = asyncio.create_task(self.receive_messages())
        heartbeat_task = asyncio.create_task(self.send_heartbeat())
        
        # Store the main task
        self.connection_task = asyncio.gather(receive_task, heartbeat_task)
        
        # Wait for the tasks to complete
        try:
            await self.connection_task
        except asyncio.CancelledError:
            logger.info("WebSocket client tasks cancelled")
    
    async def stop(self) -> None:
        """Stop the WebSocket client."""
        self.running = False
        
        if self.connection_task:
            self.connection_task.cancel()
            
        await self.disconnect()
    
    def get_average_latency(self) -> float:
        """Get the average processing latency in milliseconds."""
        if not self.processing_latency:
            return 0.0
        return sum(self.processing_latency) / len(self.processing_latency) * 1000  # Convert to ms