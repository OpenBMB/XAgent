import asyncio
import json
import os
import random
import smtplib
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Annotated, Dict, List, Optional, Set, Union
from urllib.parse import parse_qs, urlparse

import uvicorn
import yagmail
from colorama import Fore
from fastapi import (
    Body,
    Cookie,
    Depends,
    FastAPI,
    File,
    Form,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
    WebSocket,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from markdown2 import markdown, markdown_path
from sqlalchemy.orm import Session
from starlette.endpoints import WebSocketEndpoint

from XAgentIO.BaseIO import XAgentIO
from XAgentIO.exception import (
    XAgentIOWebSocketConnectError,
    XAgentIOWebSocketReceiveError,
)
from XAgentIO.input.WebSocketInput import WebSocketInput
from XAgentIO.output.WebSocketOutput import WebSocketOutput
from XAgentServer.database import InteractionBaseInterface, UserBaseInterface
from XAgentServer.database.connect import DBConnection
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.exts.mail_ext import email_content
from XAgentServer.interaction import XAgentInteraction
from XAgentServer.loggers.logs import Logger
from XAgentServer.manager import WebSocketConnectionManager
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.response_body import ResponseBody, WebsocketResponseBody
from XAgentServer.server import XAgentServer
from XAgentServer.utils import AutoReplayUtil, ShareUtil

if not os.path.exists(os.path.join(XAgentServerEnv.base_dir, "logs")):
    os.makedirs(os.path.join(XAgentServerEnv.base_dir, "logs"))

logger = Logger(
    log_dir=os.path.join(XAgentServerEnv.base_dir, "logs"),
    log_file="app.log",
    log_name="XAgentServerApp",
)


app = FastAPI()


if XAgentServerEnv.DB.db_type != "file":
    connection = DBConnection(XAgentServerEnv)
else:
    connection = None


# 中间件
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # 默认响应
    response = Response("Internal server error", status_code=500)
    if XAgentServerEnv.DB.db_type in ["sqlite", "mysql", "postgresql"]:
        try:
            request.state.db = connection.db_session
            response = await call_next(request)
        finally:
            # 关闭数据库会话
            request.state.db.close()
    else:
        response = await call_next(request)
    return response


# 依赖项,获取数据库会话对象
def get_db(request: Request):
    if XAgentServerEnv.DB.db_type in ["sqlite", "mysql", "postgresql"]:
        return request.state.db
    else:
        return None


broadcast_lock = threading.Lock()
websocket_queue: asyncio.Queue = None
manager: WebSocketConnectionManager = None
executor: ThreadPoolExecutor = None
userInterface: UserBaseInterface = None
interactionInterface: InteractionBaseInterface = None
yag: yagmail.SMTP = None


async def startup_event():
    logger.info("XAgent Service Startup Param:")
    for key, item in XAgentServerEnv.__dict__.items():
        if not key.startswith("__"):
            logger.info(f"{' '*10}{key}: {item}")

    global websocket_queue
    global manager
    global executor
    global userInterface
    global interactionInterface
    global yag
    websocket_queue = asyncio.Queue()
    logger.info("init websocket_queue")
    logger.typewriter_log(
        title=f"XAgentServer is running on {XAgentServerEnv.host}:{XAgentServerEnv.port}",
        title_color=Fore.RED,
    )
    if XAgentServerEnv.default_login:
        logger.typewriter_log(
            title=f"Default user: admin, token: xagent-admin, you can use it to login",
            title_color=Fore.RED,
        )

    manager = WebSocketConnectionManager()
    logger.typewriter_log(title=f"init a websocket manager", title_color=Fore.RED)

    logger.typewriter_log(
        title=f"init a thread pool executor, max_workers: {XAgentServerEnv.workers}",
        title_color=Fore.RED,
    )
    executor = ThreadPoolExecutor(max_workers=XAgentServerEnv.workers)

    if XAgentServerEnv.DB.db_type in ["sqlite", "mysql", "postgresql"]:
        from XAgentServer.database.connect import DBConnection
        from XAgentServer.database.dbi import InteractionDBInterface, UserDBInterface

        userInterface = UserDBInterface(XAgentServerEnv)
        interactionInterface = InteractionDBInterface(XAgentServerEnv)

    else:
        from XAgentServer.database.lsi import (
            InteractionLocalStorageInterface,
            UserLocalStorageInterface,
        )

        logger.info("init localstorage connection: users.json")
        userInterface = UserLocalStorageInterface(XAgentServerEnv)
        logger.info("init localstorage connection: interaction.json")
        interactionInterface = InteractionLocalStorageInterface(XAgentServerEnv)

    if XAgentServerEnv.Email.send_email:
        yag = yagmail.SMTP(
            user=XAgentServerEnv.Email.email_user,
            password=XAgentServerEnv.Email.email_password,
            host=XAgentServerEnv.Email.email_host,
        )
        logger.info("init yagmail")

    ShareUtil.register_db(db=interactionInterface, user_db=userInterface)


@app.on_event("startup")
async def startup():
    await startup_event()


@app.on_event("shutdown")
async def shutdown():
    if websocket_queue:
        await websocket_queue.put(None)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400, content={"status": "failed", "message": exc.errors()}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_user_auth(user_id: str = Form(...), token: str = Form(...)):
    """ """
    if userInterface.user_is_exist(user_id=user_id) == False:
        return False
    if not userInterface.user_is_valid(user_id=user_id, token=token):
        return False
    return True


@app.post("/register")
async def register(
    email: str = Form(...),
    name: str = Form(...),
    corporation: str = Form(...),
    position: str = Form(...),
    industry: str = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    """ """
    userInterface.register_db(db)
    if userInterface.user_is_exist(email=email):
        return ResponseBody(success=False, message="user is already exist")

    token = uuid.uuid4().hex
    user = {
        "user_id": uuid.uuid4().hex,
        "email": email,
        "name": name,
        "token": token,
        "available": False,
        "corporation": corporation,
        "position": position,
        "industry": industry,
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        contents = email_content(user)

        if XAgentServerEnv.Email.send_email:
            yag.send(user["email"], "XAgent Token Verification", contents)
        else:
            user["available"] = True
        userInterface.add_user(user)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(traceback.format_exc())
        return ResponseBody(success=False, message="email send failed!", data=None)

    except:
        logger.error(traceback.format_exc())
        return ResponseBody(success=False, message="register failed", data=None)
    return ResponseBody(
        data=user,
        success=True,
        message="Register success, we will send a email to you!",
    )


@app.get("/auth")
async def auth(
    user_id: str = Query(...), token: str = Query(...), db: Session = Depends(get_db)
) -> ResponseBody:
    """ """
    userInterface.register_db(db)
    user = userInterface.get_user(user_id=user_id)
    if XAgentServerEnv.default_login and user_id == "admin" and token == "xagent-admin":
        return ResponseBody(data=user.to_dict(), success=True, message="auth success")

    if user == None:
        return ResponseBody(success=False, message="user is not exist")

    if user.token != token:
        return ResponseBody(success=False, message="token is not correct")
    expired_time = datetime.now() - datetime.strptime(
        user.update_time, "%Y-%m-%d %H:%M:%S"
    )
    if expired_time.seconds > 60 * 60 * 24 * 7:
        return ResponseBody(success=False, message="token is expired")
    if user.available == False:
        user.available = True
        user.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        userInterface.update_user(user)
    else:
        return ResponseBody(success=False, message="user is already available!")

    return ResponseBody(data=user.to_dict(), success=True, message="auth success")


@app.post("/login")
async def login(
    email: str = Form(...), token: str = Form(...), db: Session = Depends(get_db)
) -> ResponseBody:
    """ """
    userInterface.register_db(db)
    user = userInterface.get_user(email=email)
    if XAgentServerEnv.default_login and email == "admin" and token == "xagent-admin":
        return ResponseBody(data=user.to_dict(), success=True, message="auth success")
    if user == None:
        return ResponseBody(success=False, message="user is not exist")

    if user.token != token:
        return ResponseBody(success=False, message="token is not correct")
    if user.available == False:
        return ResponseBody(success=False, message="user is not available")

    return ResponseBody(data=user.to_dict(), success=True, message="login success")


@app.post("/check")
async def check(token: str = Form(...), db: Session = Depends(get_db)) -> ResponseBody:
    """ """
    userInterface.register_db(db)
    if token is None:
        return ResponseBody(success=False, message="token is none")

    check = userInterface.token_is_exist(token)

    if check is True:
        return ResponseBody(data=check, success=True, message="token is effective")

    return ResponseBody(data=check, success=True, message="token is invalid")


@app.post("/upload")
async def create_upload_files(
    files: List[UploadFile] = File(...),
    user_id: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    userInterface.register_db(db)
    if user_id == "":
        return ResponseBody(success=False, message="user_id is empty!")

    if userInterface.user_is_exist(user_id=user_id) == False:
        return ResponseBody(success=False, message="user is not exist!")

    if not userInterface.user_is_valid(user_id=user_id, token=token):
        return ResponseBody(success=False, message="user is not available!")

    if len(files) == 0:
        return ResponseBody(success=False, message="files is empty!")
    if len(files) > 5:
        files = files[:5]

    if not os.path.exists(os.path.join(XAgentServerEnv.Upload.upload_dir, user_id)):
        os.makedirs(os.path.join(XAgentServerEnv.Upload.upload_dir, user_id))

    for file in files:
        if file.content_type not in XAgentServerEnv.Upload.upload_allowed_types:
            return ResponseBody(
                success=False,
                message=f"file type is not correct! Only {', '.join(XAgentServerEnv.Upload.upload_allowed_types)} are allowed!",
            )
        if file.size > 1024 * 1024 * 1:
            return ResponseBody(
                success=False,
                message="file size is too large, limit is 1MB for each file!",
            )

    file_list = []
    for file in files:
        file_name = uuid.uuid4().hex + os.path.splitext(file.filename)[-1]
        with open(
            os.path.join(XAgentServerEnv.Upload.upload_dir, user_id, file_name), "wb"
        ) as f:
            f.write(await file.read())
            file_list.append(file_name)
    return ResponseBody(
        data={"user_id": user_id, "file_list": file_list},
        success=True,
        message="upload success",
    )


@app.post("/getUserInteractions")
async def get_all_interactions(
    user_id: str = Form(...),
    token: str = Form(...),
    page_size: int = Form(...),
    page_num: int = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    """ """
    userInterface.register_db(db)
    interactionInterface.register_db(db)
    if user_id == "":
        return ResponseBody(success=False, message="user_id is empty!")

    if userInterface.user_is_exist(user_id=user_id) == False:
        return ResponseBody(success=False, message="user is not exist!")

    if not userInterface.user_is_valid(user_id=user_id, token=token):
        return ResponseBody(success=False, message="user is not available!")

    data = interactionInterface.get_interaction_by_user_id(
        user_id=user_id, page_size=page_size, page_num=page_num
    )
    return ResponseBody(data=data, success=True, message="success")


@app.post("/getSharedInteractions")
async def get_all_interactions(
    user_id: str = Form(...),
    token: str = Form(...),
    page_size: int = Form(...),
    page_num: int = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    userInterface.register_db(db)
    interactionInterface.register_db(db)
    if user_id == "":
        return ResponseBody(success=False, message="user_id is empty!")
    if userInterface.user_is_exist(user_id=user_id) == False:
        return ResponseBody(success=False, message="user is not exist!")

    data = interactionInterface.get_shared_interactions(
        page_size=page_size, page_num=page_num
    )
    return ResponseBody(data=data, success=True, message="success")


@app.post("/shareInteraction")
async def share_interaction(
    user_id: str = Form(...),
    token: str = Form(...),
    interaction_id: str = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    userInterface.register_db(db)
    interactionInterface.register_db(db)
    if user_id == "":
        return ResponseBody(success=False, message="user_id is empty!")

    if userInterface.user_is_exist(user_id=user_id) == False:
        return ResponseBody(success=False, message="user is not exist!")
    if not userInterface.user_is_valid(user_id=user_id, token=token):
        return ResponseBody(success=False, message="user is not available!")

    interaction = interactionInterface.get_interaction(interaction_id=interaction_id)
    if interaction == None:
        return ResponseBody(
            success=False,
            message=f"Don't find any interaction by interaction_id: {interaction_id}, Please check your interaction_id!",
        )

    flag = ShareUtil.share_interaction(interaction_id=interaction_id, user_id=user_id)
    return ResponseBody(
        data=interaction.to_dict(),
        success=flag,
        message="success!" if flag else "Failed!",
    )


@app.post("/deleteInteraction")
async def get_all_interactions(
    user_id: str = Form(...),
    token: str = Form(...),
    interaction_id: str = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    """ """
    userInterface.register_db(db)
    interactionInterface.register_db(db)
    if user_id == "":
        return ResponseBody(success=False, message="user_id is empty!")

    if userInterface.user_is_exist(user_id=user_id) == False:
        return ResponseBody(success=False, message="user is not exist!")

    if not userInterface.user_is_valid(user_id=user_id, token=token):
        return ResponseBody(success=False, message="user is not available!")
    try:
        data = interactionInterface.delete_interaction(interaction_id=interaction_id)
    except Exception as e:
        return ResponseBody(success=False, message=f"delete failed! {e}")
    return ResponseBody(data=data, success=True, message="success")


@app.post("/updateInteractionConfig")
async def update_interaction_parameter(
    user_id: str = Form(...),
    token: str = Form(...),
    mode: str = Form(...),
    agent: str = Form(...),
    file_list: List[str] = Form(...),
    interaction_id: str = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    userInterface.register_db(db)
    interactionInterface.register_db(db)
    if user_id == "":
        return ResponseBody(success=False, message="user_id is empty!")

    if userInterface.user_is_exist(user_id=user_id) == False:
        return ResponseBody(success=False, message="user is not exist!")

    if not userInterface.user_is_valid(user_id=user_id, token=token):
        return ResponseBody(success=False, message="user is not available!")
    if interaction_id == "":
        return ResponseBody(success=False, message=f"interaction_id is empty!")
    interaction = interactionInterface.get_interaction(interaction_id=interaction_id)
    if interaction == None:
        return ResponseBody(
            success=False,
            message=f"Don't find any interaction by interaction_id: {interaction_id}, Please check your interaction_id!",
        )
    update_data = {
        "interaction_id": interaction_id,
        "agent": agent,
        "mode": mode,
        "file_list": [json.loads(l) for l in file_list],
    }
    interactionInterface.update_interaction(update_data)
    return ResponseBody(data=update_data, success=True, message="success!")


@app.post("/updateInteractionDescription")
async def update_interaction_description(
    user_id: str = Form(...),
    token: str = Form(...),
    description: str = Form(...),
    interaction_id: str = Form(...),
    db: Session = Depends(get_db),
) -> ResponseBody:
    userInterface.register_db(db)
    interactionInterface.register_db(db)
    if user_id == "":
        return ResponseBody(success=False, message="user_id is empty!")

    if userInterface.user_is_exist(user_id=user_id) == False:
        return ResponseBody(success=False, message="user is not exist!")

    if not userInterface.user_is_valid(user_id=user_id, token=token):
        return ResponseBody(success=False, message="user is not available!")
    if interaction_id == "":
        return ResponseBody(success=False, message=f"interaction_id is empty!")
    interaction = interactionInterface.get_interaction(interaction_id=interaction_id)
    if interaction == None:
        return ResponseBody(
            success=False,
            message=f"Don't find any interaction by interaction_id: {interaction_id}, Please check your interaction_id!",
        )
    update_data = {
        "interaction_id": interaction_id,
        "description": description if description else "XAgent",
    }
    interactionInterface.update_interaction(update_data)
    return ResponseBody(data=update_data, success=True, message="success!")


@app.websocket_route("/ws/{client_id}", name="ws")
class MainServer(WebSocketEndpoint):
    encoding: str = "text"
    session_name: str = ""
    count: int = 0
    client_id: str = ""
    websocket: WebSocket = None

    """
    In this websocket, we will receive the args from user,
    and you can use it to run the interaction.
    specifically, the args is a dict, and it must contain a key named "goal" to tell XAgent what do you want to do.
    and you can add other keys to the args to tell XAgent what do you want to do.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db: Session = None
        self.userInterface = userInterface
        self.interactionInterface = interactionInterface

    def register_db(self):
        if connection:
            self.db = connection.db_session
            logger.info("init websocket db session")
        else:
            self.db = None
        self.userInterface.register_db(self.db)
        self.interactionInterface.register_db(self.db)

    async def on_connect(self, websocket: WebSocket):
        self.client_id = self.scope.get("path_params", {}).get("client_id", None)
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.log_dir = os.path.join(
            os.path.join(XAgentServerEnv.base_dir, "localstorage", "interact_records"),
            self.date_str,
            self.client_id,
        )
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = Logger(
            log_dir=self.log_dir,
            log_file=f"interact.log",
            log_name=f"{self.client_id}_INTERACT",
        )
        query_string = self.scope.get("query_string", b"").decode()
        parameters = parse_qs(query_string)
        user_id = parameters.get("user_id", [""])[0]
        token = parameters.get("token", [""])[0]
        description = parameters.get("description", [""])[0]
        self.logger.typewriter_log(
            title=f"Receive connection from {self.client_id}: ",
            title_color=Fore.RED,
            content=f"user_id: {user_id}, token: {token}, description: {description}",
        )
        with broadcast_lock:
            await manager.connect(websocket=websocket, websocket_id=self.client_id)
        # await websocket.accept()
        # await websocket_queue.put(websocket)
        self.websocket = websocket
        self.register_db()

        if self.userInterface.user_is_exist(user_id=user_id) == False:
            raise XAgentIOWebSocketConnectError("user is not exist!")
        # auth
        if not self.userInterface.user_is_valid(user_id=user_id, token=token):
            raise XAgentIOWebSocketConnectError("user is not available!")
        # check running, you can edit it by yourself in envs.py to skip this check
        if XAgentServerEnv.check_running:
            if self.interactionInterface.is_running(user_id=user_id):
                raise XAgentIOWebSocketConnectError(
                    "You have a running interaction, please wait for it to finish!"
                )

        base = InteractionBase(
            interaction_id=self.client_id,
            user_id=user_id,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            description=description if description else "XAgent",
            agent="",
            mode="",
            file_list=[],
            recorder_root_dir="",
            status="waiting",
            message="waiting...",
            current_step=uuid.uuid4().hex,
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.interactionInterface.create_interaction(base)
        await websocket.send_text(
            WebsocketResponseBody(
                status="connect",
                success=True,
                message="connect success",
                data=base.to_dict(),
            ).to_text()
        )

    async def on_disconnect(self, websocket, close_code):
        try:
            self.interactionInterface.update_interaction_status(
                interaction_id=self.client_id,
                status="failed",
                message=f"failed, code: {close_code}",
                current_step=uuid.uuid4().hex,
            )
            self.logger.typewriter_log(
                title=f"Disconnect with client {self.client_id}: ", title_color=Fore.RED
            )
            await manager.disconnect(self.client_id, websocket)
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            if self.db:
                self.db.close()

    async def on_receive(self, websocket, data):
        self.logger.typewriter_log(
            title=f"Receive data from {self.client_id}: ",
            title_color=Fore.RED,
            content=data,
        )
        args, agent, mode, file_list = await self.check_receive_data(data)
        # in this step, we need to update interaction to register agent, mode, file_list
        self.interactionInterface.update_interaction(
            {
                "interaction_id": self.client_id,
                "agent": agent,
                "mode": mode,
                "file_list": file_list,
            }
        )
        parameter = InteractionParameter(
            interaction_id=self.client_id,
            parameter_id=uuid.uuid4().hex,
            args=args,
        )
        self.interactionInterface.add_parameter(parameter)
        self.logger.info(
            f"Register parameter: {parameter.to_dict()} into interaction of {self.client_id}, done!"
        )
        await asyncio.create_task(self.do_running_long_task(parameter))

    async def on_send(self, websocket: WebSocket):
        while True:
            await asyncio.sleep(10)
            await websocket.send_text(
                WebsocketResponseBody(
                    status="pong", success=True, message="pong", data={"type": "pong"}
                ).to_text()
            )

    async def check_receive_data(self, data):
        data = json.loads(data)
        args = data.get("args", {})
        agent = data.get("agent", "")
        mode = data.get("mode", "")
        file_list = data.get("file_list", [])

        if not isinstance(args, dict) and args.get("goal", "") == "":
            await self.websocket.send_text(
                WebsocketResponseBody(
                    status="failed", message="args is empty!", data=None
                ).to_text()
            )
            raise XAgentIOWebSocketReceiveError("args is empty!")

        # mode with auto or manual and required
        if mode not in ["auto", "manual"]:
            await self.websocket.send_text(
                WebsocketResponseBody(
                    status="failed",
                    message="mode is not exist! Only auto and manual are allowed!",
                    data=None,
                ).to_text()
            )
            raise XAgentIOWebSocketReceiveError(
                "mode is not exist! Only auto and manual are allowed!"
            )
        return args, agent, mode, file_list

    async def do_running_long_task(self, parameter):
        current_step = uuid.uuid4().hex
        base = self.interactionInterface.get_interaction(interaction_id=self.client_id)
        self.interactionInterface.update_interaction_status(
            interaction_id=base.interaction_id,
            status="running",
            message="running",
            current_step=current_step,
        )

        interaction = XAgentInteraction(
            base=base, parameter=parameter, interrupt=base.mode != "auto"
        )

        io = XAgentIO(
            input=WebSocketInput(
                do_interrupt=base.mode != "auto",
                max_wait_seconds=600,
                websocket=self.websocket,
            ),
            output=WebSocketOutput(websocket=self.websocket),
        )

        interaction.resister_logger(self.logger)
        self.logger.info(
            f"Register logger into interaction of {base.interaction_id}, done!"
        )

        io.set_logger(logger=interaction.logger)
        interaction.resister_io(io)
        self.logger.info(
            f"Register io into interaction of {base.interaction_id}, done!"
        )
        interaction.register_db(self.interactionInterface)
        self.logger.info(
            f"Register db into interaction of {base.interaction_id}, done!"
        )
        # Create XAgentServer
        server = XAgentServer()
        server.set_logger(logger=self.logger)
        self.logger.info(
            f"Register logger into XAgentServer of {base.interaction_id}, done!"
        )
        self.logger.info(
            f"Start a new thread to run interaction of {base.interaction_id}, done!"
        )
        task = asyncio.create_task(server.interact(interaction))
        await task
        with broadcast_lock:
            if manager.is_connected(self.client_id):
                await manager.disconnect(self.client_id, self.websocket)
        interaction.logger.info("done!")


@app.websocket_route("/ws_do_recorder", name="ws_recorder")
class RecorderServer(WebSocketEndpoint):
    encoding: str = "text"
    session_name: str = ""
    count: int = 0
    client_id: str = ""
    websocket: WebSocket = None
    """
    In this websocket, we will receive the recorder_dir from user,
    and you can use it to record the interaction.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db: Session = None
        self.userInterface = userInterface
        self.interactionInterface = interactionInterface

    def register_db(self):
        if connection:
            self.db = connection.db_session
            logger.info("init websocket db session")
        else:
            self.db = None
        self.userInterface.register_db(self.db)
        self.interactionInterface.register_db(self.db)

    async def on_connect(self, websocket: WebSocket):
        self.client_id = uuid.uuid4().hex
        query_string = self.scope.get("query_string", b"").decode()
        parameters = parse_qs(query_string)
        user_id = parameters.get("user_id", [""])[0]
        token = parameters.get("token", [""])[0]
        recorder_dir = parameters.get("recorder_dir", [""])[0]
        description = "XAgent Recorder"
        logger.typewriter_log(
            title=f"Receive connection from {self.client_id}: ",
            title_color=Fore.RED,
            content=f"user_id: {user_id}, token: {token}, recorder_dir: {recorder_dir}",
        )
        with broadcast_lock:
            await manager.connect(websocket=websocket, websocket_id=self.client_id)

        self.websocket = websocket
        self.register_db()
        if self.userInterface.user_is_exist(user_id=user_id) == False:
            raise XAgentIOWebSocketConnectError("user is not exist!")

        if not self.userInterface.user_is_valid(user_id=user_id, token=token):
            raise XAgentIOWebSocketConnectError("user is not available!")

        # check running, you can edit it by yourself in envs.py to skip this check
        if XAgentServerEnv.check_running:
            if self.interactionInterface.is_running(user_id=user_id):
                raise XAgentIOWebSocketConnectError(
                    "You have a running interaction, please wait for it to finish!"
                )

        base = InteractionBase(
            interaction_id=self.client_id,
            user_id=user_id,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            description=description if description else "XAgent",
            agent="",
            mode="",
            file_list=[],
            recorder_root_dir=os.path.join(
                XAgentServerEnv.recorder_root_dir, recorder_dir
            ),
            status="waiting",
            message="waiting...",
            current_step=uuid.uuid4().hex,
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.interactionInterface.create_interaction(base)
        await websocket.send_text(
            WebsocketResponseBody(
                status="connect",
                success=True,
                message="connect success",
                data=base.to_dict(),
            ).to_text()
        )

    async def on_disconnect(self, websocket, close_code):
        try:
            self.interactionInterface.update_interaction_status(
                interaction_id=self.client_id,
                status="failed",
                message=f"failed, code: {close_code}",
                current_step=uuid.uuid4().hex,
            )
            logger.typewriter_log(
                title=f"Disconnect with client {self.client_id}: ", title_color=Fore.RED
            )
            await manager.disconnect(self.client_id, websocket)
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            if self.db:
                self.db.close()

    async def on_receive(self, websocket, data):
        logger.typewriter_log(
            title=f"Receive data from {self.client_id}: ",
            title_color=Fore.RED,
            content=data,
        )

        await asyncio.create_task(self.do_running_long_task(None))

    async def on_send(self, websocket: WebSocket):
        while True:
            await asyncio.sleep(10)
            await websocket.send_text(
                WebsocketResponseBody(
                    status="pong", success=True, message="pong", data={"type": "pong"}
                ).to_text()
            )

    async def do_running_long_task(self, parameter):
        current_step = uuid.uuid4().hex
        base = self.interactionInterface.get_interaction(interaction_id=self.client_id)
        self.interactionInterface.update_interaction_status(
            interaction_id=base.interaction_id,
            status="running",
            message="running",
            current_step=current_step,
        )
        logger.info(f"The interaction is over: {self.client_id}")

        interaction = XAgentInteraction(base=base, parameter=parameter, interrupt=False)

        io = XAgentIO(
            input=WebSocketInput(
                do_interrupt=False, max_wait_seconds=600, websocket=self.websocket
            ),
            output=WebSocketOutput(websocket=self.websocket),
        )

        interaction.resister_logger()
        logger.info(f"Register logger into interaction of {base.interaction_id}, done!")

        io.set_logger(logger=interaction.logger)
        interaction.resister_io(io)
        logger.info(f"Register io into interaction of {base.interaction_id}, done!")
        interaction.register_db(self.interactionInterface)
        logger.info(f"Register db into interaction of {base.interaction_id}, done!")

        server = XAgentServer()
        server.set_logger(logger=interaction.logger)
        logger.info(
            f"Register logger into XAgentServer of {base.interaction_id}, done!"
        )
        logger.info(
            f"Start a new thread to run interaction of {base.interaction_id}, done!"
        )

        await asyncio.to_thread(self.run, server, interaction)
        with broadcast_lock:
            if manager.is_connected(self.client_id):
                await manager.disconnect(self.client_id, self.websocket)
        logger.info("done!")

    def run(self, server: XAgentServer, interaction: XAgentInteraction):
        asyncio.run(server.interact(interaction))


@app.websocket_route("/ws_replay/{client_id}", name="ws_replay")
class ReplayServer(WebSocketEndpoint):
    encoding: str = "text"
    session_name: str = ""
    count: int = 0
    client_id: str = ""
    interaction_id: str = ""
    websocket: WebSocket = None
    """
    In this websocket, we will receive an interaction_id,
    and you can use it to replay the interaction.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db: Session = None
        self.userInterface = userInterface
        self.interactionInterface = interactionInterface

    def register_db(self):
        if connection:
            self.db = connection.db_session
            logger.info("init websocket db session")
        else:
            self.db = None
        self.userInterface.register_db(self.db)
        self.interactionInterface.register_db(self.db)

    async def on_connect(self, websocket: WebSocket):
        self.client_id = uuid.uuid4().hex
        self.interaction_id = self.scope.get("path_params", {}).get("client_id", None)
        query_string = self.scope.get("query_string", b"").decode()

        logger.typewriter_log(
            title=f"Receive connection from {self.client_id}: ", title_color=Fore.RED
        )
        with broadcast_lock:
            await manager.connect(websocket=websocket, websocket_id=self.client_id)

        self.websocket = websocket
        self.register_db()
        interaction = self.interactionInterface.get_interaction(
            interaction_id=self.interaction_id
        )

        if interaction == None:
            await self.websocket.send_text(
                WebsocketResponseBody(
                    success=False, message="interaction is not exist!", data=None
                ).to_text()
            )
            raise Exception("interaction is not exist!")
        await websocket.send_text(
            WebsocketResponseBody(
                status="connect",
                success=True,
                message="connect success",
                data=interaction.to_dict(),
            ).to_text()
        )

    def run_replay(self, interaction):
        asyncio.run(AutoReplayUtil.do_replay(self.websocket, interaction))

    async def on_disconnect(self, websocket, close_code):
        try:
            logger.typewriter_log(
                title=f"Disconnect with client {self.client_id}: ", title_color=Fore.RED
            )
            await manager.disconnect(self.client_id, websocket)
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            if self.db:
                self.db.close()

    async def on_receive(self, websocket, data):
        logger.typewriter_log(
            title=f"Receive data from {self.client_id}: ",
            title_color=Fore.RED,
            content=data,
        )

        interaction = self.interactionInterface.get_interaction(
            interaction_id=self.interaction_id
        )

        await asyncio.to_thread(self.run_replay, interaction)
        await asyncio.sleep(random.randint(3, 10))
        await self.websocket.send_text(
            WebsocketResponseBody(status="finished", data=None).to_text()
        )
        print("finished")
        await self.websocket.close()

    async def on_send(self, websocket: WebSocket):
        pass


@app.websocket_route("/ws_share/{client_id}", name="ws_share")
class SharedServer(WebSocketEndpoint):
    encoding: str = "text"
    session_name: str = ""
    count: int = 0
    client_id: str = ""
    interaction_id: str = ""
    websocket: WebSocket = None
    """
    In this websocket, we will receive an interaction_id,
    and you can use it to replay the interaction.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db: Session = None
        self.userInterface = userInterface
        self.interactionInterface = interactionInterface

    def register_db(self):
        if connection:
            self.db = connection.db_session
            logger.info("init websocket db session")
        else:
            self.db = None
        self.userInterface.register_db(self.db)
        self.interactionInterface.register_db(self.db)

    async def on_connect(self, websocket: WebSocket):
        self.client_id = uuid.uuid4().hex
        self.interaction_id = self.scope.get("path_params", {}).get("client_id", None)
        query_string = self.scope.get("query_string", b"").decode()
        parameters = parse_qs(query_string)
        logger.typewriter_log(
            title=f"Receive connection from {self.client_id}: ", title_color=Fore.RED
        )
        with broadcast_lock:
            await manager.connect(websocket=websocket, websocket_id=self.client_id)

        self.websocket = websocket
        self.register_db()
        interaction = self.interactionInterface.get_shared_interaction(
            interaction_id=self.interaction_id
        )

        if interaction == None:
            await self.websocket.send_text(
                WebsocketResponseBody(
                    success=False, message="interaction is not exist!", data=None
                ).to_text()
            )
            raise Exception("interaction is not exist!")
        await websocket.send_text(
            WebsocketResponseBody(
                status="connect",
                success=True,
                message="connect success",
                data=interaction.to_dict(),
            ).to_text()
        )

    def run_shared(self, interaction):
        asyncio.run(ShareUtil.do_replay(self.websocket, interaction))

    async def on_disconnect(self, websocket, close_code):
        logger.typewriter_log(
            title=f"Disconnect with client {self.client_id}: ", title_color=Fore.RED
        )
        await manager.disconnect(self.client_id, websocket)

    async def on_receive(self, websocket, data):
        logger.typewriter_log(
            title=f"Receive data from {self.client_id}: ",
            title_color=Fore.RED,
            content=data,
        )

        shared = self.interactionInterface.get_shared_interaction(
            interaction_id=self.interaction_id
        )
        await asyncio.to_thread(self.run_shared, shared)
        await asyncio.sleep(random.randint(3, 10))
        await self.websocket.send_text(
            WebsocketResponseBody(status="finished", data=None).to_text()
        )
        print("finished")
        await self.websocket.close()

    async def on_send(self, websocket: WebSocket):
        pass


if __name__ == "__main__":
    uvicorn.run(
        app=XAgentServerEnv.app,
        port=XAgentServerEnv.port,
        reload=XAgentServerEnv.reload,
        workers=XAgentServerEnv.workers,
        host=XAgentServerEnv.host,
    )
