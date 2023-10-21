
from colorama import Fore, Style
from typing import List, Dict

from XAgent.logs import logger, print_task_save_items
from XAgent.ai_functions import function_manager

class WorkingMemoryAgent():
    def __init__(self):
        self.subtask_handle_mapping = {}
        self.execute_process: List[Dict] = []
    
    @classmethod
    def get_working_memory_function(cls):
        chat_with_subtask_function = function_manager.get_function_schema('chat_with_other_subtask')
        return [chat_with_subtask_function]


    def register_task(self, terminal_plan):
        subtask_id = terminal_plan.get_subtask_id(to_str=True)
        finish_node = terminal_plan.process_node

        datapoint = {
            "plan": terminal_plan,
            "task_id": subtask_id,
            "qa_sequence": [],
        }

        self.execute_process.append(datapoint)
        self.subtask_handle_mapping[subtask_id] = datapoint 

        logger.typewriter_log(
            "Working Memory: ",
            Fore.YELLOW,
            f"{Fore.YELLOW}Register a new subtask={Style.RESET_ALL}{subtask_id} {Fore.YELLOW}Process length={Style.RESET_ALL}{finish_node.get_depth()}."
        )
        print_task_save_items(terminal_plan.data)

    def handle(self, tool_name, tool_input):
        assert tool_name == "chat_with_other_subtask"
        logger.log("handle chat with other subtask")


working_memory_agent = WorkingMemoryAgent()