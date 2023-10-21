import json
import json5
import jsonschema
from typing import List
from colorama import Fore
from copy import  deepcopy
from tenacity import retry, stop_after_attempt

from XAgent.agent.base_agent import BaseAgent
from XAgent.utils import RequiredAbilities, LLMStatusCode
from XAgent.agent.utils import _chat_completion_request
from XAgent.message_history import Message
from XAgent.config import CONFIG
from XAgent.ai_functions import function_manager
from XAgent.ai_functions.request import dynamic_json_fixs,FunctionCallSchemaError
from XAgent.logs import logger

class ToolAgent(BaseAgent):
    abilities = set([RequiredAbilities.tool_tree_search])
    
    @retry(stop=stop_after_attempt(CONFIG.max_retry_times),reraise=True)
    def parse(
        self,
        placeholders: dict = {},
        functions=None,
        function_call=None,
        stop=None,
        additional_messages: List[Message] = [],
        additional_insert_index: int = -1,
        *args,
        **kwargs
    ):
        
        prompt_messages = self.fill_in_placeholders(placeholders)
        messages = prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
        messages = [ message.raw() for message in messages]

        response = _chat_completion_request(
            messages=messages,
            functions=functions,
            function_call=function_call,
            model=self.config.default_completion_kwargs['model'],
            stop=stop,
            *args,
            **kwargs
        )
        if response["choices"][0]["message"]["function_call"]['name'] == 'subtask_handle':
            # validate the tool_call only here
            arguments = json5.loads(response["choices"][0]["message"]["function_call"]['arguments'])
            tool_schema = function_manager.get_function_schema(arguments['tool_call']["tool_name"])
            assert tool_schema is not None, f"Function {arguments['tool_call']['tool_name']} not found! Poential Schema Validation Error!"

            partial_res = deepcopy(dict(response["choices"][0]["message"]))

            if 'tool_input' in arguments['tool_call']:
                tool_call_args = arguments['tool_call']['tool_input']
                partial_res['function_call']['arguments'] = json5.loads(partial_res['function_call']['arguments'])
                partial_res['function_call']['arguments']['tool_call']['tool_input'] = '`Wrapped`'
            else:
                tool_call_args = ''
                
            partial_res['content'] = json.dumps(partial_res.pop('function_call'))
            composed_messages = messages+[partial_res]
            
            retries = 0
            while retries < CONFIG.max_retry_times:
                try:
                    if isinstance(tool_call_args,str):
                        tool_call_args = {} if tool_call_args == '' else json5.loads(tool_call_args)
                    jsonschema.validate(instance=tool_call_args, schema=tool_schema['parameters'])
                    
                    break
                except Exception as e:  
                    # logger.typewriter_log('Schema Validation for tool call arguments failed, trying to fix it...',Fore.YELLOW)
                    if not isinstance(tool_call_args,str):
                        tool_call_args = json5.dumps(tool_call_args)
                    new_tool_response = dynamic_json_fixs(tool_call_args,tool_schema,composed_messages,str(e))
                    tool_call_args = new_tool_response["choices"][0]["message"]["function_call"]["arguments"]
                        
                    retries += 1
                    if retries >= CONFIG.max_retry_times:
                        raise e
            
            # update the arguments
            arguments['tool_call']['tool_input'] = json.dumps(tool_call_args)
            response["choices"][0]["message"]["function_call"]['arguments'] = json.dumps(arguments) 
            
        message = response["choices"][0]["message"]
        tokens = response["usage"]

        return LLMStatusCode.SUCCESS, message, tokens
