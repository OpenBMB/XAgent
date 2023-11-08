import abc
import json
import os
import uuid
from datetime import datetime

from XAgentIO.BaseIO import XAgentIO
from XAgentServer.database import InteractionBaseInterface
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.loggers.logs import Logger
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.subtask import Subtask
from XAgentServer.models.ws import XAgentOutputData


class XAgentInteraction(metaclass=abc.ABCMeta):
    """
    A class to represent a XAgent interaction.

    This class provides methods to manage and control the interaction.

    Attributes:
        base (InteractionBase): The interaction base 
        parameter (InteractionParameter): The parameters of the interaction
        interrupt (bool): To indicate whether the interaction can be interrupted or not
    """

    def __init__(
        self,
        base: InteractionBase,
        parameter: InteractionParameter,
        interrupt: bool = False,
    ) -> None:
        """
        The constructor for the XAgentInteraction class.

        Args:
            base (InteractionBase): The interaction base
            parameter (InteractionParameter): The parameters of the interaction
            interrupt (bool): To indicate whether the interaction can be interrupted or not
        """
        self.base = base
        self.parameter = parameter
        self._cache : XAgentOutputData = None
        
        self.current_step = uuid.uuid4().hex
        self.logger = None
        self.interrupt = interrupt
        self.log_dir = os.path.join(os.path.join(XAgentServerEnv.base_dir, "localstorage",
                                        "interact_records"), datetime.now().strftime("%Y-%m-%d"), self.base.interaction_id)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def to_dict(self) -> dict:
        """
        Convert the parameter to a python dict.

        Returns:
            dict: Dictionary representation of the parameter
        """
        return self.parameter.to_dict()

    def to_json(self) -> str:
        """
        Convert the parameter to a JSON string.

        Returns:
            str: JSON string representation of the parameter
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def resister_logger(self, logger: Logger):
        """
        Register a logger to the interaction.

        Args:
            logger (Logger): The logger to be registered
        """
        self.logger = logger
        self.logger.info(f"init interaction: {self.base.interaction_id}")

    def resister_io(self, io: XAgentIO):
        """
        Register an I/O agent to the interaction.

        Args:
            io (XAgentIO): The I/O agent to be registered
        """
        self.io = io

    def register_db(self, db: InteractionBaseInterface):
        """
        Register a database interface to the interaction.

        Args:
            db (InteractionBaseInterface): The database interface to be registered
        """
        self.db = db

    def register_recorder_root_dir(self, recorder_root_dir):
        """
        Register a root directory for the recorder.

        Args:
            recorder_root_dir (str): Path to the root directory
        """
        self.recorder_root_dir = recorder_root_dir

    def init_cache(self, data: XAgentOutputData):
        """
        Initialize cache with given data.

        Args:
            data (XAgentOutputData): The data to populate the cache with
        """
        self._cache = data
        self.logger.info(f"init cache")

    def get_cache(self) -> dict:
        """
        Get the current cache data.

        Returns:
            dict: Data from the cache
        """
        return self._cache.to_dict() if self.data_cache is not None else {}

    def save_cache(self):
        """
        Save the current cache data to a JSON file.
        """
        with open(os.path.join(self.log_dir, "cache.json"), "w", encoding="utf-8") as f:
            json.dump(self._cache.to_dict(), f, indent=2, ensure_ascii=False)

    async def update_cache(self,
                           update_data: dict,
                           status="",
                           current: str = None):
        """
        Update the cache data.

        Args:
            update_data (dict): The update data
            status (str): The current status of the interaction
            current (str): The current subtask or refinement task id 

        Raises:
            ValueError: If status is not in ['start', 'subtask', 'refinement', 'inner', 'finished', 'failed']
            ValueError: If current is not provided when status is 'subtask' or 'refinement' or 'inner'
            ValueError: If the update_data is not a list when status is 'subtask'
            ValueError: If the update_data is not a dict when status is 'refinement' or 'inner'
            ValueError: If a subtask with current id doesn't exist when status is 'inner'
        """
        
        if status not in ["start", "subtask", "refinement", "inner", "finished", "failed"]:
            raise ValueError(
                "status must be in ['start', 'subtask', 'refinement', 'inner', 'finished', 'failed']")
        
        
        self.current_step = uuid.uuid4().hex
        # self.logger.typewriter_log(
            # f"CURRENT: {self.current_step}", f"update cache, status {status}, current {current}, update_data: {update_data}")
        if status == "inner":
            tool_name = update_data.get("using_tools", {}).get("tool_name", "") if isinstance(update_data, dict) else ""
            
            if tool_name == "subtask_submit":
                status = "subtask_submit"

        push_data = {
            "status": status,
            "current": current,
            "random_seed": self.current_step,
            "data": update_data
        }
        if status == "start":
            
            for k, v in update_data.items():
                if k == "subtasks":
                    update_data['subtasks'] = [
                        Subtask(**subtask) for subtask in v]

            self._cache.update(update_data)

            push_data = {
                "status": status,
                "random_seed": self.current_step,
                "data": {k: v if k != "subtasks" else [l.to_dict() for l in v] for k, v in update_data.items()}
            }
            self.db.update_interaction_status(self.base.interaction_id, status="running", message="running", current_step=self.current_step)

        if status == "subtask":
            
            if current is None:
                raise ValueError(
                    "current must be a task_id while status is subtask")
            if not isinstance(update_data, list):
                raise ValueError(
                    "update_data must be a list while status is subtask")
            new_subtask_list = []
            for subtask in self._cache.subtasks:
                if current == subtask.task_id:
                    break
                new_subtask_list.append(subtask)

            new_subtask_list.extend([Subtask(**subtask)
                                    for subtask in update_data])
            self._cache.subtasks = new_subtask_list
            push_data = {
                "status": status,
                "current": current,
                "data": update_data,
                "random_seed": self.current_step,
            }
            self.db.update_interaction_status(
                self.base.interaction_id, status="running", message="running", current_step=self.current_step)
        
        if status == "refinement":
            
            if current is None:
                raise ValueError(
                    "current must be a task_id while status is refinement")
            if not isinstance(update_data, dict):
                raise ValueError(
                    "update_data must be a dict while status is refinement")
            sub_task = None
            for subtask in self._cache.subtasks:
                if current == subtask.task_id:
                    
                    subtask.refinement = update_data
                    sub_task = subtask.to_dict()
                    break
            push_data = {
                "status": status,
                "node_id": sub_task.get("node_id", ""),
                "task_id": sub_task.get("task_id", ""),
                "name": sub_task.get("name", ""),
                "args": sub_task.get("args", ""),
                "current": current,
                "data": update_data,
                "random_seed": self.current_step,
            }
            self.db.update_interaction_status(
                self.base.interaction_id, status="running", message="running", current_step=self.current_step)

        
        if status == "inner":
            
            if current is None:
                raise ValueError(
                    "current must be a task_id while status is inner")
            if not isinstance(update_data, dict):
                raise ValueError(
                    "update_data must be a dict while status is inner")
            sub_task = None
            for subtask in self._cache.subtasks:
                if current == subtask.task_id:
                    
                    subtask.inner.append(update_data)
                    sub_task = subtask.to_dict()
                    break
            if not sub_task:
                raise ValueError(
                    f"subtask {current} not found while status is inner from {self._cache.subtasks}")
            
            push_data = {
                "status": status,
                "node_id": sub_task.get("node_id", ""),
                "task_id": sub_task.get("task_id", ""),
                "name": sub_task.get("name", ""),
                "args": sub_task.get("args", ""),
                "current": current,
                "data": update_data,
                "random_seed": self.current_step,
            }
            self.db.update_interaction_status(
                self.base.interaction_id, status="running", message="running", current_step=self.current_step)

        
        self.save_cache()

        await self.auto_send(push_data=push_data)
        if status == "finished":
            await self.auto_close()


    async def auto_send(self, push_data):
        """
        Automatically send the push_data.

        Args:
            push_data (dict): The data to be sent

        Raises:
            Exception: If there was an error while sending the data
        """

        # self.logger.info(f"send data: {push_data}")
        await self.io.Output.run(push_data)

    async def auto_receive(self, can_modify=None):
        """
        Receiving data automatically.

        Args:
            can_modify (list): list of keys that can be modified in the interaction

        Returns:
            dict: The received data
        """
        data = await self.io.Input.run(can_modify)
        self.db.add_parameter(InteractionParameter(
            parameter_id=uuid.uuid4().hex,
            interaction_id=self.base.interaction_id,
            args=data.get("args", {}),
        ))
        return data

    async def auto_close(self):
        """
        Automatically close the interaction.
        """
        # self.io.close()
        self.logger.info(f"close io connection")
        self.db.update_interaction_status(self.base.interaction_id, status="finished",
                                   message="io connection closed", current_step=self.current_step)
