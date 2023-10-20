import json5
import openai
import jsonschema

from copy import deepcopy
from colorama import Fore

from openai.error import AuthenticationError, PermissionError, InvalidRequestError
from tenacity import retry, stop_after_attempt, wait_exponential,retry_if_not_exception_type, wait_chain, wait_none

from XAgent.loggers.logs import logger
from XAgent.config import CONFIG,get_openai_model_name,get_apiconfig_by_model
from XAgent.running_recorder import recorder


class FunctionCallSchemaError(Exception):
    pass




def dynamic_json_fixs(args,function_schema,messages:list=[],error_message:str=None):
    logger.typewriter_log(f'Schema Validation for Function call {function_schema["name"]} failed, trying to fix it...',Fore.YELLOW)
    repair_req = deepcopy(CONFIG.default_completion_kwargs)
    repair_req['messages'] = [*messages,
        {
            'role':'system',
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
                args,
                'Start!'
            ])
        }]
    repair_req['functions'] = [function_schema]
    repair_req['function_call'] = {'name':function_schema['name']}
    return openai_chatcompletion_request(function_call_check=False,**repair_req)


def load_args_with_schema_validation(function_schema:dict,args:str,messages:list=[],*,return_response=False,response=None):
    # loading arguments
    arguments = args
    retries = 0
    while retries < CONFIG.max_retry_times:
        try:
            if isinstance(arguments,str):
                arguments = {} if arguments == '' else json5.loads(arguments)

            jsonschema.validate(instance=arguments, schema=function_schema['parameters'])
            
            break
        except Exception as e:
            if not isinstance(arguments,str):
                arguments = json5.dumps(arguments)
            response = dynamic_json_fixs(arguments,function_schema,messages,str(e))
            arguments = response['choices'][0]['message']['function_call']['arguments']
            
            retries += 1
            if retries >= CONFIG.max_retry_times:
                raise e
    
    if return_response:
        return arguments,response
    else:
        return arguments


LLM_query_count = 0 #motex lock

@retry(retry=retry_if_not_exception_type((AuthenticationError, PermissionError, InvalidRequestError,AssertionError)),stop=stop_after_attempt(CONFIG.max_retry_times+6),wait=wait_chain(*[wait_none() for _ in range(6)]+[wait_exponential(min=113, max=293)]),reraise=True)
def openai_chatcompletion_request(*,function_call_check=True,record_query_response=None,**kwargs):
    global LLM_query_count
    regist_kwargs = deepcopy(kwargs)
    query_kwargs = deepcopy(kwargs)
    model_name = get_openai_model_name(kwargs.pop('model', 'gpt-3.5-turbo-16k'))
    logger.info("openai_chatcompletion_request: using " + model_name)
    
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)
    chatcompletion_kwargs.update(kwargs)
    chatcompletion_kwargs.pop('schema_error_retry',None)
    llm_query_id = deepcopy(LLM_query_count) #motex lock
    LLM_query_count += 1
    record_query_response = recorder.query_llm_inout(llm_query_id = llm_query_id,
                                        messages=query_kwargs.pop("messages",None), 
                                        functions=query_kwargs.pop("functions",None), 
                                        function_call=query_kwargs.pop("function_call",None), 
                                        model = query_kwargs.pop("model",None),
                                        stop = query_kwargs.pop("stop",None),
                                        other_args = query_kwargs)
    if record_query_response != None:
        response = record_query_response
    else:
        try:
            response = openai.ChatCompletion.create(**chatcompletion_kwargs)
            response = json5.loads(str(response))
            if response['choices'][0]['finish_reason'] == 'length':
                raise InvalidRequestError('maximum context length exceeded',None)
        except InvalidRequestError as e:
            logger.info(e)
            if 'maximum context length' in e._message:
                if model_name == 'gpt-4':
                    if 'gpt-4-32k' in CONFIG.openai_keys:
                        model_name = 'gpt-4-32k'
                    else:
                        model_name = 'gpt-3.5-turbo-16k'
                elif model_name == 'gpt-3.5-turbo':
                    model_name = 'gpt-3.5-turbo-16k'
                else:
                    raise e
                print("max context length reached, retrying with " + model_name)
                chatcompletion_kwargs = get_apiconfig_by_model(model_name)
                chatcompletion_kwargs.update(kwargs)
                chatcompletion_kwargs.pop('schema_error_retry',None)
                
                response = openai.ChatCompletion.create(**chatcompletion_kwargs)
                response = json5.loads(str(response))
            else:
                raise e
                    
    # register the request and response
    # import pdb; pdb.set_trace()
    recorder.regist_llm_inout(llm_query_id = llm_query_id,
                        messages=regist_kwargs.pop('messages',None), 
                        functions=regist_kwargs.pop('functions',None), 
                        function_call=regist_kwargs.pop('function_call',None), 
                        model = regist_kwargs.pop('model',None),
                        stop = regist_kwargs.pop('stop',None),
                        other_args = regist_kwargs,
                        output_data = response)
    if function_call_check:
        if  'function_call' not in response['choices'][0]['message']:
            logger.info("FunctionCallSchemaError")
            raise FunctionCallSchemaError(f"No function call found in the response: {response['choices'][0]['message']} ")  
        # verify the schema of the function call if exists
        function_schema = None
        for function in kwargs['functions']:
            if function['name'] == response['choices'][0]['message']['function_call']['name']:
                function_schema = function
        if function_schema is None:
            function_schema_error = f"Your last function calling call function {response['choices'][0]['message']['function_call']['name']} that is not in the provided functions. Make sure function name in list: {list(map(lambda x:x['name'],kwargs['functions']))}"
            
            if 'schema_error_retry' not in kwargs:
                kwargs['schema_error_retry'] = True
                kwargs['messages'].append({
                    'role':'system',
                    'content':function_schema_error
                })
            else:
                kwargs['messages'][-1]['content'] = function_schema_error

            logger.info("not found in the provided functions")
            raise FunctionCallSchemaError(f"Function {response['choices'][0]['message']['function_call']['name']} not found in the provided functions: {list(map(lambda x:x['name'],kwargs['functions']))}")
        
        arguments,response = load_args_with_schema_validation(function_schema,response['choices'][0]['message']['function_call']['arguments'],kwargs['messages'],return_response=True,response=response)


    return response
