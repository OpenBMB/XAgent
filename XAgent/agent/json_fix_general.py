"""This module contains functions to fix JSON strings using general programmatic approaches, suitable for addressing
common JSON formatting issues."""
from __future__ import annotations

import contextlib
import json
import re
from typing import Optional
from regex import regex
from colorama import Fore
from jsonschema import Draft7Validator
import os
import json5
from XAgent.logs import logger

# CFG = Config()

def extract_char_position(error_message: str) -> int:
    """Extract the character position from the JSONDecodeError message.

    Args:
        error_message (str): The error message from the JSONDecodeError
          exception.

    Returns:
        int: The character position.
    """

    char_pattern = re.compile(r"\(char (\d+)\)")
    if match := char_pattern.search(error_message):
        return int(match[1])
    else:
        raise ValueError("Character position not found in the error message.")


def validate_json(json_object: object, schema_name: str) -> dict | None:
    """
    :type schema_name: object
    :param schema_name: str
    :type json_object: object
    """
    # scheme_file = os.path.join(os.path.dirname(__file__), f"{schema_name}.json")
    # with open(scheme_file, "r") as f:
        # schema = json.load(f)
    # validator = Draft7Validator(schema)
    validator = Draft7Validator(schema_name)

    if errors := sorted(validator.iter_errors(json_object), key=lambda e: e.path):
        logger.error("The JSON object is invalid.")
        # if CFG.debug_mode:
        logger.error(
            json.dumps(json_object, indent=4)
        )  # Replace 'json_object' with the variable containing the JSON data
        logger.error("The following issues were found:")

        for error in errors:
            logger.error(f"Error: {error.message}")
    else:
        logger.debug("The JSON object is valid.")

    return json_object


def validate_json_string(json_string: str, schema_name: str) -> dict | None:
    """
    :type schema_name: object
    :param schema_name: str
    :type json_object: object
    """

    try:
        json_loaded = json.loads(json_string)
        return validate_json(json_loaded, schema_name)
    except:
        return None


def is_string_valid_json(json_string: str, schema_name: str) -> bool:
    """
    :type schema_name: object
    :param schema_name: str
    :type json_object: object
    """

    return validate_json_string(json_string, schema_name) is not None


def extract_char_position(error_message: str) -> int:
    """Extract the character position from the JSONDecodeError message.

    Args:
        error_message (str): The error message from the JSONDecodeError
          exception.

    Returns:
        int: The character position.
    """

    char_pattern = re.compile(r"\(char (\d+)\)")
    if match := char_pattern.search(error_message):
        return int(match[1])
    else:
        raise ValueError("Character position not found in the error message.")

def fix_invalid_escape(json_to_load: str, error_message: str) -> str:
    """Fix invalid escape sequences in JSON strings.

    Args:
        json_to_load (str): The JSON string.
        error_message (str): The error message from the JSONDecodeError
          exception.

    Returns:
        str: The JSON string with invalid escape sequences fixed.
    """
    while error_message.startswith("Invalid \\escape"):
        bad_escape_location = extract_char_position(error_message)
        json_to_load = (
            json_to_load[:bad_escape_location] + json_to_load[bad_escape_location + 1 :]
        )
        try:
            json.loads(json_to_load)
            return json_to_load
        except json.JSONDecodeError as e:
            logger.debug("json loads error - fix invalid escape", e)
            error_message = str(e)
    return json_to_load


def balance_braces(json_string: str) -> Optional[str]:
    """
    Balance the braces in a JSON string.

    Args:
        json_string (str): The JSON string.

    Returns:
        str: The JSON string with braces balanced.
    """

    open_braces_count = json_string.count("{")
    close_braces_count = json_string.count("}")

    while open_braces_count > close_braces_count:
        json_string += "}"
        close_braces_count += 1

    while close_braces_count > open_braces_count:
        json_string = json_string.rstrip("}")
        close_braces_count -= 1

    with contextlib.suppress(json.JSONDecodeError):
        json.loads(json_string)
        return json_string


def add_quotes_to_property_names(json_string: str) -> str:
    """
    Add quotes to property names in a JSON string.

    Args:
        json_string (str): The JSON string.

    Returns:
        str: The JSON string with quotes added to property names.
    """

    def replace_func(match: re.Match) -> str:
        return f'"{match[1]}":'

    property_name_pattern = re.compile(r"(\w+):")
    corrected_json_string = property_name_pattern.sub(replace_func, json_string)

    try:
        json.loads(corrected_json_string)
        return corrected_json_string
    except json.JSONDecodeError as e:
        raise e


def correct_json(json_to_load: str) -> str:
    """
    Correct common JSON errors.
    Args:
        json_to_load (str): The JSON string.
    """

    try:
        logger.debug("json", json_to_load)
        json.loads(json_to_load)
        return json_to_load
    except json.JSONDecodeError as e:
        logger.debug("json loads error", e)
        error_message = str(e)
        if error_message.startswith("Invalid \\escape"):
            json_to_load = fix_invalid_escape(json_to_load, error_message)
        if error_message.startswith(
            "Expecting property name enclosed in double quotes"
        ):
            json_to_load = add_quotes_to_property_names(json_to_load)
            try:
                json5.loads(json_to_load)
                return json_to_load
            except json.JSONDecodeError as e:
                logger.debug("json loads error - add quotes", e)
                error_message = str(e)
        if balanced_str := balance_braces(json_to_load):
            return balanced_str
    return json_to_load

def fix_json_using_multiple_techniques(assistant_reply: str, raise_error: bool = False):
    """
    Fix the given JSON string to make it parseable and fully compliant with two techniques.

    Args:
        json_string (str): The JSON string to fix.

    Returns:
        str: The fixed JSON string
    """
    assistant_reply = assistant_reply.strip()
    if assistant_reply.startswith("```json"):
        assistant_reply = assistant_reply[7:]
    if assistant_reply.endswith("```"):
        assistant_reply = assistant_reply[:-3]
    try:
        return json.loads(assistant_reply,strict=False)  # just check the validity
    except json.JSONDecodeError:  # noqa: E722
        pass

    if assistant_reply.startswith("json "):
        assistant_reply = assistant_reply[5:]
        assistant_reply = assistant_reply.strip()
    try:
        return json.loads(assistant_reply)  # just check the validity
    except json.JSONDecodeError:  # noqa: E722
        pass

    # Parse and print Assistant response
    assistant_reply_json = fix_and_parse_json(assistant_reply)
    # assistant_reply_json = assistant_reply
    if assistant_reply_json == {}:
        assistant_reply_json = attempt_to_fix_json_by_finding_outermost_brackets(
            assistant_reply
        )

    if assistant_reply_json != {}:
        return assistant_reply_json

    if raise_error:
        return json5.loads(assistant_reply)
    else:
        return {}


def attempt_to_fix_json_by_finding_outermost_brackets(json_string: str):
    # if CFG.speak_mode and CFG.debug_mode:
    #     say_text(
    #         "I have received an invalid JSON response from the OpenAI API. "
    #         "Trying to fix it now."
    #     )
    logger.error("Attempting to fix JSON by finding outermost brackets\n")

    try:
        json_pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
        json_match = json_pattern.search(json_string)

        if json_match:
            # Extract the valid JSON object from the string
            json_string = json_match.group(0)
            logger.typewriter_log(
                title="Apparently json was fixed.", title_color=Fore.GREEN
            )
            # if CFG.speak_mode and CFG.debug_mode:
            #     say_text("Apparently json was fixed.")
        else:
            return {}

    except (json.JSONDecodeError, ValueError):
        logger.error(f"Error: Invalid JSON: {json_string}\n")
        # if CFG.speak_mode:
        #     say_text("Didn't work. I will have to ignore this response then.")
        logger.error("Error: Invalid JSON, setting it to empty JSON now.\n")
        json_string = {}

    return fix_and_parse_json(json_string)

def fix_and_parse_json(
    json_to_load: str, try_to_fix_with_gpt: bool = True
):
    """Fix and parse JSON string

    Args:
        json_to_load (str): The JSON string.
        try_to_fix_with_gpt (bool, optional): Try to fix the JSON with GPT.
            Defaults to True.

    Returns:
        str or dict[Any, Any]: The parsed JSON.
    """

    with contextlib.suppress(json.JSONDecodeError):
        json_to_load = json_to_load.replace("\t", "")
        return json.loads(json_to_load)

    with contextlib.suppress(json.JSONDecodeError):
        json_to_load = correct_json(json_to_load)
        return json.loads(json_to_load)
    # Let's do something manually:
    # sometimes GPT responds with something BEFORE the braces:
    # "I'm sorry, I don't understand. Please try again."
    # {"text": "I'm sorry, I don't understand. Please try again.",
    #  "confidence": 0.0}
    # So let's try to find the first brace and then parse the rest
    #  of the string
    try:
        brace_index = json_to_load.index("{")
        maybe_fixed_json = json_to_load[brace_index:]
        last_brace_index = maybe_fixed_json.rindex("}")
        maybe_fixed_json = maybe_fixed_json[: last_brace_index + 1]
        return json.loads(maybe_fixed_json)
    except (json.JSONDecodeError, ValueError) as e:
        # return try_ai_fix(try_to_fix_with_gpt, e, json_to_load)
        return json_to_load
        return "failed"
    
