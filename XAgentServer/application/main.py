"""Start up file of XAgent Server"""
import traceback
import uvicorn
from colorama import Fore
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.application.dependence import (enable_dependence,
                                                 enable_logger)
from XAgentServer.exts.exception_ext import XAgentAuthError, XAgentDBError, XAgentError, XAgentFileError

app = FastAPI()

logger = enable_logger()

# 中间件
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """
    Exception middleware
    """
    # 默认响应
    message = "Internal server error"
    response = Response(message, status_code=500)
    try:
        response = await call_next(request)
    except XAgentDBError as error:
        traceback.print_exc()
        message = "XAgent DB Error." if XAgentServerEnv.prod else error.message
        response = JSONResponse(
            status_code=500,
            content={"status": "failed", "message": message}
        )
    except XAgentFileError as error:
        traceback.print_exc()
        message = "XAgent File Error." if XAgentServerEnv.prod else error.message
        response = JSONResponse(
            status_code=500,
            content={"status": "failed", "message": message}
        )
    except XAgentAuthError as error:
        traceback.print_exc()
        response = JSONResponse(
            status_code=401,
            content={"status": "failed", "message": error.message}
        )
    except XAgentError as error:
        traceback.print_exc()
        message = "XAgent Error." if XAgentServerEnv.prod else error.message
   
        response = JSONResponse(
            status_code=500,
            content={"status": "failed", "message": message}
        )

    return response


async def print_start_message():
    """
    print start message
    """
    logger.typewriter_log(
        title="XAgent Server Dependences:",
        title_color=Fore.RED,
        content="""
        Python: 3.10+ 
        FastAPI: Http server
        Websocket: long connect with client
        MySQL: save xagent data
        SqlAlchemy: ORM with MySQL
        Redis: save status of interaction
        Threading: run interaction
        APScheduler: send data to client and keep alive
        FastAPI APIRouter: manage websocket route
        XAgentError: XAgentServer.exts.exception_ext""",
        )
    logger.typewriter_log(
        title="XAgent Server Version:",
        title_color=Fore.RED,
        content="""
        V 1.1.0""",
        )
    logger.typewriter_log(
        title="Notes:",
        title_color=Fore.RED,
        content="""
        Since V 1.1.0, 
        Local storage will no longer be supported, replaced by Mysql.
        The service depends on Redis and Mysql, 
        so you need to install Redis and Mysql before using it.
        Before you use this service, please ensure that the following services are available:
            1. Redis on docker, port: 6379, you can start it by docker, default password: xagent
            2. Mysql on docker, port: 3306, you can start it by docker
            3. XAgent Tool Server is runnning on port 8080
            4. Port 8090 is not occupied
        """,
        )


async def startup_event():
    """start up event
    """
    logger.info("XAgent Service Startup Param:")
    for key, item in XAgentServerEnv.__dict__.items():
        if not key.startswith("__"):
            logger.info(f"{' '*10}{key}: {item}")
    enable_dependence(logger)


@app.on_event("startup")
async def startup():
    """
    start up event
    """
    await startup_event()
    if XAgentServerEnv.default_login:
        logger.typewriter_log(
            title="Default user: Guest, token: xagent, you can use it to login",
            title_color=Fore.RED)
    await print_start_message()


@app.on_event("shutdown")
async def shutdown():
    """
    shut down event
    """
    print("XAgent Service Shutdown!")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """handle validation exception

    Args:
        request (Request): _description_
        exc (RequestValidationError): _description_

    Returns:
        _type_: _description_
    """
    return JSONResponse(
        status_code=400,
        content={"status": "failed", "message": exc.errors()}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from XAgentServer.application.routers import conv, user, workspace
from XAgentServer.application.websockets import base, recorder, replayer, share

app.include_router(user.router)
app.include_router(conv.router)
app.include_router(workspace.router)
app.include_router(base.router)
app.include_router(recorder.router)
app.include_router(replayer.router)
app.include_router(share.router)


if __name__ == "__main__":

    uvicorn.run(app=XAgentServerEnv.app,
                port=XAgentServerEnv.port,
                reload=XAgentServerEnv.reload,
                workers=XAgentServerEnv.workers,
                host=XAgentServerEnv.host)
