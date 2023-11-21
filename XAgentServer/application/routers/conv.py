"""conv module."""

from datetime import datetime
import time
import json
import os
from typing import List
import uuid
import zipfile

from fastapi import APIRouter, Depends, File, Form, UploadFile
import requests
from sqlalchemy.orm import Session
from XAgentServer.application.core.envs import XAgentServerEnv

from XAgentServer.application.cruds.interaction import InteractionCRUD
from XAgentServer.application.cruds.user import UserCRUD
from XAgentServer.application.dependence import get_db
from XAgentServer.application.schemas.response_body import ResponseBody
from XAgentServer.enums.status import StatusEnum
from XAgentServer.exts.exception_ext import XAgentAuthError, XAgentWebError
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.raw import XAgentRaw
from XAgentServer.models.shared_interaction import SharedInteractionBase

router = APIRouter(prefix="/conv",
                   tags=["conv"],
                   responses={404: {"description": "Not found"}})


def user_is_available(
        user_id: str = Form(...),
        token: str = Form(...),
        db: Session = Depends(get_db)):
    """
    check user is available    
    """
    if user_id == "":
        raise XAgentAuthError("user_id is empty!")
    if not UserCRUD.is_exist(db=db, user_id=user_id):
        raise XAgentAuthError("user is not exist!")
    if not UserCRUD.user_is_valid(db=db, user_id=user_id, token=token):
        raise XAgentAuthError("user is not available!")
    return user_id


@router.post("/getUserInteractions")
async def get_all_interactions(user_id: str = Depends(user_is_available),
                               page_size: int = Form(...),
                               page_num: int = Form(...),
                               db: Session = Depends(get_db)) -> ResponseBody:
    """
    get all interactions by user_id
    """

    data = InteractionCRUD.search_interaction_by_user_id(db=db,
                                                         user_id=user_id,
                                                         page_size=page_size,
                                                         page_num=page_num)
    return ResponseBody(data=data, success=True, message="success")


@router.post("/init_conv_env")
def init_conv_env(user_id: str = Depends(user_is_available),
                  db: Session = Depends(get_db)):
    """
    initialize conv env
    """

    interaction = InteractionCRUD.get_ready_interaction(db=db, user_id=user_id)

    if interaction is None:
        interaction_id = uuid.uuid4().hex
        base = InteractionBase(interaction_id=interaction_id,
                               user_id=user_id,
                               create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                               description="XAgent",
                               agent="",
                               mode="",
                               file_list=[],
                               recorder_root_dir="",
                               status="ready",
                               message="ready...",
                               current_step="-1",
                               update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                               )
        InteractionCRUD.create_interaction(db=db, base=base)
    else:
        interaction_id = interaction.interaction_id

    return ResponseBody(data={"id": interaction_id,
                              "t": str(int(datetime.now().timestamp() * 1000))}, success=True, message="success")


@router.post("/getSharedInteractions")
async def get_share_interactions(user_id: str = Depends(user_is_available),
                                 page_size: int = Form(...),
                                 page_num: int = Form(...),
                                 db: Session = Depends(get_db)) -> ResponseBody:
    """
    get all interactions by user id
    """

    data = InteractionCRUD.search_many_shared(
        db=db, page_size=page_size, page_index=page_num)
    return ResponseBody(data=data, success=True, message="success")


@router.post("/shareInteraction")
async def share_interaction(user_id: str = Depends(user_is_available),
                            interaction_id: str = Form(...),
                            db: Session = Depends(get_db)) -> ResponseBody:
    """
    update_interaction_description
    """
    interaction = InteractionCRUD.get_interaction(db=db,
                                                  interaction_id=interaction_id)
    if interaction is None:
        return ResponseBody(success=False,
                            message=f"Don't find any interaction by interaction_id: \
                                {interaction_id}, Please check your interaction_id!")

    finish_status = InteractionCRUD.get_finish_status(
        db=db, interaction_id=interaction_id)
    if not finish_status:
        return ResponseBody(success=False, message="interaction is not finish!")
    user = UserCRUD.get_user(db=db, user_id=user_id)
    user_name = user.name
    interaction_dir = os.path.join(XAgentServerEnv.base_dir,
                                   "localstorage",
                                   "interact_records",
                                   interaction.create_time[:10],
                                   interaction_id)
    workspace_dir = os.path.join(interaction_dir, "workspace")
    zip_file = os.path.join(interaction_dir, "workspace.zip")
    if not os.path.exists(zip_file):
        if os.path.exists(workspace_dir):
            files = os.listdir(workspace_dir)
            # zip workspace
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as z:
                for f in files:
                    file = os.path.join(workspace_dir, f)
                    z.write(file, arcname=f)

    raws = InteractionCRUD.search_many_raws(
        db=db, interaction_id=interaction_id)

    share_data = {
        "user_id": user_id,
        "user_name": user_name,
        "token": user.token,
        "interaction": json.dumps(interaction.to_dict(), ensure_ascii=False),
        "raws": json.dumps([raw.to_dict() for raw in raws], ensure_ascii=False),
    }

    with open(zip_file, 'rb') as f:
        files = {"files": f.read()}
    try:
        res = requests.post(url=XAgentServerEnv.share_url,
                            data=share_data,
                            files=files,
                            timeout=60)

        data = res.json()

        return ResponseBody(**data)
    except Exception as e:
        return ResponseBody(success=False, message=str(e), data=None)


@router.post("/community")
def community(user_id: str = Depends(user_is_available),
              user_name: str = Form(...),
              interaction: str = Form(...),
              raws: str = Form(...),
              files: UploadFile = File(...),
              db: Session = Depends(get_db)):
    """
    community, this api is runing on x-agent.net
    """
    interaction = json.loads(interaction)
    raws = json.loads(raws)
    interaction_id = interaction["interaction_id"]
    old_share = InteractionCRUD.get_shared_interaction(
        db=db, interaction_id=interaction_id)

    # 如果已经分享过了，就不再分享了
    if old_share:
        raise XAgentWebError("interaction is exist!")

    contain_finish = False
    for raw in raws:
        if raw["status"] == StatusEnum.FINISHED:
            contain_finish = True
            break
    # 如果没有finish的节点，就不分享了
    if not contain_finish:
        raise XAgentWebError("interaction is not finish!")

    interaction_dir = os.path.join(XAgentServerEnv.base_dir,
                                   "localstorage",
                                   "interact_records",
                                   interaction["create_time"][:10],
                                   interaction_id,
                                   "workspace")

    if not os.path.exists(interaction_dir):
        os.makedirs(interaction_dir)

    # 先暂存文件
    with open(os.path.join(interaction_dir, "workspace.zip"), "wb") as f:
        f.write(files.file.read())

    # 解压文件
    with zipfile.ZipFile(file=os.path.join(interaction_dir, "workspace.zip"), mode="r") as zip_file:
        zip_list = zip_file.namelist()  # 得到压缩包里所有文件
        for f in zip_list:
            zip_file.extract(f, interaction_dir)  # 循环解压文件到指定目录

    # 删除压缩包
    os.remove(os.path.join(interaction_dir, "workspace.zip"))

    base = InteractionBase(**interaction)

    share = SharedInteractionBase(
        interaction_id=interaction_id,
        user_name=user_name,
        create_time=interaction["create_time"],
        update_time=interaction["update_time"],
        description=interaction["description"],
        agent=interaction["agent"],
        mode=interaction["mode"],
        is_deleted=False,
        star=0,
        is_audit=False
    )

    InteractionCRUD.create_interaction(db=db, base=base)

    InteractionCRUD.add_share(db=db, share=share)

    for raw in raws:
        old_raw = InteractionCRUD.get_raw(db=db,
                                          interaction_id=interaction_id,
                                          node_id=raw["node_id"])
        if old_raw is None:
            xraw = XAgentRaw(**raw)
            InteractionCRUD.insert_raw(db=db, process=xraw)

    return ResponseBody(data=None, success=True, message="success")


@router.post("/deleteInteraction")
async def delete_interaction(user_id: str = Depends(user_is_available),
                             interaction_id: str = Form(...),
                             db: Session = Depends(get_db)) -> ResponseBody:
    """
    delete
    """

    data = InteractionCRUD.delete_interaction(db=db,
                                              interaction_id=interaction_id)

    return ResponseBody(data=data, success=True, message="success")


@router.post("/updateInteractionConfig")
async def update_interaction_parameter(user_id: str = Depends(user_is_available),
                                       mode: str = Form(...),
                                       agent: str = Form(...),
                                       file_list: List[str] = Form(...),
                                       interaction_id: str = Form(...),
                                       db: Session = Depends(get_db)
                                       ) -> ResponseBody:
    """
    update parameter

    """
    if interaction_id == "":
        return ResponseBody(success=False, message="interaction_id is empty!")
    interaction = InteractionCRUD.get_interaction(db=db,
                                                  interaction_id=interaction_id)
    if interaction is None:
        return ResponseBody(success=False, message=f"Don't find any interaction by interaction_id:\
            {interaction_id}, Please check your interaction_id!")
    update_data = {
        "interaction_id": interaction_id,
        "agent": agent,
        "mode": mode,
        "file_list": [json.loads(l) for l in file_list],
    }
    InteractionCRUD.update_interaction(db=db, base_data=update_data)
    return ResponseBody(data=update_data, success=True, message="success!")


@router.post("/updateInteractionDescription")
async def update_interaction_description(user_id: str = Depends(user_is_available),
                                         description: str = Form(...),
                                         interaction_id: str = Form(...),
                                         db: Session = Depends(get_db)
                                         ) -> ResponseBody:
    """
    update description

    """
    if interaction_id == "":
        return ResponseBody(success=False, message="interaction_id is empty!")
    interaction = InteractionCRUD.get_interaction(db=db,
                                                  interaction_id=interaction_id)
    if interaction is None:
        return ResponseBody(success=False, message=f"Don't find any interaction by interaction_id:\
            {interaction_id}, Please check your interaction_id!")
    update_data = {
        "interaction_id": interaction_id,
        "description": description if description else "XAgent",
    }
    InteractionCRUD.update_interaction(db=db, base_data=update_data)
    return ResponseBody(data=update_data, success=True, message="success!")
