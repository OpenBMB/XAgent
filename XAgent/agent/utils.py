import json
import json5
import openai
import traceback
import jsonschema

from copy import deepcopy
from typing import Dict, List, Union
from colorama import Fore, Style

from openai.error import AuthenticationError, PermissionError, InvalidRequestError
from tenacity import retry, stop_after_attempt,retry_if_not_exception_type

from XAgent.utils import TaskSaveItem, LLMStatusCode
from XAgent.message_history import Message
from XAgent.logs import logger
from XAgent.config import CONFIG
from XAgent.running_recorder import recorder
from XAgent.ai_functions.request import openai_chatcompletion_request


@retry(retry=retry_if_not_exception_type((AuthenticationError, PermissionError, InvalidRequestError)),stop=stop_after_attempt(CONFIG.max_retry_times),reraise=True)
def _chat_completion_request(messages, functions=None,function_call=None, model="gpt-3.5-turbo-16k",stop=None,restrict_cache_query=True, **kwargs):
    if isinstance(messages[0],Message):
        messages = [ message.raw() for message in messages]

    json_data = deepcopy(kwargs)
    json_data.update({"messages": messages})
    json_data.update({'model': model})
    if stop is not None:
        json_data.update({"stop": stop})
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    
    # Yujia: maybe temperature == 0 is more stable? Not rigrously tested.
    # json_data.update({"temperature": 0.1})
    response = openai_chatcompletion_request(**json_data)

    return response

def get_command(response_json: Dict):
    """Parse the response and return the command name and arguments

    Args:
        response_json (json): The response from the AI

    Returns:
        tuple: The command name and arguments

    Raises:
        json.decoder.JSONDecodeError: If the response is not valid JSON

        Exception: If any other error occurs
    """
    try:
        if "command" not in response_json:
            return "Error:", "Missing 'command' object in JSON"

        if not isinstance(response_json, dict):
            return "Error:", f"'response_json' object is not dictionary {response_json}"

        command = response_json["command"]
        if not isinstance(command, dict):
            return "Error:", "'command' object is not a dictionary"

        if "name" not in command:
            return "Error:", "Missing 'name' field in 'command' object"

        command_name = command["name"]

        # Use an empty dictionary if 'args' field is not present in 'command' object
        arguments = command.get("args", {})

        return command_name, arguments
    except json.decoder.JSONDecodeError:
        return "Error:", "Invalid JSON"
    # All other errors, return "Error: + error message"
    except Exception as e:
        return "Error:", str(e)

if __name__ == "__main__":
    _chat_completion_request(messages=[])