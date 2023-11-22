"""router user"""
import smtplib
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Query
from sqlalchemy.orm import Session

from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.application.cruds.user import UserCRUD
from XAgentServer.application.dependence import get_db
from XAgentServer.application.schemas.response_body import ResponseBody
from XAgentServer.exts.mail_ext import email_content

router = APIRouter(prefix="/user",
                   tags=["user"],
                   responses={404: {"description": "Not found"}})


@router.post("/register")
async def register(email: str = Form(...),
                   name: str = Form(...),
                   corporation: str = Form(...),
                   position: str = Form(...),
                   industry: str = Form(...),
                   db: Session = Depends(get_db)) -> ResponseBody:
    """
    register user
    """
    if UserCRUD.is_exist(db=db, email=email):
        return ResponseBody(success=False, message="user is already exist")

    token = uuid.uuid4().hex
    user = {"user_id": uuid.uuid4().hex, "email": email, "name": name,
            "token": token, "available": False, "corporation": corporation,
            "position": position, "industry": industry,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_beta": False}
    try:

        contents = email_content(user)

        if XAgentServerEnv.Email.send_email:
            from XAgentServer.application.global_val import yag
            yag.send(user["email"], 'XAgent Token Verification', contents)
        else:
            user["available"] = True
        UserCRUD.add_user(db=db, user_dict=user)
    except smtplib.SMTPAuthenticationError:
        return ResponseBody(success=False, message="email send failed!", data=None)

    except Exception:
        return ResponseBody(success=False, message="register failed", data=None)

    return ResponseBody(data=user, success=True, message="Register success, we will send a email to you!")


@router.get("/auth")
async def auth(user_id: str = Query(...),
               token: str = Query(...),
               db: Session = Depends(get_db)
               ) -> ResponseBody:
    """
    user auth
    """
    user = UserCRUD.get_user(db=db, user_id=user_id)
    if user is None:
        return ResponseBody(success=False, message="user is not exist")

    if user.token != token:
        return ResponseBody(success=False, message="token is not correct")
    expired_time = datetime.now() - datetime.strptime(
        user.update_time, "%Y-%m-%d %H:%M:%S")
    if expired_time.seconds > 60 * 60 * 24 * 7:
        return ResponseBody(success=False, message="token is expired")
    if not user.available:

        user.available = True
        user.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        UserCRUD.update_user(db=db, user=user)
    else:
        return ResponseBody(success=False, message="user is already available!")

    return ResponseBody(data=user.to_dict(), success=True, message="auth success")


@router.post("/login")
async def login(email: str = Form(...),
                token: str = Form(...),
                db: Session = Depends(get_db)) -> ResponseBody:
    """
    login
    """
    user = UserCRUD.get_user(db=db, email=email)
    if user is None:
        return ResponseBody(success=False, message="user is not exist")

    if user.token != token:
        return ResponseBody(success=False, message="token is not correct")
    if not user.available:
        return ResponseBody(success=False, message="user is not available")

    return ResponseBody(data=user.to_dict(), success=True, message="login success")


@router.post("/check")
async def check(token: str = Form(...), db: Session = Depends(get_db)) -> ResponseBody:
    """
    check token is effective
    """
    if token is None:
        return ResponseBody(success=False, message="token is none")

    result = UserCRUD.token_is_exist(db=db, token=token, user_id=None)

    if result:
        return ResponseBody(data=result, success=True, message="token is effective")

    return ResponseBody(data=result, success=True, message="token is invalid")
