"""XAgent Server Application
"""
import json
import os
import re
import shutil

from colorama import Fore

from XAgent.workflow.task_handler import TaskHandler
from XAgentServer.interaction import XAgentInteraction
from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.loggers.logs import Logger
from XAgentServer.exts.exception_ext import (
    XAgentRunningError,
    XAgentUploadFileError)
from XAgent.core import XAgentCoreComponents, XAgentParam


class XAgentServer:
    """XAgent Server Start Class
    """

    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger

    def interact(self, interaction: XAgentInteraction):
        # query = message
        """
        XAgent Server Start Function
        """
        from XAgent.config import CONFIG as config
        xagent_core = None
        try:
            config.reload()
            args = {}
            # args
            args = interaction.parameter.args

            self.logger.info(
                f"server is running, the start query is {args.get('goal', '')}")
            xagent_param = XAgentParam()

            # build query
            xagent_param.build_query({
                "role_name": "Assistant",
                "task": args.get("goal", ""),
                "plan": args.get("plan", ["Pay attention to the language in initial goal, always answer with the same language of the initial goal given."]),
            })
            xagent_param.build_config(config)
            xagent_core = XAgentCoreComponents()
            # build XAgent Core Components
            xagent_core.build(xagent_param, interaction=interaction)
            json_str = json.dumps(
                xagent_param.config.to_dict(), indent=2)
            json_str=re.sub(r'"api_key": "(.+?)"', r'"api_key": "**"', json_str)
            self.logger.info(json_str)
            self.logger.typewriter_log(
                "Human-In-The-Loop",
                Fore.RED,
                str(xagent_param.config.enable_ask_human_for_help),
            )

            file_list = interaction.base.file_list
            for file in file_list:
                file_uuid = file.get("uuid", "")
                file_name = file.get("name", "")
                if file_uuid.startswith("/"):
                    file_path = file_uuid
                else:
                    file_path = os.path.join(XAgentServerEnv.Upload.upload_dir,
                                         interaction.base.user_id, file_uuid)

                upload_dir = os.path.join(
                    xagent_core.base_dir, "upload")
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                # 拷贝到workspace
                if interaction.call_method == "web":
                    shutil.copy(file_path, os.path.join(upload_dir, file_name))
                else:
                    if os.path.exists(file_path):
                        if os.path.samefile(file_path, os.path.join(upload_dir, file_name)):
                            # 文件路径相同,跳过复制
                            pass
                        else:
                            shutil.copy(file_path, os.path.join(upload_dir, file_name))
                        # shutil.copy(file_path, os.path.join(upload_dir, file_name))

                new_file = os.path.join(upload_dir, file_name)
                try:
                    xagent_core.toolserver_interface.upload_file(new_file)
                except Exception as e:
                    self.logger.typewriter_log(
                        "Error happens when uploading file",
                        Fore.RED,
                        f"{new_file}\n{e}",
                    )
                    raise XAgentUploadFileError(str(e)) from e

            task_handler = TaskHandler(xagent_core=xagent_core,
                                       xagent_param=xagent_param)
            self.logger.info("Start outer loop async")
            task_handler.outer_loop()
        except Exception as e:
            raise XAgentRunningError(str(e)) from e
        finally:
            if xagent_core is not None:
                xagent_core.close()
