import json
import json5
import jsonschema
from typing import List
from colorama import Fore
from tenacity import retry, stop_after_attempt

from XAgent.agent.base_agent import BaseAgent
from XAgent.utils import RequiredAbilities
from XAgent.message_history import Message
from XAgent.logs import logger
from XAgent.data_structure.node import ToolNode
from XAgent.ai_functions import function_manager,objgenerator
from XAgent.config import CONFIG

class ToolAgent(BaseAgent):
    """
    This class is used to represent the ToolAgent object, which is inherited from the BaseAgent. It mainly focuses
    on actions around the tool tree and its functions.

    Attributes:
        abilities (set): Set to store the abilities of the current ToolAgent. By default, it is set to 
        `RequiredAbilities.tool_tree_search`.
    """
    abilities = set([RequiredAbilities.tool_tree_search])

    @retry(stop=stop_after_attempt(CONFIG.max_retry_times),reraise=True)
    def parse(
        self,
        placeholders: dict = {},
        arguments:dict=None,
        functions=None,
        function_call=None,
        stop=None,
        additional_messages: List[Message] = [],
        additional_insert_index: int = -1,
        *args,
        **kwargs
    ):
        """
        This function generates a message list and a token list based on the input parameters using the 
        `generate()` function, modifies it as per specific conditions, and returns it.
        
        Args:
            placeholders (dict, optional): Dictionary object to store the placeholders and their mappings.
            arguments (dict, optional): Dictionary object to store argument's details.
            functions: List of permissible functions that can be inserted in the function fields for the `openai` type.
            function_call: A dictionary representing the current function call being processed.
            stop: The termination condition for the loop.
            additional_messages (list, optional): List of additional messages to be appended to the existing message list.
            additional_insert_index (int, optional): The index position to insert the additional messages.
            *args: Variable length argument list for the parent class's `generate()` function.
            **kwargs: Arbitrary keyword arguments for the parent class's `generate()` function.
            
        Returns:
            tuple: A tuple containing a dictionary of the parsed message and a list of tokens.
            
        Raises:
            AssertionError: If the specified function schema is not found in the list of possible functions.
            Exception: If the validation of the tool's call arguments fails.
        """
        
        prompt_messages = self.fill_in_placeholders(placeholders)
        messages = prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
        messages = [message.raw() for message in messages]
        
        # Temporarily disable the arguments for openai
        if self.config.default_request_type == 'openai':
            arguments = None
            functions = list(filter(lambda x: x['name'] not in ['subtask_submit','subtask_handle'],functions))
            if CONFIG.enable_ask_human_for_help:
                functions += [function_manager.get_function_schema('ask_human_for_help')]
            messages[0]['content'] += '\n--- Avaliable Tools ---\nYou are allowed to use tools in the "subtask_handle.tool_call" function field.\nRemember the "subtask_handle.tool_call.tool_input" field should always in JSON, as following described:\n{}'.format(json.dumps(functions,indent=2))
            
            def change_tool_call_description(message:dict,reverse:bool=False):
                des_pairs = [('Use tools to handle the subtask',
                              'Use "subtask_handle" to make a normal tool call to handle the subtask'),
                             ('5.1  Please remember to generate the function call field after the "criticism" field.\n  5.2  Please check all content is in json format carefully.',
                              '5.1. Please remember to generate the "tool_call" field after the "criticism" field.\n  5.2. Please remember to generate comma if the "tool_call" field is after the "criticism" field.\n  5.3. Please check whether the **"tool_call"** field is in the function call json carefully.'),
                             ('After decide the action, use "subtask_handle" functions to apply action.',
                              'After decide the action, call functions to apply action.')]
                
                for pair in des_pairs:
                    message['content'] = message['content'].replace(pair[0],pair[1]) if reverse else message['content'].replace(pair[1],pair[0])
                    
                return message
            
            messages[0] = change_tool_call_description(messages[0])
            functions = [function_manager.get_function_schema('subtask_submit'),
                         function_manager.get_function_schema('subtask_handle')]

        message,tokens = self.generate(
            messages=messages,
            arguments=arguments,
            functions=functions,
            function_call=function_call,
            stop=stop,
            *args,**kwargs
        )

        function_call_args:dict = message['function_call']['arguments']

        # for tool_call, we need to validate the tool_call arguments if exising
        if self.config.default_request_type == 'openai' and 'tool_call' in function_call_args:
            tool_schema = function_manager.get_function_schema(function_call_args['tool_call']["tool_name"])
            assert tool_schema is not None, f"Function {function_call_args['tool_call']['tool_name']} not found! Poential Schema Validation Error!"
            
            tool_call_args = function_call_args['tool_call']['tool_input'] if 'tool_input' in function_call_args['tool_call'] else ''
            
            def validate():
                nonlocal tool_schema,tool_call_args
                if isinstance(tool_call_args,str):
                    tool_call_args = {} if tool_call_args == '' else json5.loads(tool_call_args)
                jsonschema.validate(instance=tool_call_args, schema=tool_schema['parameters'])
            
            try:
                validate()
            except Exception as e:  
                messages[0] = change_tool_call_description(messages[0],reverse=True)
                tool_call_args = objgenerator.dynamic_json_fixes(
                    broken_json=tool_call_args,
                    function_schema=tool_schema,
                    messages=messages,
                    error_message=str(e))["choices"][0]["message"]["function_call"]["arguments"]
                validate()
            
            function_call_args['tool_call']['tool_input'] = tool_call_args
            
            message['function_call'] = function_call_args.pop('tool_call')
            message['function_call']['name'] = message['function_call'].pop('tool_name')
            message['function_call']['arguments'] = message['function_call'].pop('tool_input')
            message['arguments'] = function_call_args
                
        return message,tokens
    
    def message_to_tool_node(self,message) -> ToolNode:
        """
        This method converts a given message dictionary to a ToolNode object.
        
        Args:
            message (dict): Dictionary of message data containing content, function call and arguments.

        Returns:
            ToolNode: A ToolNode object generated from the provided message.
            
        Warning:
            If the `function_call` field is missing in the input message, a warning message will be logged. 
        """
        
        # assume message format
        # {
        #   "content": "The content is useless",
        #   "function_call": {
        #       "name": "xxx",
        #       "arguments": "xxx"
        #  },
        #  "arguments": {
        #      "xxx": "xxx",
        #      "xxx": "xxx"   
        #  },
        # }
        
        new_node = ToolNode()
        if "content" in message.keys():
            print(message["content"])
            new_node.data["content"] = message["content"]
        if 'arguments' in message.keys():
            new_node.data['thoughts']['properties'] = message["arguments"]
        if "function_call" in message.keys():
            new_node.data["command"]["properties"]["name"] = message["function_call"]["name"]
            new_node.data["command"]["properties"]["args"] = message["function_call"]["arguments"]
        else:
            logger.typewriter_log("message_to_tool_node warning: no function_call in message",Fore.RED)

        return new_node