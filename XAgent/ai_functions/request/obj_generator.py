import json5
import jsonschema
import importlib


from copy import deepcopy
from colorama import Fore

from openai.error import AuthenticationError, PermissionError, InvalidRequestError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type, wait_chain, wait_none


from .error import FunctionCallSchemaError

from XAgent.logs import logger
from XAgent.config import CONFIG,get_model_name,get_apiconfig_by_model


class OBJGenerator:
    def __init__(self,):        
        self.chatcompletion_request_funcs = {}
        
    # @retry(
    #     retry=retry_if_not_exception_type((AuthenticationError, PermissionError, InvalidRequestError, AssertionError)),
    #     stop=stop_after_attempt(CONFIG.max_retry_times+3), 
    #     wait=wait_chain(*[wait_none() for _ in range(3)]+[wait_exponential(min=113, max=293)]),
    #     reraise=True)
    def chatcompletion(self,**kwargs):
        model_name = get_model_name(kwargs.pop('model',CONFIG.default_completion_kwargs['model']))
        kwargs['model'] = model_name
        logger.debug("chatcompletion: using " + model_name)

        request_type = kwargs.pop('request_type',CONFIG.default_request_type)
        for k in list(kwargs.keys()):
            if kwargs[k] is None:
                kwargs.pop(k)
        
        response = self._get_chatcompletion_request_func(request_type)(**kwargs)
        
        # refine the response
        match request_type:
            case 'openai':                
                response = self.function_call_refine(kwargs,response)
            case 'xagent':
                pass
            case _:
                raise NotImplementedError(f"Request type {request_type} not implemented")
        
        return response
        
    def _get_chatcompletion_request_func(self, request_type:str):
        if request_type not in self.chatcompletion_request_funcs:
            module = importlib.import_module(f'.{request_type}','XAgent.ai_functions.request')
            self.chatcompletion_request_funcs[request_type] = getattr(module,'chatcompletion_request')
        return self.chatcompletion_request_funcs[request_type]

    def dynamic_json_fixs(self, broken_json, function_schema, messages: list = [], error_message: str = None):
        logger.typewriter_log(
            f'Schema Validation for Function call {function_schema["name"]} failed, trying to fix it...', Fore.YELLOW)
        repair_req_kwargs = deepcopy(CONFIG.default_completion_kwargs)
        repair_req_kwargs['messages'] = [*messages,
                                  {
                                      'role': 'system',
                                      'content': '\n'.join([
                                          'Your last function call result in error',
                                          '--- Error ---',
                                          error_message,
                                          'Your task is to fix all errors exist in the Broken Json String to make the json validate for the schema in the given function, and use new string to call the function again.',
                                          '--- Notice ---',
                                          '- You need to carefully check the json string and fix the errors or adding missing value in it.',
                                          '- Do not give your own opinion or imaging new info or delete exisiting info!',
                                          '- Make sure the new function call does not contains information about this fix task!',
                                          '--- Broken Json String ---',
                                          broken_json,
                                          'Start!'
                                      ])
                                  }]
        repair_req_kwargs['functions'] = [function_schema]
        repair_req_kwargs['function_call'] = {'name': function_schema['name']}
        return self.chatcompletion(**repair_req_kwargs)
    
    def load_args_with_schema_validation(self,function_schema:dict,args:str,messages:list=[],*,return_response=False,response=None):
        # loading arguments
        arguments = args
        def validate():
            nonlocal function_schema,arguments
            if isinstance(arguments,str):
                arguments = {} if arguments == '' else json5.loads(arguments)
            jsonschema.validate(instance=arguments, schema=function_schema['parameters'])
            
        try:
            validate()
        except Exception as e:
            if not isinstance(arguments,str):
                arguments = json5.dumps(arguments)
            # give one opportunity to fix the json string
            response = self.dynamic_json_fixs(arguments,function_schema,messages,str(e))
            arguments = response['choices'][0]['message']['function_call']['arguments']
            validate()

        if return_response:
            return arguments,response
        else:
            return arguments
        
    def function_call_refine(self,req_kwargs,response):
        if  'function_call' not in response['choices'][0]['message']:
            logger.warn("FunctionCallSchemaError: No function call found in the response")
            raise FunctionCallSchemaError(f"No function call found in the response: {response['choices'][0]['message']} ")
        
        # verify the schema of the function call if exists
        function_schema = list(filter(lambda x: x['name'] == response['choices'][0]['message']['function_call']['name'],req_kwargs['functions']))
        function_schema = None if len(function_schema) == 0 else function_schema[0]
        
        if function_schema is None:
            error_message = {
                'role':'system',
                'content': f"Your last function calling call function {response['choices'][0]['message']['function_call']['name']} that is not in the provided functions. Make sure function name in list: {list(map(lambda x:x['name'],req_kwargs['functions']))}"
            }
            
            if req_kwargs['messages'][-1]['role'] != 'system' and 'Your last function calling call function' not in req_kwargs['messages'][-1]['content']:
                req_kwargs['messages'].append(error_message)
            elif req_kwargs['messages'][-1]['role'] == 'system' and 'Your last function calling call function' in req_kwargs['messages'][-1]['content']:
                req_kwargs['messages'][-1] = error_message
                
            logger.warn(f"FunctionCallSchemaError: Function {response['choices'][0]['message']['function_call']['name']} not found in the provided functions.")
            raise FunctionCallSchemaError(f"Function {response['choices'][0]['message']['function_call']['name']} not found in the provided functions: {list(map(lambda x:x['name'],req_kwargs['functions']))}")
            
        arguments,response = self.load_args_with_schema_validation(function_schema,response['choices'][0]['message']['function_call']['arguments'],req_kwargs['messages'],return_response=True,response=response)
        return response
    
objgenerator = OBJGenerator()