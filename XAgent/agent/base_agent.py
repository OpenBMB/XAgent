import abc
import json5
from typing import List
from colorama import Fore
from copy import deepcopy

from XAgent.config import CONFIG
from XAgent.utils import LLMStatusCode, RequiredAbilities
from XAgent.message_history import Message
from XAgent.logs import logger
from XAgent.ai_functions import objgenerator


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

    def fill_in_placeholders(self, placeholders: dict):
        filled_messages = deepcopy(self.prompt_messages)
        for message in filled_messages:
            role = message.role
            if role in placeholders:
                for key, value in placeholders[role].items():
                    message.content = message.content.replace("{{" + str(key) + "}}", str(value))
        return filled_messages
    
    
    def generate(self,
                 messages:list[dict]|list[Message],
                 arguments:dict=None,
                 functions:list[dict]=None,
                 function_call:dict=None,
                 stop:dict=None,
                 *args,**kwargs):
        if isinstance(messages[0],Message):
            messages = [message.raw() for message in messages]
        if functions is not None and len(functions) == 1 and function_call is None:
            function_call = {'name':functions[0]['name']} # must call at least one function
        match CONFIG.default_request_type:
            case 'openai':
                if arguments is not None:
                    if functions is None or len(functions) == 0:
                        functions = [{
                            'name':'reasoning',
                            'parameters':arguments
                        }]
                        function_call = {'name':'reasoning'}
                    elif len(functions) == 1:
                        for k,v in arguments['properties'].items():
                            functions[0]['parameters']['properties'][k] = v
                            if k in arguments['required']:
                                functions[0]['parameters']['required'].append(k)
                    else:
                        raise NotImplementedError("Not implemented for multiple functions with arguments")
                    
                response = objgenerator.chatcompletion(
                    messages=messages,
                    functions=functions,
                    function_call=function_call,
                    stop=stop,
                    *args,**kwargs)
                
                message = {}
                function_call_args:dict = json5.loads(response["choices"][0]["message"]["function_call"]['arguments'])
                
                if arguments is not None:
                    message['arguments'] = {
                        k: function_call_args.pop(k)
                        for k in arguments['properties'].keys() if k in function_call_args
                    }
                if len(function_call_args) > 0:
                    message['function_call'] = {
                        'name': response['choices'][0]['message']['function_call']['name'],
                        'arguments': function_call_args
                    }

            case 'xagent':
                response = objgenerator.chatcompletion(
                    messages=messages,
                    arguments=arguments,
                    functions=functions,
                    function_call=function_call,
                    stop=stop,
                    *args,**kwargs)
                message = json5.loads(response["choices"][0]["message"]['content'])
            case _:
                raise NotImplementedError(f"Request type {CONFIG.default_request_type} not implemented")
            
        tokens = response["usage"]
        return message, tokens