import traceback
from fastapi import WebSocket
from XAgentIO.exception import XAgentIOWebSocketDisconnectError
from XAgentIO.output.base import BaseOutput
from XAgentServer.response_body import WebsocketResponseBody


class WebSocketOutput(BaseOutput):

    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.websocket = websocket

    def set_logger(self, logger):
        self.logger = logger

    async def run(self, output: dict):
        try:
            websocket_data = WebsocketResponseBody(**output).to_text()
            await self.websocket.send_text(websocket_data)
        except Exception as e:
            self.logger.info(traceback.format_exc())
            raise XAgentIOWebSocketDisconnectError

