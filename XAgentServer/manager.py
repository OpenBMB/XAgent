from __future__ import annotations

import asyncio
import os
import threading
from typing import Dict, List

from fastapi import WebSocket, WebSocketDisconnect, status

from XAgentIO.exception import (XAgentIOWebSocketReceiveError,
                                XAgentIOWebSocketSendError)
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.loggers.logs import Logger
from XAgentServer.response_body import WebsocketResponseBody


class Singleton(type):
    """
    Metaclass to define a class as a Singleton.
    
    Attributes:
        _instances (Dict): Stores the instances of the Singleton classes created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Returns the instance of the class if exists else creates and returns a new instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            An instance of the Singleton class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class WebSocketConnectionManager(metaclass=Singleton):
    """
    Manages websocket connections.
    
    Attributes:
        active_connections (List[Dict[str, WebSocket]]): Stores the details of all the active connections.
        logger (Logger): A Logger instance to log information, warning and error messages.
    """

    def __init__(self):
        """
        Initializes the WebSocketConnectionManager instance.
        """
        self.active_connections: List[Dict[str, WebSocket]] = []
        self.logger = Logger(log_dir=os.path.join(XAgentServerEnv.base_dir, "logs"), log_file="websocket.log")
        
        self.create_pong_task()

    async def connect(self, websocket: WebSocket, websocket_id: str):
        """
        Connects to a websocket and adds it to the list of active connections.

        Args:
            websocket (WebSocket): A WebSocket instance representing the websocket to connect.
            websocket_id (str): The ID to be used for the websocket connection.

        """
        await websocket.accept()
        self.logger.info(f"websocket {websocket_id} connected")
        self.active_connections.append({websocket_id: websocket})

    async def disconnect(self, websocket_id: str, websocket: WebSocket):
        """
        Removes a websocket connection from the list of active connections.

        Args:
            websocket_id (str): The ID of the websocket connection to remove.
            websocket (WebSocket): A WebSocket instance representing the websocket connection to remove.
        """
        self.active_connections.remove({websocket_id: websocket})
        self.logger.info(f"websocket {websocket_id} remove from active connections")

    def is_connected(self, websocket_id: str) -> bool:
        """
        Checks if a websocket connection is active.

        Args:
            websocket_id (str): The ID of the websocket connection to check.

        Returns:
            True if the websocket connection is active, False otherwise.
        """
        for connection in self.active_connections:
            if websocket_id in connection.keys():
                return True
        return False
    
    def get_connection(self, websocket_id: str) -> WebSocket:
        """
        Retrieves the WebSocket instance of an active connection.

        Args:
            websocket_id (str): The ID of the websocket connection to retrieve.

        Returns:
            A WebSocket instance representing the connection if exists, None otherwise.
        """
        for connection in self.active_connections:
            if websocket_id in connection.keys():
                return connection[websocket_id]
        return None
    

    async def broadcast_pong(self):
        """
        Periodically sends a message to all active websocket connections.
        """
        while True:
            
            self.logger.info(f"pong broadcast for active connections: {len(self.active_connections)}")
            
            for connection in self.active_connections:
                for websocket_id, websocket in connection.items():
                    try:
                        await websocket.send_text(WebsocketResponseBody(status="pong", data={"type": "pong"}, message="pong").to_text())
                    except Exception as e:
                        self.logger.error(f"websocket {websocket_id} is disconnected")
                        self.active_connections.remove(connection)
                        continue
            await asyncio.sleep(20)
            

    def loop_pong(self):
        """
        Starts an infinite loop to broadcast messages to active connections.
        """
        asyncio.run(self.broadcast_pong())

    def create_pong_task(self):
        """
        Creates a new daemon thread to continuously broadcast messages to active connections.
        """
        self.logger.info("Create task for pong broadcast")
        pong = threading.Thread(target=self.loop_pong, daemon=True)
        pong.start()