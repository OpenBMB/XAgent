
import json
import openai

from openai.error import InvalidRequestError

from XAgent.logs import logger
from XAgent.config import CONFIG, get_apiconfig_by_model, get_model_name


def chatcompletion_request(**kwargs):
    """
    Performs a chat completion request to OpenAI's Chat Model taking 
    optional arguments as parameters to customize the request.

    It expects the necessary parameters to be passed in the kwargs to create 
    a chat completion. By default, it uses the model specified in the CONFIG. 
    If the context length is exceeded, the function throws an 'InvalidRequestError'.

    Args:
        **kwargs (dict): The dictionary of parameters passed to the 
        `openai.ChatCompletion.create` method. The parameters can be any valid 
        input parameters accepted by this method. A 'model' key is expected 
        in kwargs. If it exists, it is used, else the model defined in
        CONFIG is used.

    Returns:
        dict: response from the `openai.ChatCompletion.create` method.

    Raises:
        InvalidRequestError: If the context length is exceeded or 
        any other request error occurs during the process.
    """
    model_name = get_model_name(kwargs.pop('model', CONFIG.default_completion_kwargs['model']))
    logger.debug("chatcompletion: using " + model_name)
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)
    chatcompletion_kwargs.update(kwargs)
    
    try:
        response = openai.ChatCompletion.create(**chatcompletion_kwargs)
        response = json.loads(str(response))
        if response['choices'][0]['finish_reason'] == 'length':
            raise InvalidRequestError('maximum context length exceeded', None)
    except InvalidRequestError as e:
        raise e
                    
    return response
