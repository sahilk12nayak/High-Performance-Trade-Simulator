"""
WebSocket manager for connecting to exchange data feeds
"""
import json
import logging
import asyncio
import threading
import time
import websockets
from typing import Dict, Any, Optional

from src.config import EXCHANGES

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections to exchange data feeds"""
    
    def __init__(self, simulator):
        """Initialize the WebSocket manager"""
        self.simulator = simulator
        self.websocket = None
        self.running = False
        self.thread = None
        self.last_message_time = 0
        self.message_count = 0
        
        logger.info("WebSocket manager initialized")
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.running and self.thread is not None and self.thread.is_alive()
    
    def connect(self) -> None:
        """Connect to the WebSocket feed"""
        if self.is_connected():
            logger.warning("Already connected to WebSocket feed")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_websocket_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Connecting to {self.simulator.exchange} WebSocket feed for {self.simulator.pair}")
    
    def disconnect(self) -> None:
        """Disconnect from the WebSocket feed"""
        if not self.is_connected():
            logger.warning("Not connected to WebSocket feed")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        logger.info("Disconnected from WebSocket feed")
    
    def _run_websocket_loop(self) -> None:
        """Run the WebSocket event loop in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._websocket_handler())
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            loop.close()
            logger.info("WebSocket event loop closed")
    
    async def _websocket_handler(self) -> None:
        """Handle WebSocket connection and messages"""
        exchange = self.simulator.exchange
        pair = self.simulator.pair
        
        if exchange not in EXCHANGES:
            logger.error(f"Unknown exchange: {exchange}")
            return
        
        # Construct WebSocket URL
        base_url = EXCHANGES[exchange].websocket_url
        url = f"{base_url}{pair}"
        
        logger.info(f"Connecting to WebSocket: {url}")
        
        try:
            async with websockets.connect(url) as websocket:
                self.websocket = websocket
                logger.info(f"Connected to {url}")
                
                while self.running:
                    try:
                        message = await websocket.recv()
                        self._process_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed")
                        break
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            self.websocket = None
            logger.info("WebSocket connection handler exited")
    
    def _process_message(self, message: str) -> None:
        """Process a WebSocket message"""
        start_time = time.time()
        
        try:
            data = json.loads(message)
            
            # Update message statistics
            self.message_count += 1
            self.last_message_time = start_time
            
            # Process the orderbook data
            self.simulator.process_orderbook(data)
            
            # Calculate processing latency
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.simulator.update_latency(latency)
            
            if self.message_count % 100 == 0:
                logger.debug(f"Processed {self.message_count} messages, latest latency: {latency:.2f} ms")
        
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")
        except Exception as e:
            logger.error(f"Error processing message: {e}")