import abc
import os
import requests
import json5
import openai
from typing import List
from colorama import Fore
from typing import overload
from copy import deepcopy


from XAgent.data_structure.node import ToolNode
from XAgent.utils import LLMStatusCode, RequiredAbilities
from XAgent.message_history import Message
from XAgent.agent.utils import get_command, _chat_completion_request
from XAgent.logs import logger
from XAgent.ai_functions import function_manager
from XAgent.ai_functions.request import load_args_with_schema_validation

class BaseAgent(metaclass=abc.ABCMeta):
    abilities = set([
        RequiredAbilities.plan_generation,
        RequiredAbilities.plan_refinement,
        RequiredAbilities.task_evaluator,
        RequiredAbilities.tool_tree_search,
        RequiredAbilities.reflection,
        RequiredAbilities.summarization,
    ])

    def __init__(self, config, prompt_messages: List[Message] = None):
        # self.abilities = {}
        # for key in RequiredAbilities:
        #     self.abilities[key] = True
        logger.typewriter_log(
            f"Constructing an Agent:",
            Fore.YELLOW,
            self.__class__.__name__,
        )
        self.config = config
        self.prompt_messages = prompt_messages
        self.usage = {

        }


    @abc.abstractmethod
    def parse(self,**args) -> (LLMStatusCode, Message, dict):
        pass

    def message_to_tool_node(self,message) -> ToolNode:
        new_node = ToolNode()
        # print(message)
        if "content" in message.keys():
            print(message["content"])
            new_node.data["content"] = message["content"]
        
        if "function_call" in message.keys():
            function_schema = function_manager.get_function_schema(message["function_call"]["name"])
            if function_schema is not None:
                function_input = load_args_with_schema_validation(function_schema,message["function_call"]["arguments"])
            else:
                function_input = json5.loads(message["function_call"]["arguments"])
                
            if message["function_call"]["name"] == "subtask_handle":
                if 'tool_input' in function_input["tool_call"]:
                    function_schema = function_manager.get_function_schema(function_input["tool_call"]["tool_name"])
                    if function_schema is not None:
                        function_input["tool_call"]["tool_input"] = load_args_with_schema_validation(function_schema,function_input["tool_call"]["tool_input"])
                    else:
                        logger.typewriter_log("message_to_tool_node error: schema for tool {} not found!".format(function_input["tool_call"]["tool_name"]),Fore.RED)
                        function_input["tool_call"]["tool_input"] = {}
                else:
                    function_input["tool_call"]["tool_input"] = {}
                
                for key in ["thought","reasoning","plan","criticism"]:
                    if key in function_input.keys():
                        new_node.data["thoughts"]["properties"][key] = function_input[key]

                new_node.data["command"]["properties"]["name"] = function_input["tool_call"]["tool_name"]
                new_node.data["command"]["properties"]["args"] = function_input["tool_call"]["tool_input"]
            else:
                new_node.data["command"]["properties"]["name"] = message["function_call"]["name"]
                new_node.data["command"]["properties"]["args"] = json5.loads(message["function_call"]["arguments"])
        else:
            logger.typewriter_log("message_to_tool_node error: no function_call in message",Fore.RED)

        return new_node

    def fill_in_placeholders(self, placeholders: dict):
        filled_messages = deepcopy(self.prompt_messages)
        for message in filled_messages:
            role = message.role
            if role in placeholders:
                for key, value in placeholders[role].items():
                    message.content = message.content.replace("{{" + str(key) + "}}", str(value))
        return filled_messages

class GPT4Normal(BaseAgent):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def parse(self, messages, stop=None, **args):
        output = _chat_completion_request(messages=messages, model=self.config.default_completion_kwargs['model'], stop=stop, **args)

        message = output['choices'][0]['message']

        tokens = output['usage']

        return LLMStatusCode.SUCCESS, message, tokens
    
    @overload
    def message_to_tool_node(self, message):
        node_info_data = json5.loads(message["content"])



        new_node = ToolNode()
        for key,value in node_info_data["thoughts"].items():
            if key in new_node.data["thoughts"]["properties"].keys():
                new_node.data["thoughts"]["properties"][key] = value


        command_name, arguments = get_command(node_info_data)
        new_node.data["command"]["properties"]["name"] = command_name
        new_node.data["command"]["properties"]["args"] = arguments

        return new_node
