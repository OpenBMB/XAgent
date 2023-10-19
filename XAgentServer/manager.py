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
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class WebSocketConnectionManager(metaclass=Singleton):
    def __init__(self):
        self.active_connections: List[Dict[str, WebSocket]] = []
        self.logger = Logger(log_dir=os.path.join(XAgentServerEnv.base_dir, "logs"), log_file="websocket.log")
        
        self.create_pong_task()

    async def connect(self, websocket: WebSocket, websocket_id: str):
        await websocket.accept()
        self.logger.info(f"websocket {websocket_id} connected")
        self.active_connections.append({websocket_id: websocket})

    async def disconnect(self, websocket_id: str, websocket: WebSocket):
        self.active_connections.remove({websocket_id: websocket})
        self.logger.info(f"websocket {websocket_id} remove from active connections")

    def is_connected(self, websocket_id: str) -> bool:
        for connection in self.active_connections:
            if websocket_id in connection.keys():
                return True
        return False
    
    def get_connection(self, websocket_id: str) -> WebSocket:
        for connection in self.active_connections:
            if websocket_id in connection.keys():
                return connection[websocket_id]
        return None
    

    async def broadcast_pong(self):
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
        asyncio.run(self.broadcast_pong())


    def create_pong_task(self):
        self.logger.info("Create task for pong broadcast")
        pong = threading.Thread(target=self.loop_pong, daemon=True)
        pong.start()
