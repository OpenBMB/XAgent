"""
Base Websocket Server
Note:
    You can use this websocket to run your interaction.
    You can modify it by yourself to do something,
    such as change the way to receive data from client,
    or use celery to run interaction,
    or use ThreadPoolExecutor to run interaction and so on.
Version: 1.1.0
Attention:
    Since Version: 1.1.0, Local storage will no longer be supported, replaced by Mysql and only
Components:
    Websocket is a way for long connect with client
    MySQL to save xagent data
    Redis to save status of interaction
    Threading to run interaction
    APScheduler to send data to client and keep alive
    FastAPI APIRouter to manage websocket route
    XAgentError in XAgentServer.exts.exception_ext
"""
import json
import os
import threading
import traceback
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
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.raw import XAgentRaw
from XAgentServer.server import XAgentServer
from XAgentServer.enums.status import StatusEnum
from XAgentServer.application.websockets.common import (check_user,
                                                        handle_data,
                                                        handle_workspace_filelist)
from XAgentServer.application.global_val import redis


router = APIRouter()


# @router.websocket_route("/ws/{client_id}", name="ws")
@router.websocket("/ws/base/{client_id}", name="ws")
class MainServer(WebSocketEndpoint):
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
            interaction = InteractionCRUD.get_interaction(
                db=self.db, interaction_id=self.client_id)
            if interaction.status not in [StatusEnum.FINISHED, StatusEnum.FAILED]:
                InteractionCRUD.update_interaction_status(db=self.db,
                                                          interaction_id=self.client_id,
                                                          status=StatusEnum.CLOSED,
                                                          message="closed",
                                                          current_step="0")
            try:
                await self.on_disconnect(websocket, close_code)
                if self.scheduler.running:
                    self.scheduler.shutdown()
                    self.logger.info("shutdown scheduler")
                if self.db:
                    self.db.close()
                    self.logger.info("close db")
            finally:
                # notice the agent stop if user close the websocket
                redis.set_key(f"{self.client_id}", "close")

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
            log_dir=self.log_dir, log_file="interact.log", log_name=f"{self.client_id}_INTERACT")
        query_string = self.scope.get("query_string", b"").decode()
        parameters = parse_qs(query_string)
        user_id = parameters.get("user_id", [""])[0]
        token = parameters.get("token", [""])[0]
        description = parameters.get("description", [""])[0]
        self.logger.typewriter_log(
            title=f"Receive connection from {self.client_id}: ",
            title_color=Fore.RED,
            content=f"user_id: {user_id}, token: {token}, description: {description}")
        await websocket.accept()
        try:
            await check_user(db=self.db, user_id=user_id, token=token)
            # check running, you can edit it by yourself in envs.py to skip this check
            if XAgentServerEnv.check_running:
                if InteractionCRUD.is_running(db=self.db, user_id=user_id):
                    raise XAgentWebSocketConnectError(
                        "You have a running interaction, please wait for it to finish!")
            base = InteractionCRUD.get_interaction(db=self.db,
                                                   interaction_id=self.client_id)
            if base is None:
                raise XAgentWebSocketConnectError(
                    "init interaction failed, please restart!")

            InteractionCRUD.update_interaction(db=self.db,
                                               base_data={
                                                   "interaction_id": self.client_id,
                                                   "status": "connected",
                                                   "message": "connected",
                                                   "current_step": "0",
                                                   "description": description}
                                               )

        except XAgentWebSocketConnectError as e:
            self.logger.error(
                f"Error in on_connect of {self.client_id}: {e}")
            await websocket.send_text(
                WebsocketResponseBody(
                    status="connect",
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
        if data.get("type", "") != "ping":
            self.logger.typewriter_log(
                title=f"Receive data from {self.client_id}: ",
                title_color=Fore.RED,
                content=json.dumps(data, indent=4, ensure_ascii=False)
            )
        if data.get("type", "") == "data":
            args = data.get("args", {})
            agent = data.get("agent", "")
            mode = data.get("mode", "")
            file_list = data.get("file_list", [])
            node_id = data.get("node_id", "")
            parameter = InteractionParameter(
                interaction_id=self.client_id,
                parameter_id=uuid.uuid4().hex,
                args=args,
            )
            InteractionCRUD.add_parameter(db=self.db, parameter=parameter)

            if node_id:
                InteractionCRUD.update_human_data(
                    db=self.db, interaction_id=self.client_id, node_id=node_id, human_data=args)
                redis.set_key(f"{self.client_id}_{node_id}_receive", 1)

            else:
                InteractionCRUD.update_interaction(db=self.db,
                                                   base_data={
                                                       "interaction_id": self.client_id,
                                                       "agent": agent,
                                                       "mode": mode,
                                                       "file_list": file_list,
                                                       "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                                                   )
                # Create a new raw data to record
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
                    do_interrupt=mode != "auto",
                    wait_seconds=0,
                    ask_for_human_help=False,
                    is_human=True,
                    human_data=args,
                    human_file_list=file_list,
                    is_send=False,
                    is_receive=False,
                    is_deleted=False
                ))
                redis.set_key(f"{self.client_id}_send", 1)

            if not self.scheduler.running:
                # add pong job to scheduler
                self.scheduler.add_job(self.pong, "interval", seconds=20)
                # add send data job to scheduler
                self.scheduler.add_job(self.send_data, "interval", seconds=1)
                self.scheduler.start()

                # start a new thread to run interaction
                t = threading.Thread(
                    target=self.task_handler, args=(parameter,))
                t.start()

    def task_handler(self, parameter: InteractionParameter):
        """
        define a long task to run interaction

        Args:
            parameter (InteractionParameter): The parameter of interaction
        """

        try:
            current_step = uuid.uuid4().hex
            base = InteractionCRUD.get_interaction(db=self.db,
                                                   interaction_id=self.client_id)
            InteractionCRUD.update_interaction_status(db=self.db,
                                                      interaction_id=base.interaction_id,
                                                      status="running",
                                                      message="running",
                                                      current_step=current_step)

            # if mode is not auto, we will interrupt the interaction
            # and you can change the wait_seconds
            # default 10 min.
            interaction = XAgentInteraction(
                base=base,
                parameter=parameter,
                interrupt=base.mode != "auto")

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
            traceback.print_exc()
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
        try:
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

                        await self.websocket.send_text(
                            WebsocketResponseBody(
                                status=row.status,
                                success=True, message=message,
                                data=handle_data(row=row, root_dir=self.log_dir),
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
        except Exception as e:
            self.logger.error(
                f"Error in send_data of {self.client_id}: {e}")
            traceback.print_exc()
            self.continue_flag = False
            raise XAgentError(e) from e