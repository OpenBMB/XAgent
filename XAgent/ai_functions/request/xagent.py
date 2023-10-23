import json
import openai

from openai.error import InvalidRequestError

from XAgent.logs import logger
from XAgent.config import CONFIG,get_apiconfig_by_model,get_model_name


def chatcompletion_request(**kwargs):
    model_name = get_model_name(kwargs.pop('model',CONFIG.default_completion_kwargs['model']))
    logger.debug("chatcompletion: using " + model_name)
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)
    chatcompletion_kwargs.update(kwargs)
    
    try:
        response = openai.ChatCompletion.create(**chatcompletion_kwargs)
        response = json.loads(str(response))
        if response['choices'][0]['finish_reason'] == 'length':
            raise InvalidRequestError('maximum context length exceeded',None)
    except InvalidRequestError as e:
        raise e
                    
    return response
