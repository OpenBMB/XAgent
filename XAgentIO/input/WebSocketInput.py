import asyncio
import json

from fastapi import WebSocket, WebSocketDisconnect

from XAgentIO.exception import (XAgentIOWebSocketDisconnectError,
                                XAgentIOWebSocketTimeoutError)
from XAgentIO.input.base import BaseInput
from XAgentServer.loggers.logs import Logger
from XAgentServer.response_body import WebsocketResponseBody


class WebSocketInput(BaseInput):
    """WebSocket input class provides efficient, asyncio-based methods for handling WebSocket input data.
    
    Attributes:
        websocket (WebSocket): WebSocket object where data is being received from.
        logger (Logger): A Logger object used for logging debug and error information.

    """

    def __init__(self, websocket: WebSocket, do_interrupt: bool = False, max_wait_seconds: int = 600):
        """Initializes a new instance of the WebSocketInput class.
        
        Args:
            websocket (WebSocket): WebSocket object where data is being received from.
            do_interrupt (bool, optional): Boolean value indicating whether to interrupt data input, defaults to False.
            max_wait_seconds (int, optional): Maximum seconds to wait for data input before raising a TimeoutError, defaults to 600.
        
        """
        super().__init__(do_interrupt, max_wait_seconds)
        self.websocket = websocket

    def set_logger(self, logger: Logger):
        """Sets the logger attribute with the provided Logger object.
        
        Args:
            logger (Logger): The Logger object to set the logger attribute with.

        """
        self.logger = logger

    def set_interrupt(self, do_interrupt: bool = True):
        """Sets the do_interrupt attribute with the provided Boolean value.
        
        Args:
            do_interrupt (bool, optional): The Boolean value to set the do_interrupt attribute with, defaults to True.
            
        """
        self.do_interrupt = do_interrupt

    async def interrupt(self):
        """Waits for data for the specified max_wait_seconds, returning the received data if successful.
        
        Raises:
            XAgentIOWebSocketTimeoutError: If no WebSocket data is received within the designated wait time.

        Returns:
            dict: The received data as a dictionary if successful, otherwise raises an Error.

        """
        wait = 0
        while wait < self.max_wait_seconds:
            print (f"\r waiting for {wait} second, remaining {self.max_wait_seconds - wait} second", end="")
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
        self.websocket.send_text(WebsocketResponseBody(data=None, status="failed", message="Wait timeout, close.").to_text())
        raise XAgentIOWebSocketTimeoutError

        
    async def auto_receive(self):
        """Receives JSON-formatted data from the websocket.
        
        Returns:
            dict: The received data as a dictionary.

        """
        data = await self.websocket.receive_json()
        return data

    async def run(self, input):
        """Runs the interrupt if do_interrupt is set to True, otherwise returns the received data.
        
        Args:
            input (dict): The received data as a dictionary.
            
        Returns:
            dict: The received data as a dictionary.

        """
        if self.do_interrupt:
            data = await self.interrupt()
            return data
        else:
            return input