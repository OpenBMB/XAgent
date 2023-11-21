"""XAgent Interaction Class"""
import abc
from abc import ABCMeta
import os
import uuid
import time
from datetime import datetime
import zipfile
from colorama import Fore

from sqlalchemy.orm import Session
from XAgent.toolserver_interface import ToolServerInterface

from XAgentServer.loggers.logs import Logger
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.enums.status import StatusEnum
from XAgentServer.models.raw import XAgentRaw

from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.application.cruds.interaction import InteractionCRUD
from XAgentServer.exts.exception_ext import XAgentTimeoutError

from XAgentServer.application.global_val import redis


class XAgentInteraction(metaclass=abc.ABCMeta):
    """
    XAgent 核心交互组件集, 引用: XAgentCE
    Attributes:
        base: 交互基本信息
        parameter: 交互参数
        interrupt: 是否包含中断
        toolserver: 工具服务
        call_method: 调用方式
        wait_seconds: 等待时间
        
    Components:
        logger: 日志
        db: 数据库
        recorder: 运行记录
        toolserver_interface: 工具服务接口
        
    组件集中的所有组件全局唯一

    """

    def __init__(
        self,
        base: InteractionBase,
        parameter: InteractionParameter,
        interrupt: bool = False,
        call_method: str = "web",
        wait_seconds: int = 600,
    ) -> None:
        self.base = base
        self.parameter = parameter
        # 唯一标识当前的执行步骤
        self.current_step = uuid.uuid4().hex
        self.logger = None
        self.interrupt = interrupt
        self.call_method = call_method
        self.wait_seconds = wait_seconds
        self.log_dir = os.path.join(
            os.path.join(XAgentServerEnv.base_dir,
                         "localstorage",
                         "interact_records"),
            datetime.now().strftime("%Y-%m-%d"),
            self.base.interaction_id)
        self.human_data = None
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.extract_dir = os.path.join(self.log_dir, "workspace")
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

        self.db: Session = None
        self.toolserver_interface = None

    def register_toolserver_interface(self, toolserver_interface: ToolServerInterface):
        """register tool server interface"""
        self.toolserver_interface = toolserver_interface

    def resister_logger(self, logger: Logger):
        """
        注册logger, 根据会话id创建日志文件夹, 并创建日志文件
        """

        self.logger = logger
        self.logger.info(f"init interaction: {self.base.interaction_id}")

    def register_db(self, db: Session):
        """
        注册db

        Args:
            db: Session对象
        """
        self.db = db

    def insert_data(self,
                    data: dict,
                    status="",
                    current: str = None,
                    is_include_pictures: bool = False,):
        """
        更新缓存, 推送数据
        """
        # check alive
        alive = redis.get_key(self.base.interaction_id)
        if alive == "close":
            self.logger.info("The user terminated this action and exited.")
            exit(0)
        self.current_step = uuid.uuid4().hex

        if status == "inner":
            tool_name = data.get("using_tools", {}).get(
                "tool_name", "") if isinstance(data, dict) else ""

            if tool_name == "subtask_submit":
                status = StatusEnum.SUBMIT

        # download workspace files
        self.download_files()

        file_list = os.listdir(self.extract_dir)

        # insert raw
        process = XAgentRaw(
            node_id=self.current_step,
            interaction_id=self.base.interaction_id,
            current=current,
            step=0,
            data=data,
            file_list=file_list,
            status=status,
            do_interrupt=self.interrupt,
            wait_seconds=0,
            ask_for_human_help=False,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_deleted=False,
            is_human=False,
            human_data=None,
            human_file_list=[],
            is_send=self.call_method != 'web',
            is_receive=False,
            include_pictures=is_include_pictures,
        )
        if status == StatusEnum.FINISHED:
            InteractionCRUD.update_interaction_status(
                db=self.db,
                interaction_id=self.base.interaction_id,
                status=StatusEnum.FINISHED,
                message="finished",
                current_step=self.current_step)
        else:
            InteractionCRUD.update_interaction_status(
                db=self.db,
                interaction_id=self.base.interaction_id,
                status="running",
                message="running",
                current_step=self.current_step)
        InteractionCRUD.insert_raw(db=self.db, process=process)
        if self.call_method == "web":
            redis.set_key(self.base.interaction_id + "_send", 1)
        elif self.call_method == "cmd":
            # print workspace file list
            file_list_str = ", ".join(file_list) 
            self.logger.typewriter_log(
                title=f"-=-=-=-=-=-=-= {self.base.interaction_id}, {self.current_step}, WORKSPACE FILE LIST -=-=-=-=-=-=-=\n",
                title_color=Fore.GREEN,
                content=f"[{file_list_str}] in {self.extract_dir}"
            )

    def download_files(self):
        """download files

        Returns:
            Boolean: True or False
        """
        try:
            save_path = self.toolserver_interface.download_all_files()

            if os.path.exists(save_path):
                zip_file = zipfile.ZipFile(save_path)
                zip_list = zip_file.namelist()  # 得到压缩包里所有文件
                for f in zip_list:
                    zip_file.extract(f, self.extract_dir)  # 循环解压文件到指定目录

                zip_file.close()
            return True
        except zipfile.BadZipFile:
            return False

    def receive(self, can_modify=None):
        """
        接收数据
        """

        if self.call_method == "web":
            wait = 0
            while wait < self.wait_seconds:
                human_data = self.get_human_data()
                if human_data is not None:
                    return human_data
                else:
                    wait += 2
                    time.sleep(2)

            raise XAgentTimeoutError("等待数据超时，关闭连接")
        else:
            print(can_modify)

    def get_human_data(self):
        """
        获取人类数据
        """
        # check alive, ensure the interaction is alive
        # if The user terminated this action and exited
        alive = redis.get_key(self.base.interaction_id)
        if alive == "close":
            self.logger.info("The user terminated this action and exited!")
            exit(0)
        receive_key = self.base.interaction_id + "_" + self.current_step + "_receive"
        is_receive = redis.get_key(receive_key)

        if is_receive:
            raw = InteractionCRUD.get_raw(
                db=self.db, interaction_id=self.base.interaction_id, node_id=self.current_step)

            if raw and raw.is_human and raw.is_receive:
                redis.delete_key(receive_key)
                return raw.human_data

        return None

    def ask_for_human_help(self, data):
        """调用工具时，请求人类帮助
        Execute the tool and ask for human help
        """

        self.current_step = uuid.uuid4().hex
        self.download_files()
        file_list = os.listdir(self.extract_dir)
        # special: ask for human help and do interrupt
        # send data
        process = XAgentRaw(
            node_id=self.current_step,
            interaction_id=self.base.interaction_id,
            current=self.current_step,
            step=0,
            data=data,
            file_list=file_list,
            status=StatusEnum.ASK_FOR_HUMAN_HELP,
            do_interrupt=True,
            wait_seconds=0,
            ask_for_human_help=True,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_deleted=False,
            is_human=False,
            human_data=None,
            human_file_list=[],
            is_send=False,
            is_receive=False,
            include_pictures=False,
        )

        # insert into mysql
        InteractionCRUD.insert_raw(db=self.db, process=process)

        # set redis
        redis.set_key(self.base.interaction_id + "_send", 1)

        # set status

        InteractionCRUD.update_interaction_status(
            db=self.db,
            interaction_id=self.base.interaction_id,
            status=StatusEnum.ASK_FOR_HUMAN_HELP,
            message="ask for human help",
            current_step=self.current_step)

        # check alive
        alive = redis.get_key(self.base.interaction_id)
        if alive == "close":
            self.logger.info("The user terminated this action and exited!")
            exit(0)

        # wait for human data
        wait = 0
        while wait < self.wait_seconds:
            human_data = self.get_human_data()
            if human_data is not None:
                return human_data
            else:
                wait += 2
                time.sleep(2)

        raise XAgentTimeoutError("ASK-For-Human-Data: 等待数据超时，关闭连接")
    
