"""workspace module."""

import base64
import json
import os
from typing import List
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from XAgentServer.application.core.envs import XAgentServerEnv

from XAgentServer.application.cruds.interaction import InteractionCRUD
from XAgentServer.application.cruds.user import UserCRUD
from XAgentServer.application.dependence import get_db
from XAgentServer.application.schemas.response_body import ResponseBody

router = APIRouter(prefix="/workspace",
                   tags=["workspace"],
                   responses={404: {"description": "Not found"}})


def user_is_available(
        user_id: str = Form(...),
        token: str = Form(...),
        db: Session = Depends(get_db)):
    """
    check user is available    
    """
    if user_id == "":
        raise HTTPException(status_code=401, detail="user_id is empty!")
    if not UserCRUD.is_exist(db=db, user_id=user_id):
        raise HTTPException(status_code=401, detail="user is not exist!")
    if not UserCRUD.user_is_valid(db=db, user_id=user_id, token=token):
        raise HTTPException(
            status_code=401, detail="user is not available!")
    return user_id


@router.post("/upload")
async def create_upload_files(files: List[UploadFile] = File(...),
                              user_id: str = Depends(user_is_available)) -> ResponseBody:
    """Upload Files"""

    if len(files) == 0:
        return ResponseBody(success=False, message="files is empty!")
    if len(files) > 5:
        files = files[:5]

    if not os.path.exists(os.path.join(XAgentServerEnv.Upload.upload_dir, user_id)):
        os.makedirs(os.path.join(XAgentServerEnv.Upload.upload_dir, user_id))

    for f in files:
        if f.size > 1024 * 1024 * 1:
            return ResponseBody(success=False,
                                message="file size is too large, limit is 1MB for each file!")

    file_list = []
    for file in files:
        file_name = uuid.uuid4().hex + os.path.splitext(file.filename)[-1]
        with open(os.path.join(XAgentServerEnv.Upload.upload_dir, user_id, file_name), "wb") as f:
            f.write(await file.read())
            file_list.append({"uuid": file_name, "name": file.filename})
    return ResponseBody(data={"user_id": user_id,
                              "file_list": file_list},
                        success=True, message="upload success")


@router.post("/file")
async def file(user_id: str = Depends(user_is_available),
               interaction_id: str = Form(...),
               db: Session = Depends(get_db),
               file_name: str = Form(...)):
    """
    get download file
    """
    interaction = InteractionCRUD.get_interaction(db=db, interaction_id=interaction_id)

    if interaction is None:
        return ResponseBody(success=False, message="interaction is not exist!")

    time_str = interaction.create_time[:10]

    file_path = os.path.join(
        XAgentServerEnv.base_dir,
        "localstorage/interact_records",
        time_str,
        interaction_id,
        "workspace")
    if not os.path.exists(file_path):
        return ResponseBody(success=False,
                            message="file is not exist!")

    file_suffix = file_name.split(".")[-1]
    if file_suffix in ["jpg", "png",
                       "jpeg", "gif", "bmp"]:
        with open(os.path.join(file_path, file_name), "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return ResponseBody(
            data=f"data:image/{file_suffix};base64,{data}",
            success=True,
            message="get file success!"
        )

    if file_suffix in ["mp4", "avi", "mkv",
                       "rmvb", "rm", "flv", "3gp", "wmv"]:
        return FileResponse(os.path.join(file_path, file_name),
                            media_type="video/" + file_suffix)

    if file_suffix in ["mp3", "wav", "wma",
                       "ogg", "aac", "flac", "ape"]:
        return FileResponse(os.path.join(file_path, file_name),
                            media_type="audio/" + file_suffix)

    if file_suffix in ["pdf", "doc", "docx",
                       "xls", "xlsx", "ppt", "pptx"]:
        return FileResponse(os.path.join(file_path, file_name),
                            media_type="application/" + file_suffix)

    if file_suffix in ["json"]:
        with open(os.path.join(file_path, file_name), 'r', encoding="utf-8") as f:
            data = json.load(f)

        return ResponseBody(data=json.dumps(data,
                                            ensure_ascii=False,
                                            indent=4),
                            success=True,
                            message="get file success!")

    if file_suffix in ["ipynb"]:
        return FileResponse(os.path.join(file_path, file_name),
                            media_type="application/" + file_suffix)
    
    
    with open(os.path.join(file_path, file_name), 'r', encoding="utf-8") as f:
        data = f.read()

    return ResponseBody(data=data, success=True, message="get file success!")
