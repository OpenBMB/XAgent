import json

from colorama import Fore
from XAgent.config import CONFIG
from XAgent.agent.base_agent import BaseAgent
from XAgent.agent.summarize import summarize_action, summarize_plan, clip_text
from XAgent.core import XAgentCoreComponents
from XAgent.data_structure.node import ToolNode
from XAgent.data_structure.tree import TaskSearchTree
from XAgent.inner_loop_search_algorithms.base_search import BaseSearchMethod
from XAgent.message_history import Message
from XAgent.utils import SearchMethodStatusCode, ToolCallStatusCode
NOW_SUBTASK_PROMPT = '''

'''


def make_message(now_node: ToolNode, max_length, config, now_dealing_task):
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
            now_dealing_task.to_json())
    else:
        terminal_task_info = json.dumps(
            now_dealing_task.to_json(), indent=2, ensure_ascii=False)

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

    def __init__(self, xagent_core_components: XAgentCoreComponents):
        """
        xagent_core_components: XAgentCoreComponents object, used to initialize ReACTChainSearch object
        Initializes ReACTChainSearch object. It maintains a list of trees to represent 
        the processed tasks.
        """
        super().__init__()

        self.tree_list = []

        self.finish_node = None

        self.xagent_core_components = xagent_core_components

    def run(self,
            config,
            agent: BaseAgent,
            arguments,
            functions,
            task_id,
            now_dealing_task,
            plan_agent,
            max_try=1,
            max_answer=1):
        """
        Runs the chain search task.

        Args:
            config: Configuration for the search.
            agent: Base agent responsible for chain search.
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
            self.generate_chain(config, agent, arguments,
                                functions, task_id, now_dealing_task, plan_agent)

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

    def generate_chain(self, config, agent: BaseAgent, arguments, functions, task_id, now_dealing_task, plan_agent):
        """
        Run the chain search task.

        Args:
            config: Configuration for the search.
            agent: Base agent responsible for chain search.
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
            self.xagent_core_components.logger.typewriter_log(
                "-=-=-=-=-=-=-= THOUGHTS, REASONING, PLAN AND CRITICISM WILL NOW BE VERIFIED BY AGENT -=-=-=-=-=-=-=",
                Fore.GREEN,
                "",
            )
            if now_node.father != None:
                if self.xagent_core_components.interaction.interrupt:
                    can_modify = self.get_origin_data(now_node.data)
                    receive_data = self.xagent_core_components.interaction.receive(
                        can_modify)
                    data, rewrite_flag = self.rewrite_input_func(
                        now_node.data, receive_data)
                    now_node.data = data
                    if rewrite_flag:
                        self.xagent_core_components.logger.typewriter_log(
                            "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                            Fore.GREEN,
                            "",
                        )
                        self.xagent_core_components.print_assistant_thoughts(now_node.data, False)
                        self.xagent_core_components.logger.typewriter_log(
                            "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                            Fore.GREEN,
                            "",
                        )

            message_sequence = make_message(now_node=now_node,
                                            max_length=config.max_subtask_chain_length,
                                            config=config,
                                            now_dealing_task=now_dealing_task)

            function_call = None
            if now_node.get_depth() == config.max_subtask_chain_length - 1:
                function_call = {"name": "subtask_submit"}

            file_archi, _, = self.xagent_core_components.toolserver_interface.execute_command_client(
                "FileSystemEnv_print_filesys_struture", {"return_root": True})
            file_archi, length = clip_text(file_archi, 1000, clip_end=True)

            human_prompt = ""
            if config.enable_ask_human_for_help:
                human_prompt = "- Use 'ask_human_for_help' when you need help, remember to be specific to your requirement to help user to understand your problem."
            else:
                human_prompt = "- Human is not available for help. You are not allowed to ask human for help in any form or channel. Solve the problem by yourself. If information is not enough, try your best to use default value."

            all_plan = plan_agent.latest_plan.to_json()
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
                        "workspace_files": file_archi,
                        "subtask_id": now_dealing_task.get_subtask_id(to_str=True),
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

            print_data = self.xagent_core_components.print_assistant_thoughts(
                new_tree_node.data, False
            )

            tool_output, tool_output_status_code, need_for_plan_refine, using_tools = self.xagent_core_components.function_handler.handle_tool_call(
                new_tree_node)
            self.need_for_plan_refine = need_for_plan_refine
            now_attempt_tree.make_father_relation(now_node, new_tree_node)
            self.xagent_core_components.interaction.insert_data(
                data={**print_data, "using_tools": using_tools}, status="inner", current=task_id, is_include_pictures=self.is_include_pictures(using_tools))

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

    def is_include_pictures(self, using_tools):
        """判断是否包含png
        """
        tool_name = using_tools.get("tool_name", "") if isinstance(
            using_tools, dict) else ""
        tool_output = using_tools.get(
            "tool_output", {}) if isinstance(using_tools, dict) else ""
        if tool_name == "PythonNotebook_execute_cell":
            for output in tool_output:
                if isinstance(output, dict) and 'file_name' in output:
                    return True
        return False
