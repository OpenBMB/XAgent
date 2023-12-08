import json
import openai
from openai.error import InvalidRequestError
from XAgent.logs import logger
from XAgent.config import CONFIG,get_apiconfig_by_model,get_model_name
import requests
import traceback


def chatcompletion_request(**kwargs):
    logger.info(f"xagent received {json.dumps(kwargs)}")
    model_name = get_model_name(kwargs.pop('model',CONFIG.default_completion_kwargs['model']))
    logger.debug("chatcompletion: using " + model_name)
    chatcompletion_kwargs = get_apiconfig_by_model(model_name)
    chatcompletion_kwargs.update(kwargs)
    try:
        #response = openai.ChatCompletion.create(**chatcompletion_kwargs)
        response = requests.post("http://127.0.0.1:8081/chat/completions",
                headers={"accept": "application/json", "Content-Type": "application/json"},
                json={
                        "model": model_name,
                        "repetition_penalty": 1.05,
                        "messages": chatcompletion_kwargs.get("messages", []),
                        "global_arguments": chatcompletion_kwargs.get("arguments",{}),
                        "tools": chatcompletion_kwargs.get("functions",[]),
                        "tool_choice": chatcompletion_kwargs.get("function_call", {}),
                    }
                ).json()
        logger.info(f"xagent get response: {response}")
        # response = json.loads(str(response))
        if response['choices'][0]['finish_reason'] == 'length':
            raise InvalidRequestError('maximum context length exceeded',None)
    except InvalidRequestError as e:
        logger.error(f"xagent get error: {traceback.format_exc()}")
        raise e
    return response
