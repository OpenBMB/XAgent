"""Replayer Websocket Server
"""
import json
import os
import asyncio
import random
from datetime import datetime
from urllib.parse import parse_qs
from typing import Any

from colorama import Fore
from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session
from starlette.endpoints import WebSocketEndpoint
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.application.cruds.interaction import InteractionCRUD
from XAgentServer.application.dependence import get_db
from XAgentServer.application.schemas.response_body import WebsocketResponseBody
from XAgentServer.exts.exception_ext import XAgentWebSocketConnectError
from XAgentServer.loggers.logs import Logger

from XAgentServer.application.websockets.common import check_user, handle_data, handle_workspace_filelist

router = APIRouter()


@router.websocket("/ws/share/{client_id}", name="ws_replay")
class ReplayServer(WebSocketEndpoint):
    """Main Websocket Server
    Extends:
        WebSocketEndpoint
    
    Description:
        In this websocket, we will receive the args from user,
        and you can use it to run the interaction.
        specifically, the args is a dict, 
        and it must contain a key named "goal" to tell XAgent what do you want to do.

    """

    def __init__(self, websocket: WebSocket, db: Session = Depends(get_db), client_id: str = ""):
        super().__init__(websocket.scope, websocket.receive, websocket.send)
        self.db = db
        self.client_id: str = client_id
        self.websocket = websocket
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.log_dir = ""
        self.logger = None
        self.scheduler = AsyncIOScheduler()
        
    async def dispatch(self) -> None:
        """_summary_

        Raises:
            exc: _description_
        """
        websocket = WebSocket(self.scope, receive=self.receive, send=self.send)
        close_code = 1000
        await self.on_connect(websocket)
        try:
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.receive":
                    data = await self.decode(websocket, message)
                    await self.on_receive(websocket, data)
                elif message["type"] == "websocket.disconnect":
                    close_code = 1000
                    break
        except Exception as exc:
            close_code = 1011
            raise exc
        finally:
            await self.on_disconnect(websocket, close_code)
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.logger.info("shutdown scheduler")
            if self.db:
                self.db.close()
                self.logger.info("close db")
            
    async def on_connect(self, websocket: WebSocket):
        """Connect to client

        Args:
            websocket (WebSocket): A websocket object

        Raises:
            XAgentWebSocketConnectError: If the user is running, it will raise this error.
        """
        
        self.log_dir = os.path.join(os.path.join(XAgentServerEnv.base_dir, "localstorage",
                                    "interact_records"), self.date_str, self.client_id)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = Logger(
            log_dir=self.log_dir, log_file="share.log", log_name=f"{self.client_id}_SHARE")
        query_string = self.scope.get("query_string", b"").decode()
        parameters = parse_qs(query_string)
        user_id = parameters.get("user_id", [""])[0]
        token = parameters.get("token", [""])[0]
        self.logger.typewriter_log(
            title=f"Receive connection from {self.client_id}: ",
            title_color=Fore.RED,
            content=f"user_id: {user_id}, token: {token}")
        await websocket.accept()
        try:
            # await check_user(db=self.db, user_id=user_id, token=token)
            # check running, you can edit it by yourself in envs.py to skip this check
            if XAgentServerEnv.check_running:
                if InteractionCRUD.is_running(db=self.db, user_id=user_id):
                    raise XAgentWebSocketConnectError(
                        "You have a running interaction, please wait for it to finish!")
        except XAgentWebSocketConnectError as exc:
            await websocket.send_text(
                WebsocketResponseBody(
                    status="connect",
                    success=False,
                    message=str(exc),
                    data=None).to_text())
            await websocket.close(code=1000)
            return
        await websocket.send_text(
            WebsocketResponseBody(
                status="connect",
                success=True,
                message="connect success",
                data=None).to_text())

    async def on_disconnect(self, websocket: WebSocket, close_code):
        """When disconnect with client, it will run this function
        Override this function to do something when disconnect with client
        
        Args:
            websocket (WebSocket): A websocket object
            close_code (_type_): The close code, default is 0
        """
        self.logger.typewriter_log(
            title=f"Disconnect with client {self.client_id}: ",
            title_color=Fore.RED)
        

    async def on_receive(self, websocket: WebSocket, data: Any):
        """
        When receive data from client, it will run this function
        
        Args:
            websocket (WebSocket): A websocket object
            data (any): The data from client
        """
        data = json.loads(data)
        self.logger.typewriter_log(
            title=f"Receive data from {self.client_id}: ",
            title_color=Fore.RED,
            content=json.dumps(data, indent=4, ensure_ascii=False)
        )
        if data.get("type", "") == "ping":
            # await self.pong()
            pass
        elif data.get("type", "") == "shared":
            if not self.scheduler.running:
                self.scheduler.add_job(self.pong, "interval", seconds=20)
                self.scheduler.add_job(self.send_data, "date", next_run_time=datetime.now())
                self.scheduler.start()
                 
    async def pong(self):
        """
        pong to client for keeping alive
        """
        await self.websocket.send_text(json.dumps({"type": "pong"}, ensure_ascii=False, indent=2))

    async def send_data(self):
        """
        send data to client
        """
        try:
            rows = InteractionCRUD.search_many_raws(db=self.db, interaction_id=self.client_id)
            for row in rows:
                self.logger.typewriter_log(
                    title=f"Send data to {self.client_id}: ",
                    title_color=Fore.RED,
                    content=f"Send {row.node_id}data to client, length: {len(json.dumps(row.data))}."
                )
                root_dir = os.path.join(XAgentServerEnv.base_dir, "localstorage", "interact_records", row.create_time[:10], row.interaction_id)
                await self.websocket.send_text(
                    WebsocketResponseBody(status=row.status,
                                        success=True, message="success",
                                        data=handle_data(row=row, root_dir=root_dir),
                                        current=row.current,
                                        node_id=row.node_id,
                                        workspace_file_list=handle_workspace_filelist(row.file_list)).to_text())
                await asyncio.sleep(random.randint(1, 3))
            if self.scheduler.running:
                self.scheduler.shutdown()
        except:
            if self.scheduler.running:
                self.scheduler.shutdown()