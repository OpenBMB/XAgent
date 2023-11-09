import asyncio
import json

from fastapi import WebSocket, WebSocketDisconnect

from XAgentIO.exception import (
    XAgentIOWebSocketDisconnectError,
    XAgentIOWebSocketTimeoutError,
)
from XAgentIO.input.base import BaseInput
from XAgentServer.loggers.logs import Logger
from XAgentServer.response_body import WebsocketResponseBody


class WebSocketInput(BaseInput):
    def __init__(
        self,
        websocket: WebSocket,
        do_interrupt: bool = False,
        max_wait_seconds: int = 600,
    ):
        super().__init__(do_interrupt, max_wait_seconds)
        self.websocket = websocket

    def set_logger(self, logger: Logger):
        self.logger = logger

    def set_interrupt(self, do_interrupt: bool = True):
        self.do_interrupt = do_interrupt

    async def interrupt(self):
        wait = 0
        while wait < self.max_wait_seconds:
            print(
                f"\r waiting for {wait} second, remaining {self.max_wait_seconds - wait} second",
                end="",
            )
            try:
                data = await asyncio.wait_for(self.auto_receive(), 1)
                if isinstance(data, dict):
                    data_type = data.get("type", None)
                    if data_type == "ping":
                        await self.websocket.send_json({"type": "pong"})
                        continue
                    if data_type == "data":
                        self.logger.info(f"Receiving data change request...")
                        self.logger.info(f"Received ：{data}")
                        wait = 0
                        return data
                else:
                    pass
            except asyncio.TimeoutError:
                wait += 1
        self.logger.error(f"Wait timeout, close.")
        self.websocket.send_text(
            WebsocketResponseBody(
                data=None, status="failed", message="Wait timeout, close."
            ).to_text()
        )
        raise XAgentIOWebSocketTimeoutError

    async def auto_receive(self):
        data = await self.websocket.receive_json()
        return data

    async def run(self, input):
        if self.do_interrupt:
            data = await self.interrupt()
            return data
        else:
            return input
