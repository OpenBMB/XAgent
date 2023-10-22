import json
import openai

from openai.error import InvalidRequestError

from XAgent.logs import logger
from XAgent.config import CONFIG,get_apiconfig_by_model


def chatcompletion_request(**kwargs):
    model_name = kwargs.pop('model')
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)
    chatcompletion_kwargs.update(kwargs)
    
    try:
        response = openai.ChatCompletion.create(**chatcompletion_kwargs)
        response = json.loads(str(response))
        if response['choices'][0]['finish_reason'] == 'length':
            raise InvalidRequestError('maximum context length exceeded',None)
    except InvalidRequestError as e:
        logger.info(e)
        if 'maximum context length' in e._message:
            if model_name == 'gpt-4':
                if 'gpt-4-32k' in CONFIG.api_keys:
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
            response = json.loads(str(response))
        else:
            raise e
                    
    return response
