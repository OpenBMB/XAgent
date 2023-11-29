"""XAgent Core Components"""


import abc
from datetime import datetime
import os
import uuid

from colorama import Fore
from XAgent.agent.dispatcher import XAgentDispatcher
from XAgent.agent import PlanGenerateAgent, PlanRefineAgent, ToolAgent, ReflectAgent
from XAgent.utils import TaskSaveItem
from XAgent.vector_db import VectorDBInterface
from XAgent.workflow.base_query import AutoGPTQuery, BaseQuery
from XAgent.workflow.working_memory import WorkingMemoryAgent
from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.interaction import XAgentInteraction

from XAgentServer.loggers.logs import Logger
from XAgent.function_handler import FunctionHandler
from XAgent.toolserver_interface import ToolServerInterface
from XAgent.recorder import RunningRecoder


class XAgentParam(metaclass=abc.ABCMeta):
    """
    XAgent Param
    """

    def __init__(self,
                 config=None,
                 query: BaseQuery = None,
                 newly_created: bool = True) -> None:
        self.config = config
        self.query = query
        self.newly_created = newly_created

    def build_query(self, query: dict):
        """
        build query
        """
        self.query = AutoGPTQuery(**query)

    def build_config(self, config):
        """
        build config
        """
        self.config = config


class XAgentCoreComponents(metaclass=abc.ABCMeta):
    """
    XAgent 核心组件集 / XAgent Core Components
    Components:
        logger: 日志 / logger
        recorder: 运行记录 / running recorder
        toolserver_interface: 工具服务接口 / tool server interface
        function_handler: 功能处理器 / function handler
        working_memory_function: 工作记忆 / working memory
        agent_dispatcher: 代理调度器 / agent dispatcher
        vector_db_interface: 向量数据库接口 / vector db interface
        interaction: 交互 / interaction


    组件集中的所有组件全局唯一 / all components in the component set are globally unique

    """

    global_recorder = None

    def __init__(self) -> None:
        self.interaction = None
        self.logger = None
        self.recorder = None
        self.toolserver_interface = None
        self.function_handler = None
        self.tool_functions_description_list = []
        self.function_list = []
        self.working_memory_function = None
        self.agent_dispatcher = None
        self.vector_db_interface = None
        self.base_dir = ""
        self.extract_dir = ""
        self.available_agents = [
            PlanGenerateAgent,
            PlanRefineAgent,
            ToolAgent,
            ReflectAgent,
        ]

    def register_interaction(self,
                             interaction: XAgentInteraction):
        """
        register an interaction to the core components
        """
        self.interaction = interaction

    def register_logger(self):
        """
        register a logger to the core components
        """
        self.base_dir = os.path.join(
            os.path.join(XAgentServerEnv.base_dir,
                         "localstorage",
                         "interact_records"),
            datetime.now().strftime("%Y-%m-%d"),
            self.interaction.base.interaction_id)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)

        self.extract_dir = os.path.join(self.base_dir, "workspace")
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir, exist_ok=True)
        self.logger = self.interaction.logger

    def resister_recorder(self, param: XAgentParam):
        """
        register a recorder to the core components
        """
        self.recorder = RunningRecoder(
            record_id=self.interaction.base.interaction_id,
            newly_start=param.newly_created,
            root_dir=self.base_dir,
            logger=self.logger
        )
        if param.newly_created:
            self.recorder.regist_query(param.query)
            self.recorder.regist_config(param.config)
        else:
            self.recorder.load_from_db(self.interaction.base.recorder_root_dir)
            self.recorder.regist_query(param.query)
            self.recorder.regist_config(param.config)

        XAgentCoreComponents.global_recorder = self.recorder

    def register_toolserver_interface(self, param: XAgentParam):
        """
        register a tool server interface to the core components
        """
        self.logger.info("register tool server interface")
        self.toolserver_interface = ToolServerInterface(
            self.recorder, logger=self.logger)
        self.logger.info("lazy init tool server interface")
        self.toolserver_interface.lazy_init(config=param.config)
        # to download all files
        self.interaction.register_toolserver_interface(
            self.toolserver_interface)

    def register_function_handler(self, config):
        """
        register a function handler to the core components
        """
        self.logger.info("register function handler")
        self.function_handler = FunctionHandler(
            toolserver_interface=self.toolserver_interface,
            config=config,
            interaction=self.interaction,
            recorder=self.recorder,
            logger=self.logger)

    def register_working_memory_function(self):
        """
        register a working memory agent to the core components
        """
        # working memory function is used for
        # communication between different agents that handle different subtasks
        self.logger.info("register working memory function")
        self.working_memory_agent = WorkingMemoryAgent(logger=self.logger)
        self.working_memory_function = WorkingMemoryAgent.get_working_memory_function()

    def register_agent_dispatcher(self, param: XAgentParam):
        """
        register a agent dispatcher to the core components
        """
        self.logger.info("register agent dispatcher")
        self.agent_dispatcher = XAgentDispatcher(param.config,
                                                 enable=False,
                                                 logger=self.logger)
        for agent in self.available_agents:
            self.agent_dispatcher.regist_agent(agent)

    def register_vector_db_interface(self):
        """
        register a vector db interface to the core components
        """
        # self.vector_db_interface = VectorDBInterface()
        pass

    def register_all(self, param: XAgentParam, interaction: XAgentInteraction):
        """
        register all components to the core components
        """
        self.register_interaction(interaction)
        self.register_logger()
        self.resister_recorder(param)
        self.register_toolserver_interface(param)
        self.register_function_handler(param.config)
        self.register_working_memory_function()
        self.register_agent_dispatcher(param=param)
        self.register_vector_db_interface()

    def build(self, param: XAgentParam, interaction: XAgentInteraction):
        """
        start all components
        """
        self.register_all(param, interaction)
        self.logger.info("build all components, done!")

        subtask_functions, self.tool_functions_description_list = self.function_handler.get_functions(
            param.config)
        self.function_list = subtask_functions + self.working_memory_function

    def start(self):
        """
        start all components
        """
        self.logger.info("start all components")

    def close(self):
        """
        close all components
        """
        self.toolserver_interface.download_all_files()
        self.toolserver_interface.close()

    def print_task_save_items(self,
                              item: TaskSaveItem,
                              ) -> None:

        self.logger.typewriter_log(
            f"Task Name:", Fore.YELLOW, f"{item.name}"
        )
        self.logger.typewriter_log(
            f"Task Goal:", Fore.YELLOW, f"{item.goal}"
        )
        self.logger.typewriter_log(
            f"Task Prior-Criticism:", Fore.YELLOW, f"{item.prior_plan_criticism}"
        )
        if len(item.posterior_plan_reflection) > 0:
            self.logger.typewriter_log(
                f"Task Posterior-Criticism:", Fore.YELLOW
            )
            for line in item.posterior_plan_reflection:
                line = line.lstrip("- ")
                self.logger.typewriter_log("- ", Fore.GREEN, line.strip())
        if len(item.milestones) > 0:
            self.logger.typewriter_log(
                f"Task Milestones:", Fore.YELLOW,
            )
            for line in item.milestones:
                line = line.lstrip("- ")
                self.logger.typewriter_log("- ", Fore.GREEN, line.strip())
        # if len(item.expected_tools) > 0:
        #     logger.typewriter_log(
        #         f"Expected Tools:", Fore.YELLOW,
        #     )
        #     for line in item.expected_tools:
        #         line = f"{line['tool_name']}: {line['reason']}".lstrip("- ")
        #         logger.typewriter_log("- ", Fore.GREEN, line.strip())
        if len(item.tool_reflection) > 0:
            self.logger.typewriter_log(
                f"Posterior Tool Reflections:", Fore.YELLOW,
            )
            for line in item.tool_reflection:
                line = f"{line['target_tool_name']}: {line['reflection']}".lstrip(
                    "- ")
                self.logger.typewriter_log("- ", Fore.GREEN, line.strip())

        self.logger.typewriter_log(
            f"Task Status:", Fore.YELLOW, f"{item.status.name}"
        )
        if item.action_list_summary != "":
            self.logger.typewriter_log(
                f"Action Summary:", Fore.YELLOW, f"{item.action_list_summary}"
            )

    def print_assistant_thoughts(
        self,
        # ai_name: object,
        assistant_reply_json_valid: object,
        speak_mode: bool = False,
    ) -> None:
        assistant_thoughts_reasoning = None
        assistant_thoughts_plan = None
        assistant_thoughts_speak = None
        assistant_thoughts_criticism = None

        assistant_thoughts = assistant_reply_json_valid.get("thoughts", {})
        assistant_thoughts = assistant_thoughts.get("properties", {})
        assistant_thoughts_text = assistant_thoughts.get("thought")
        if assistant_thoughts:
            assistant_thoughts_reasoning = assistant_thoughts.get("reasoning")
            assistant_thoughts_plan = assistant_thoughts.get("plan")
            assistant_thoughts_criticism = assistant_thoughts.get("criticism")
        if assistant_thoughts_text is not None and assistant_thoughts_text != "":
            self.logger.typewriter_log(
                f"THOUGHTS:", Fore.YELLOW, f"{assistant_thoughts_text}"
            )
        if assistant_thoughts_reasoning is not None and assistant_thoughts_reasoning != "":
            self.logger.typewriter_log(
                "REASONING:", Fore.YELLOW, f"{assistant_thoughts_reasoning}")

        if assistant_thoughts_plan is not None and len(assistant_thoughts_plan) > 0:
            self.logger.typewriter_log("PLAN:", Fore.YELLOW, "")
            # If it's a list, join it into a string
            if isinstance(assistant_thoughts_plan, list):
                assistant_thoughts_plan = "\n".join(assistant_thoughts_plan)
            elif isinstance(assistant_thoughts_plan, dict):
                assistant_thoughts_plan = str(assistant_thoughts_plan)

            # Split the input_string using the newline character and dashes
            lines = assistant_thoughts_plan.split("\n")
            for line in lines:
                line = line.lstrip("- ")
                self.logger.typewriter_log("- ", Fore.GREEN, line.strip())

        if assistant_thoughts_criticism is not None and assistant_thoughts_criticism != "":
            self.logger.typewriter_log(
                "CRITICISM:", Fore.YELLOW, f"{assistant_thoughts_criticism}")
        return {
            "thoughts": assistant_thoughts_text,
            "reasoning": assistant_thoughts_reasoning,
            "plan": assistant_thoughts_plan,
            "criticism": assistant_thoughts_criticism,
            "node_id": uuid.uuid4().hex
        }
