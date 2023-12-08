import json
from copy import deepcopy

from colorama import Fore
from XAgent.config import CONFIG
from XAgent.agent.base_agent import BaseAgent
from XAgent.agent.summarize import summarize_action,summarize_plan,clip_text,get_token_nums
from XAgent.data_structure.node import ToolNode
from XAgent.data_structure.tree import TaskSearchTree
from XAgent.inner_loop_search_algorithms.base_search import BaseSearchMethod
from XAgent.logs import logger, print_assistant_thoughts
from XAgent.message_history import Message
from XAgent.tool_call_handle import function_handler, toolserver_interface
from XAgent.utils import SearchMethodStatusCode, ToolCallStatusCode
from XAgent.data_structure.plan import Plan
from XAgent.ai_functions import function_manager
NOW_SUBTASK_PROMPT = '''

'''


def make_message(now_node: ToolNode, task_handler, max_length, config):
    """
    Function to generate messages for each node.

    Args:
        now_node: The current ToolNode instance.
        task_handler: Handler of the tasks.
        max_length: Maximum length of the subtask chain.
        config: The configuration settings.

    Returns:
        The sequence of messages for the current node.

    """
    
    if CONFIG.enable_summary:
        terminal_task_info = summarize_plan(
            task_handler.now_dealing_task.to_json())
    else:
        terminal_task_info = json.dumps(
            task_handler.now_dealing_task.to_json(), indent=2, ensure_ascii=False)

    message_sequence = []

    now_subtask_prompt = f'''Now you will perform the following subtask:\n"""\n{terminal_task_info}\n"""\n'''
    message_sequence.append(Message("user", now_subtask_prompt))
    action_process = now_node.process

    if config.enable_summary:
        action_process = summarize_action(
            action_process, terminal_task_info)
    user_prompt = f"""The following steps have been performed (you have already done the following and the current file contents are shown below):\n
    {action_process}
    """
    message_sequence.append(Message("user", user_prompt))
    return message_sequence


class ReACTChainSearch(BaseSearchMethod):
    """
    Class for ReACT chain search. It performs chain based searches for tasks.
    """
    
    def __init__(self):
        """
        Initializes ReACTChainSearch object. It maintains a list of trees to represent 
        the processed tasks.
        """
        super().__init__()

        self.tree_list = []

    async def run_async(self, config, agent: BaseAgent, task_handler, arguments, functions, task_id, max_try=1, max_answer=1):
        """
        Runs the chain search task.

        Args:
            config: Configuration for the search.
            agent: Base agent responsible for chain search.
            task_handler: Handler of the tasks.
            arguments: Arguments for the current task to be handled.
            functions: The available functions for use by agent.
            task_id: ID of the current task.
            max_try: Maximum number of attempts.
            max_answer: Maximum number of answers to be received

        Returns:
            None
        Raises:
            None
        """
        
        for _attempt_id in range(max_try):
            await self.generate_chain_async(config, agent, task_handler, arguments,functions, task_id)

        if self.status == SearchMethodStatusCode.HAVE_AT_LEAST_ONE_ANSWER:
            self.status = SearchMethodStatusCode.SUCCESS
        else:
            self.status = SearchMethodStatusCode.FAIL

    def get_finish_node(self):
        """
        Function to retrieve the finished node in the task tree.
        
        Returns:
            The finished node.  
        """
        return self.finish_node

    def get_origin_data(self, data):
        """
        Retrieves the initially entered data.

        Args:
            data: The initially entered data list.
        
        Returns:
            The initially entered data as a dictionary.:
        """
        assistant_thoughts_reasoning = None
        assistant_thoughts_plan = None
        assistant_thoughts_speak = None
        assistant_thoughts_criticism = None

        assistant_thoughts = data.get("thoughts", {})
        assistant_thoughts = assistant_thoughts.get("properties", {})
        assistant_thoughts_text = assistant_thoughts.get("thought")
        if assistant_thoughts:
            assistant_thoughts_reasoning = assistant_thoughts.get("reasoning")
            assistant_thoughts_plan = assistant_thoughts.get("plan")
            assistant_thoughts_criticism = assistant_thoughts.get("criticism")

        return {"args": {
            "thoughts": assistant_thoughts_text,
            "reasoning": assistant_thoughts_reasoning,
            "plan": assistant_thoughts_plan,
            "criticism": assistant_thoughts_criticism
        }}

    def rewrite_input_func(self, old, new):
        """
        Checks whether the new inputs are valid and if so updates the old input
        with the new one.

        Args:
            old: The old input entry.
            new: The new input entry to replace the old one.

        Returns:
            The updated input list and the rewrite status.
        """
        if not isinstance(new, dict):
            pass
        if new is None:
            return old, False
        else:
            args = new.get("args", {})
            assistant_thoughts_reasoning = None
            assistant_thoughts_plan = None
            assistant_thoughts_speak = None
            assistant_thoughts_criticism = None

            assistant_thoughts = old.get("thoughts", {})
            assistant_thoughts = assistant_thoughts.get("properties", {})
            assistant_thoughts_text = assistant_thoughts.get("thought")
            if assistant_thoughts:
                assistant_thoughts_reasoning = assistant_thoughts.get(
                    "reasoning")
                assistant_thoughts_plan = assistant_thoughts.get("plan")
                assistant_thoughts_criticism = assistant_thoughts.get(
                    "criticism")

                if "thoughts" in args.keys() and "thought" in assistant_thoughts.keys():
                    old["thoughts"]["properties"]["thought"] = args.get(
                        "thoughts", assistant_thoughts_text)
                if "reasoning" in args.keys() and "reasoning" in assistant_thoughts.keys():
                    old["thoughts"]["properties"]["reasoning"] = args.get(
                        "reasoning", assistant_thoughts_reasoning)
                if "plan" in args.keys() and "plan" in assistant_thoughts.keys():
                    old["thoughts"]["properties"]["plan"] = args.get(
                        "plan", assistant_thoughts_plan)
                if "criticism" in args.keys() and "criticism" in assistant_thoughts.keys():
                    old["thoughts"]["properties"]["criticism"] = args.get(
                        "criticism", assistant_thoughts_criticism)

            return old, True

    async def generate_chain_async(self, config, agent: BaseAgent, task_handler, arguments,functions, task_id):
        """
        Run the chain search task.

        Args:
            config: Configuration for the search.
            agent: Base agent responsible for chain search.
            task_handler: Handler of the tasks.
            arguments: Arguments for the current task to be handled.
            functions: The available functions for use by agent.
            task_id: ID of the current task.

        Returns:
            None.
        Raises:
            None.
        """
        
        self.tree_list.append(TaskSearchTree())
        now_attempt_tree = self.tree_list[-1]
        now_node = now_attempt_tree.root

        while now_node.get_depth() < config.max_subtask_chain_length:
            logger.typewriter_log(
                "-=-=-=-=-=-=-= THOUGHTS, REASONING, PLAN AND CRITICISM WILL NOW BE VERIFIED BY AGENT -=-=-=-=-=-=-=",
                Fore.GREEN,
                "",
            )
            if now_node.father != None:
                if task_handler.interaction.interrupt:
                    can_modify = self.get_origin_data(now_node.data)
                    receive_data = await task_handler.interaction.auto_receive(can_modify)
                    data, rewrite_flag = self.rewrite_input_func(
                        now_node.data, receive_data)
                    now_node.data = data
                    if rewrite_flag:
                        logger.typewriter_log(
                            "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                            Fore.GREEN,
                            "",
                        )
                        print_assistant_thoughts(now_node.data, False)
                        logger.typewriter_log(
                            "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                            Fore.GREEN,
                            "",
                        )

            message_sequence = make_message(now_node=now_node,
                                            task_handler=task_handler,
                                            max_length=config.max_subtask_chain_length,
                                            config=config)
            
            function_call = None
            if now_node.get_depth() == config.max_subtask_chain_length - 1:
                function_call = {"name": "subtask_submit"}

            file_archi, _, = toolserver_interface.execute_command_client(
                "FileSystemEnv_print_filesys_struture",{"return_root":True})
            file_archi,length = clip_text(file_archi,1000,clip_end=True)
                
            human_prompt = ""
            if config.enable_ask_human_for_help:
                human_prompt = "- Use 'ask_human_for_help' when you need help, remember to be specific to your requirement to help user to understand your problem."
            else:
                human_prompt = "- Human is not available for help. You are not allowed to ask human for help in any form or channel. Solve the problem by yourself. If information is not enough, try your best to use default value."

            all_plan = task_handler.plan_agent.latest_plan.to_json()
            if config.enable_summary:
                all_plan = summarize_plan(all_plan)
            else:
                all_plan = json.dumps(all_plan, indent=2, ensure_ascii=False)
            
            new_message, tokens = agent.parse(
                placeholders={
                    "system": {
                        "all_plan": all_plan
                    },
                    "user": {
                        "workspace_files":file_archi,
                        "subtask_id": task_handler.now_dealing_task.get_subtask_id(to_str=True),
                        "max_length": config.max_subtask_chain_length,
                        "step_num": str(now_node.get_depth()+1),
                        "human_help_prompt": human_prompt,
                    }
                },
                arguments=arguments,
                functions=functions,
                function_call=function_call,
                additional_messages=message_sequence,
                additional_insert_index=-1
            )
            new_tree_node = agent.message_to_tool_node(new_message)

            print_data = print_assistant_thoughts(
                new_tree_node.data, False
            )

            tool_output, tool_output_status_code, need_for_plan_refine, using_tools = function_handler.handle_tool_call(
                new_tree_node, task_handler)
            self.need_for_plan_refine = need_for_plan_refine

            now_attempt_tree.make_father_relation(now_node, new_tree_node)

            await task_handler.interaction.update_cache(update_data={**print_data, "using_tools": using_tools}, status="inner", current=task_id)

            now_node = new_tree_node

            if tool_output_status_code == ToolCallStatusCode.SUBMIT_AS_SUCCESS:

                self.status = SearchMethodStatusCode.HAVE_AT_LEAST_ONE_ANSWER
                break
            elif tool_output_status_code == ToolCallStatusCode.SUBMIT_AS_FAILED:
                break

        self.finish_node = now_node  
        
    def to_json(self):
        """
        Placeholder function to convert ReACTChainSearch object to JSON.

        Currently not implemented.
        
        Returns:
            None
        """
        pass