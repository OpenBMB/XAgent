import traceback
from fastapi import WebSocket
from XAgentIO.exception import XAgentIOWebSocketDisconnectError
from XAgentIO.output.base import BaseOutput
from XAgentServer.response_body import WebsocketResponseBody


class WebSocketOutput(BaseOutput):
    """
    A class used to handle WebSocket output.

    Attributes:
    ----------
    websocket : WebSocket,
        Socket instance to send the output to.

    Methods:
    -------
    set_logger(logger)
        Sets the logger to be used in WebSocketOutput instance.

    async run(output)
        Processes the output and sends it through the websocket.
    """
    
    def __init__(self, websocket: WebSocket):
        """
        Initializes an instance of the WebSocketOutput class.

        Args:
        -----
        websocket (WebSocket):
            A websocket instance that this WebSocketOutput will use to send output.
        """
        super().__init__()
        self.websocket = websocket

    def set_logger(self, logger):
        """
        Sets the logger to be used in WebSocketOutput instance.

        Args:
        -----
        logger : logging.Logger,
            A logger instance to be used in WebSocketOutput
        """
        self.logger = logger

    async def run(self, output: dict):
        """
        Processes the output and sends it through the websocket. If it fails,
        it logs the error and raises a XAgentIOWebSocketDisconnectError.

        Args:
        -----
        output (dict):
            The python dictionary that needs to be sent through the websocket.

        Raises:
        ------
        XAgentIOWebSocketDisconnectError:
            If sending output through the websocket fails.
        """
        try:
            websocket_data = WebsocketResponseBody(**output).to_text()
            await self.websocket.send_text(websocket_data)
        except Exception as e:
            self.logger.info(traceback.format_exc())
            raise XAgentIOWebSocketDisconnectError