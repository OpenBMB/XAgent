#!/usr/bin/env python
# encoding: utf-8
import json
import os
import orjson
from io import StringIO
from ruamel import yaml

folded = yaml.scalarstring.FoldedScalarString
literal = yaml.scalarstring.LiteralScalarString

yaml_obj = yaml.YAML()
yaml_obj.width = 1000000


B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
BOS, EOS = "<s>", "</s>"

# custom yaml dump
def custom_yaml_dump(item):
    if item is None:
        return item
    elif isinstance(item, dict):
        data = {}
        for key, value in item.items():
            data[key] = custom_yaml_dump(value)
        return data
    elif isinstance(item, str) and '\n' in item:
        return literal(item)
    else:
        return item


def yaml_load(string):
    f = StringIO(string)
    data = yaml_obj.load(f)
    return data


def yaml_dump(item):
    f = StringIO()
    item = custom_yaml_dump(item)
    yaml_obj.dump(item, f)
    f.seek(0)
    string = f.read()
    return string


def message_format(msg):
    """https://github.com/facebookresearch/llama/blob/main/llama/generation.py#L343"""
    if msg["role"] == "user":
        string = f"{BOS}{B_INST} {msg['content'].strip()} {E_INST} "
    elif msg["role"] == "assistant":
        string = f"{msg['content'].strip()}{EOS}"
    else:
        raise NotImplementedError
    return string


def merge_messages(messages):
    new_messages = []
    pre_role = ""
    for msg in messages:
        # system message should be merged with user message
        # reference: https://github.com/facebookresearch/llama/blob/main/llama/generation.py#L324
        if msg['role'] == 'system':
            role = 'user'
            content = B_SYS + msg["content"] + E_SYS
        else:
            role = msg['role']
            content = msg['content']

        if role == pre_role:
            new_messages[-1]["content"] += "\n" + content
        else:
            new_messages.append({'role': role, 'content': content})
        pre_role = role
    return new_messages


def find_system_msg(messages):
    idx = -1
    for i, msg in enumerate(messages):
        if msg["role"] == "system":
            idx = i
    return idx


def my_dump(item, dump_method):
    item = json_try(item)
    if dump_method == 'yaml':
        return yaml_dump(item)
    elif dump_method == 'json':
        return json.dumps(item, ensure_ascii=False)
    else:
        raise NotImplementedError


def json_try(item):
    if isinstance(item, str):
        try:
            x = json.loads(item)
            if not isinstance(x, str):
                return json_try(x)
            else:
                return x
        except:
            return item
    elif isinstance(item, dict):
        data = {}
        for key, value in item.items():
            data[key] = json_try(value)
        return data if len(data) > 0 else None
    elif isinstance(item, list):
        data = []
        for x in item:
            data.append(json_try(x))
        return data if len(data) > 0 else None
    else:
        return item


def my_load(string, dump_method):
    if dump_method == 'yaml':
        return yaml_load(string)
    elif dump_method == 'json':
        return json.loads(string)
    else:
        raise NotImplementedError


def format(item, dump_method='yaml'):
    """
    reformat the request item
    item: {"messages": ..., "arguments": ..., "functions": ..., "function_call": ...}
    """
    if "arguments" in item and item['arguments'] is not None and len(item['arguments']) > 0:
        arguments_string = "# Global Arguments\n" + my_dump(item["arguments"], "yaml")
    else:
        arguments_string = ""
    if "functions" in item and item['functions'] is not None and len(item['functions']) > 0:
        functions_string = "# Functions\n" + my_dump(item["functions"], "yaml")
    else:
        functions_string = ""
    if "function_call" in item and item['function_call'] is not None and 'name' in item['function_call']:
        function_call_string = f"You need to use {item['function_call']['name']} function."
    else:
        function_call_string = ""
    system_prefix = (
        "Response with following json schemas:\n" +
        f"{arguments_string}\n{functions_string}\n{function_call_string}"
    )
    system_prefix = system_prefix.strip()

    dialog = item["messages"]
    sys_msg_idx = find_system_msg(dialog)
    if sys_msg_idx == -1:
        dialog.insert(0, {"role": "system", "content": system_prefix})
    else:
        dialog[sys_msg_idx]["content"] += "\n" + system_prefix

    dialog = merge_messages(dialog)
    input_string = "".join([message_format(msg) for msg in dialog])
    return input_string


