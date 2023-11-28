"""Recorder Websocket Server"""
import json
import os
import threading
import uuid
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
from XAgentServer.exts.exception_ext import XAgentWebSocketConnectError, XAgentError
from XAgentServer.interaction import XAgentInteraction
from XAgentServer.loggers.logs import Logger
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.raw import XAgentRaw
from XAgentServer.server import XAgentServer
from XAgentServer.enums.status import StatusEnum
from XAgentServer.application.websockets.common import (check_user,
                                                        handle_data,
                                                        handle_workspace_filelist)
from XAgentServer.application.global_val import redis


router = APIRouter()


@router.websocket("/ws/recorder/{client_id}", name="ws")
class RecorderServer(WebSocketEndpoint):
    """Recorder Websocket Server
    Extends:
        WebSocketEndpoint
    
    Recorder:
        You can use this to reproduce the recorder you have executed
        You can find this in XAgent GUI Menu: Settings -> Run Recorder

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
        self.continue_flag = True

    async def dispatch(self) -> None:
        """XAgent Websocket Server Dispatch Function
        extend from WebSocketEndpoint

        override this function block: loop flag and finally block to do something
        Raises:
            exc: extend from WebSocketEndpoint
        """
        websocket = WebSocket(self.scope, receive=self.receive, send=self.send)
        close_code = 1000
        await self.on_connect(websocket)
        redis.set_key(f"{self.client_id}", "alive")
        try:
            while self.continue_flag:
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
            try:
                await self.on_disconnect(websocket, close_code)
                if self.scheduler.running:
                    self.scheduler.shutdown()
                    self.logger.info("shutdown scheduler")
                if self.db:
                    self.db.close()
                    self.logger.info("close db")
            finally:
                # this is notice the agent to stop if user close the websocket
                redis.set_key(f"{self.client_id}", "close")

    async def on_connect(self, websocket: WebSocket):
        """Connect to client

        Args:
            websocket (WebSocket): A websocket object

        Raises:
            XAgentWebSocketConnectError: If you have an interaction running, 
            you can't connect to XAgent
        """

        self.log_dir = os.path.join(os.path.join(XAgentServerEnv.base_dir, "localstorage",
                                    "interact_records"), self.date_str, self.client_id)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = Logger(
            log_dir=self.log_dir, log_file="interact.log", log_name=f"{self.client_id}_INTERACT")
        query_string = self.scope.get("query_string", b"").decode()
        parameters = parse_qs(query_string)
        user_id = parameters.get("user_id", [""])[0]
        token = parameters.get("token", [""])[0]
        recorder_dir = parameters.get("recorder_dir", [""])[0]
        description = "XAgent Recorder"
        self.logger.typewriter_log(
            title=f"Receive connection from {self.client_id}: ",
            title_color=Fore.RED,
            content=f"user_id: {user_id}, token: {token}, recorder_dir: {recorder_dir}")
        await websocket.accept()
        try:
            await check_user(db=self.db, user_id=user_id, token=token)
            # check running, you can edit it by yourself in envs.py to skip this check
            if XAgentServerEnv.check_running:
                if InteractionCRUD.is_running(db=self.db, user_id=user_id):
                    raise XAgentWebSocketConnectError(
                        "You have a running interaction, please wait for it to finish!")

            base = InteractionBase(interaction_id=self.client_id,
                                user_id=user_id,
                                create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                description=description if description else "XAgent Recorder",
                                agent="XAgent",
                                mode="auto",
                                file_list=[],
                                recorder_root_dir=os.path.join(
                                    XAgentServerEnv.recorder_root_dir, recorder_dir),
                                status="waiting",
                                message="waiting...",
                                current_step=uuid.uuid4().hex,
                                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                call_method="recorder",
                                )
            InteractionCRUD.create_interaction(db=self.db, base=base)
        except XAgentWebSocketConnectError as e:
            self.logger.error(
                f"Error in on_connect of {self.client_id}: {e}")
            await websocket.send_text(
                WebsocketResponseBody(
                    status="failed",
                    success=False,
                    message=str(e),
                    data=None).to_text())
            await websocket.close(code=1000)
            return
        await websocket.send_text(
            WebsocketResponseBody(
                status="connect",
                success=True,
                message="connect success",
                data=base.to_dict()).to_text())

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
        # await websocket.close(code=close_code)

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
        elif data.get("type", "") == "recorder":
            if not self.scheduler.running:
                self.scheduler.add_job(self.pong, "interval", seconds=20)
                self.scheduler.add_job(self.send_data, "interval", seconds=1)
                self.scheduler.start()
                t = threading.Thread(target=self.task_handler)
                t.start()


    def task_handler(self):
        """
        define a long task to run interaction
        
        Args:
            parameter (InteractionParameter): The parameter of interaction
        """
        try:
            InteractionCRUD.insert_raw(db=self.db, process=XAgentRaw(
                interaction_id=self.client_id,
                node_id=uuid.uuid4().hex,
                status=StatusEnum.RUNNING,
                create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                current="",
                step=-1,
                data=None,
                file_list=[],
                do_interrupt=False,
                wait_seconds=0,
                ask_for_human_help=False,
                is_human=True,
                human_data=None,
                human_file_list=[],
                is_send=False,
                is_receive=False,
                is_deleted=False
            ))
            redis.set_key(f"{self.client_id}_send", 1)

            current_step = uuid.uuid4().hex
            base = InteractionCRUD.get_interaction(db=self.db,
                                                interaction_id=self.client_id)
            InteractionCRUD.update_interaction_status(db=self.db,
                                                    interaction_id=base.interaction_id,
                                                    status="running",
                                                    message="running",
                                                    current_step=current_step)

            # Create XAgentInteraction to run interaction
            interaction = XAgentInteraction(
                base=base, parameter=None, interrupt=False, call_method="recorder")

            # Register logger, dbinto interaction
            interaction.resister_logger(self.logger)
            self.logger.info(
                f"Register logger into interaction of {base.interaction_id}, done!")

            interaction.register_db(db=self.db)
            self.logger.info(
                f"Register db into interaction of {base.interaction_id}, done!")
            # Create XAgentServer
            server = XAgentServer(logger=self.logger)
            self.logger.info(
                f"Register logger into XAgentServer of {base.interaction_id}, done!")
            self.logger.info(
                f"Start a new thread to run interaction of {base.interaction_id}, done!")
            # await server.interact(interaction=interaction)
            server.interact(interaction=interaction)
        except XAgentError as e:
            self.logger.error(
                f"Error in task_handler of {self.client_id}: {e}")
            InteractionCRUD.insert_error(
                db=self.db, interaction_id=self.client_id, message=str(e))
            redis.set_key(self.client_id + "_send", 1)
            InteractionCRUD.update_interaction_status(db=self.db,
                                                      interaction_id=self.client_id,
                                                      status="failed",
                                                      message=str(e),
                                                      current_step=current_step)

    async def pong(self):
        """
        pong to client for keeping alive
        """
        await self.websocket.send_text(json.dumps({"type": "pong"}, ensure_ascii=False, indent=2))

    async def send_data(self):
        """
        send data to client
        """
        send_status = redis.get_key(f"{self.client_id}_send")
        if send_status:
            rows = InteractionCRUD.get_next_send(
                db=self.db, interaction_id=self.client_id)
            rows = rows[::-1]
            for row in rows:
                if not row.is_send:
                    self.logger.typewriter_log(
                        title=f"Send data to {self.client_id}: ",
                        title_color=Fore.RED,
                        content=f"Send {row.node_id}data to client, length: {len(json.dumps(row.data))}."
                    )
                    if row.status in [StatusEnum.FAILED]:
                        # when interaction is falied, we will send the message to client
                        # and the message is the result of interaction
                        message = row.data
                    else:
                        message = "success"

                    root_dir = os.path.join(XAgentServerEnv.base_dir,
                                            "localstorage",
                                            "interact_records",
                                            row.create_time[:10],
                                            row.interaction_id)
                    await self.websocket.send_text(
                        WebsocketResponseBody(
                            status=row.status,
                            success=True, message=message,
                            data=handle_data(row=row, root_dir=root_dir),
                            current=row.current,
                            node_id=row.node_id,
                            workspace_file_list=handle_workspace_filelist(
                                row.file_list)
                        ).to_text())
                    InteractionCRUD.update_send_flag(
                        db=self.db, interaction_id=self.client_id, node_id=row.node_id)
                    redis.delete_key(f"{self.client_id}_send")

                    if row.status in [StatusEnum.FAILED, StatusEnum.FINISHED]:
                        self.continue_flag = False
                        break
