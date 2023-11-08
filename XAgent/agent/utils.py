import json
from typing import Dict

def get_command(response_json: Dict):
    """
    Parses the response and returns the command name and arguments.

    This function will raise the exception `json.decoder.JSONDecodeError` if the response is not valid JSON.
    Any other error that occurs is also caught and the function returns an "Error:" message with the exception message.

    Args:
        response_json (Dict): The response from the AI in dictionary format.

    Returns:
        tuple: The command name and arguments, or some error indication.
               If the response json dictionary does not contain the 'command' key, or the value of
               'command' is not a dictionary, or the 'command' dictionary does not contain the 'name' key,
               returns a tuple where the first element is 'Error:' and the second element is a string explaining the problem.
               If some error occurs, returns a tuple where the first element is 'Error:' and the second element is the str of the exception.

    Raises:
        json.decoder.JSONDecodeError: If the response is not valid JSON.
        Exception: If any other error occurs.
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