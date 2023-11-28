import abc
import os
import time
import base64
import uuid
import json5 as json
import requests

from typing import List
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor

from XAgent.data_structure.node import ToolNode
from XAgent.toolserver_interface import ToolServerInterface
from XAgent.utils import ToolCallStatusCode
from XAgent.ai_functions import function_manager
from XAgent.recorder import RunningRecoder
from XAgentServer.interaction import XAgentInteraction


class FunctionHandler():
    """
    The handler for functions.
    """

    def __init__(self,
                 toolserver_interface: ToolServerInterface,
                 config,
                 interaction: XAgentInteraction,
                 recorder: RunningRecoder,
                 logger=None):
        self.logger = logger
        self.toolserver_interface = toolserver_interface
        self.config = config
        self.interaction = interaction
        self.recorder = recorder
        self.subtask_submit_function = function_manager.get_function_schema(
            'subtask_submit')

        # TODO: support more complex versions of human help, like collaborative debugging.
        self.ask_human_for_help_function = function_manager.get_function_schema(
            'ask_human_for_help')
        self.human_interruption_function = function_manager.get_function_schema(
            'human_interruption')

        self.avaliable_tools_description_list = []

    def log_task_submit(self, arguments):
        """
        Log the task submission.

        Args:
            arguments: The arguments of the task submission.
        """
        self.logger.typewriter_log(
            f"-=-=-=-=-=-=-= SUBTASK SUBMITTED -=-=-=-=-=-=-=",
            Fore.YELLOW,
            "",
        )
        self.logger.typewriter_log(
            f"submit_type:", Fore.YELLOW, f"{arguments['submit_type']}"
        )
        self.logger.typewriter_log(
            f"success:", Fore.YELLOW, f"{arguments['result']['success']}"
        )
        self.logger.typewriter_log(
            f"conclusion:", Fore.YELLOW, f"{arguments['result']['conclusion']}"
        )
        if "milestones" in arguments["result"].keys():
            self.logger.typewriter_log(
                f"milestones:", Fore.YELLOW
            )
            for milestone in arguments["result"]["milestones"]:
                line = milestone.lstrip("- ")
                self.logger.typewriter_log("- ", Fore.GREEN, line.strip())
        self.logger.typewriter_log(
            f"need_for_plan_refine:", Fore.YELLOW, f"{arguments['suggestions_for_latter_subtasks_plan']['need_for_plan_refine']}"
        )
        self.logger.typewriter_log(
            f"plan_suggestions:", Fore.YELLOW, f"{arguments['suggestions_for_latter_subtasks_plan']['reason']}"
        )

    def change_subtask_handle_function_enum(self, function_name_list: List[str]):
        """
        Change the subtask handling function enumeration.

        Args:
            function_name_list: The list of function names.
        """
        match self.config.default_request_type:
            case 'openai':
                self.subtask_handle_function = function_manager.get_function_schema(
                    'subtask_handle')
                self.subtask_handle_function["parameters"]["properties"]["tool_call"][
                    "properties"]["tool_name"]["enum"] = function_name_list
            case 'xagent':
                pass
            case _:
                raise NotImplementedError(
                    f"Request type {self.config.default_request_type} not implemented")

    def intrinsic_tools(self, enable_ask_human_for_help):
        """
        Get the intrinsic tools.

        Args:
            enable_ask_human_for_help: Whether to enable the ask_human_for_help function.

        Returns:
            The intrinsic tools.
        """
        tools = [self.subtask_submit_function,]
        if enable_ask_human_for_help:
            tools.append(self.ask_human_for_help_function)
        tools.extend(self.avaliable_tools_description_list)
        return tools

    def get_functions(self, config):
        """
        Get the functions.

        Args:
            config: The configuration for the functions.

        Returns:
            The intrinsic tools and the description of the tools.
        """
        output = self.toolserver_interface.get_available_tools()

        available_tools: list = output['available_tools']
        openai_function_jsons: dict = output['tools_json']

        black_list = set(config.tool_blacklist)
        for item in black_list:
            try:
                available_tools.remove(item)
            except ValueError:
                pass
        openai_function_jsons = [
            openai_function_json for openai_function_json in openai_function_jsons if openai_function_json['name'] not in black_list]

        self.tool_names = available_tools
        self.change_subtask_handle_function_enum(available_tools)
        self.avaliable_tools_description_list = openai_function_jsons
        for tool_json in openai_function_jsons:
            function_manager.register_function(tool_json)
        return self.intrinsic_tools(config.enable_ask_human_for_help), self.avaliable_tools_description_list

    def long_result_summary(self, command: dict, result):
        """
        Summarize the long result.

        Args:
            command (dict): The command.
            result: The result.

        Returns:
            The summarized result.
        """
        if command['name'] == 'WebEnv_browse_website':
            if not isinstance(result, str):
                result = str(result)
            result = function_manager(
                'parse_web_text', webpage=result[:8096], prompt=command['arguments']['goals_to_browse'])
            result['useful_hyperlinks'] = result['useful_hyperlinks'][:3]
        if command['name'] == 'WebEnv_search_and_browse':
            with ThreadPoolExecutor(max_workers=len(result)) as pool:
                f = []
                for ret in result:
                    f.append(pool.submit(function_manager, 'parse_web_text',
                             webpage=ret['page'][:8096], prompt=command['arguments']['goals_to_browse']))
                for ret, thd in zip(result, f):
                    ret['page'] = thd.result()
                    ret['page']['useful_hyperlinks'] = ret['page']['useful_hyperlinks'][:3]

        if isinstance(result, str) and len(result) > 2000:
            # need to summarize
            pass
        return result

    def handle_tool_call(self, node: ToolNode):
        """
        Handle the tool call.

        Args:
            node (ToolNode): The tool node.

        Returns:
            The result, tool output status code, whether to refine the plan, and the tools used.
        """
        plan_refine = False
        command_name = node.data["command"]["properties"]["name"]
        arguments = node.data["command"]["properties"]["args"]

        self.logger.typewriter_log(
            "NEXT ACTION: ",
            Fore.CYAN,
            f"COMMAND: {Fore.CYAN}{command_name}{Style.RESET_ALL}  \n"
            f"ARGUMENTS: \n{Fore.CYAN}{arguments}{Style.RESET_ALL}",
        )

        if command_name == "subtask_submit":
            plan_refine, tool_output_status_code, command_result, = self.handle_subtask_submit(
                arguments)
        elif command_name == "ask_human_for_help":
            plan_refine, tool_output_status_code, command_result, = self.handle_human_help(
                arguments)
        elif command_name == "human_interruption":
            assert False, "Never call this function"
        elif command_name == '' or command_name is None:
            command_result = ''
            tool_output_status_code = ToolCallStatusCode.TOOL_CALL_SUCCESS
        else:
            command_result, tool_output_status_code, = self.toolserver_interface.execute_command_client(
                command_name,
                arguments,
                # input_hash_id,
            )
            # retry to get the result
            MAX_RETRY = 10
            retry_time = 0
            while retry_time < MAX_RETRY and tool_output_status_code == ToolCallStatusCode.TIMEOUT_ERROR and isinstance(command_result['detail'], dict) and 'type' in command_result['detail'] and command_result['detail']['type'] == 'retry':
                time.sleep(3)
                retry_time += 1
                command_result, tool_output_status_code, = self.toolserver_interface.execute_command_client(
                    command_result['detail']['next_calling'],
                    command_result['detail']['arguments'],
                )

            if tool_output_status_code == ToolCallStatusCode.TIMEOUT_ERROR and retry_time == MAX_RETRY:
                command_result = "Timeout and no content returned! Please check the content you submit!"

        if tool_output_status_code == ToolCallStatusCode.TOOL_CALL_SUCCESS:
            command_result = self.long_result_summary(
                {'name': command_name, 'arguments': arguments}, command_result)

        result = f"Command {command_name} returned: " + f"{command_result}"

        node.data["tool_output"] = command_result
        node.data["tool_status_code"] = tool_output_status_code

        # node.workspace_hash_id = output_hash_id
        if result is not None:
            node.history.add("system", result, "action_result")
            self.logger.typewriter_log("SYSTEM: ", Fore.YELLOW, result)
        else:
            node.history.add(
                "system", "Unable to execute command", "action_result")
            self.logger.typewriter_log(
                "SYSTEM: ", Fore.YELLOW, "Unable to execute command"
            )

        if tool_output_status_code == ToolCallStatusCode.TOOL_CALL_SUCCESS:
            color = Fore.GREEN
        elif tool_output_status_code == ToolCallStatusCode.SUBMIT_AS_SUCCESS:
            color = Fore.YELLOW
        elif tool_output_status_code == ToolCallStatusCode.SUBMIT_AS_FAILED:
            color = Fore.BLUE
        else:
            color = Fore.RED

        self.logger.typewriter_log(
            "TOOL STATUS CODE: ", Fore.YELLOW, f"{color}{tool_output_status_code.name}{Style.RESET_ALL}"
        )

        self.recorder.regist_tool_call(
            tool_name=command_name,
            tool_input=arguments,
            tool_output=command_result,
            tool_status_code=tool_output_status_code.name,
            thought_data={
                "thought": node.data["thoughts"], "content": node.data["content"]},
        )

        using_tools = {
            "tool_name": command_name,
            "tool_input": arguments,
            "tool_output": command_result,
            "tool_status_code": tool_output_status_code.name,
            "thought_data": {"thought": node.data["thoughts"], "content": node.data["content"]}
        }

        if tool_output_status_code in [ToolCallStatusCode.SUBMIT_AS_SUCCESS, ToolCallStatusCode.SUBMIT_AS_FAILED]:
            self.log_task_submit(arguments)

        return result, tool_output_status_code, plan_refine, using_tools

    def handle_subtask_submit(self, arguments):
        """
        Handle the subtask submission.

        Args:
            arguments: The arguments of the subtask submission.

        Returns:
            bool: Whether to refine the plan.
            The tool output status code.
            The result.
        """
        plan_refine = False
        if arguments["result"]["success"]:
            tool_output_status_code = ToolCallStatusCode.SUBMIT_AS_SUCCESS
        else:
            tool_output_status_code = ToolCallStatusCode.SUBMIT_AS_FAILED
        if arguments["suggestions_for_latter_subtasks_plan"]["need_for_plan_refine"]:
            plan_refine = True
        answer = {
            "content": f"you have successfully submit the subtask as {arguments['submit_type']}"
        }
        command_result = json.dumps(answer, ensure_ascii=False)

        return plan_refine, tool_output_status_code, command_result

    def handle_human_help(self, arguments):
        """
        Handle the ask for human help.

        Args:
            arguments: The arguments for asking human help.

        Returns:
            bool: Whether to refine the plan.
            The tool output status code.
            The result.
        """
        self.logger.typewriter_log(
            "ASK For Human Help",
            Fore.RED,
            "You must give some suggestions, please type in your feedback and then press 'Enter' to send and continue the loop"
        )
        url = "ask_human"
        payload = arguments
        tool_cache = self.recorder.query_tool_server_cache(
            url=url, payload=payload)
        if tool_cache != None:
            command_result = tool_cache["tool_output"]
            status_code = tool_cache["response_status_code"]
        else:
            prompt = "ASK For Human Help: \n You must give some suggestions, \
                  please type in your feedback and then press 'Enter' \
                  to send and continue the loop."
            human_suggestion = self.interaction.ask_for_human_help(
                prompt)
            command_result = json.dumps(
                {"output": f"{human_suggestion}"}, ensure_ascii=False)
            status_code = "human has no status :)"
        self.recorder.regist_tool_server(
            url=url,
            payload=payload,
            tool_output=command_result,
            response_status_code=status_code,
        )

        plan_refine = False
        return plan_refine, ToolCallStatusCode.TOOL_CALL_SUCCESS, command_result
