from colorama import Fore, Style
from typing import List, Dict

from XAgent.ai_functions import function_manager

class WorkingMemoryAgent():
    """
    A class used to represent an agent's working memory.

    Attributes:
        subtask_handle_mapping (dict): A dictionary to store the mapping of subtasks.
        execute_process (list): A list to store the processes to be executed.

    """
    def __init__(self, logger=None):
        """
        The constructor for the WorkingMemoryAgent class.

        Args:
            logger (object): The logger object.
        """
        self.logger = logger
        self.subtask_handle_mapping = {}
        self.execute_process: List[Dict] = []

    @classmethod
    def get_working_memory_function(cls):
        """
        The method to get the 'chat_with_other_subtask' function schema from the function manager.

        Returns:
            list: A list that contains the function schema of 'chat_with_other_subtask'.

        """
        chat_with_subtask_function = function_manager.get_function_schema('chat_with_other_subtask')
        return [chat_with_subtask_function]

    def register_task(self, terminal_plan):
        """
        The method to register a task i.e., to add the terminal plan of the task to the execution process,
        and to map the subtask id with the terminal plan in subtask_handle_mapping

        Args:
            terminal_plan (object): The terminal plan of the task.

        """
        subtask_id = terminal_plan.get_subtask_id(to_str=True)
        finish_node = terminal_plan.process_node

        datapoint = {
            "plan": terminal_plan,
            "task_id": subtask_id,
            "qa_sequence": [],
        }

        self.execute_process.append(datapoint)
        self.subtask_handle_mapping[subtask_id] = datapoint

        self.logger.typewriter_log(
            "Working Memory: ",
            Fore.YELLOW,
            f"{Fore.YELLOW}Register a new subtask={Style.RESET_ALL}{subtask_id} {Fore.YELLOW}Process length={Style.RESET_ALL}{finish_node.get_depth()}."
        )

    def handle(self, tool_name, tool_input):
        """
        The method to handle the tool named 'chat_with_other_subtask'

        Args:
            tool_name (str): The name of the tool.
            tool_input (str): The input for the tool.

        Raises:
            AssertionError: If tool name is not 'chat_with_other_subtask'.

        """
        assert tool_name == "chat_with_other_subtask"
        self.logger.log("handle chat with other subtask")