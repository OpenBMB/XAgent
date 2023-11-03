import base64
from typing import Callable, Dict, Any

from config import logger


def is_base64(s: str) -> bool:
    try:
        base64.b64decode(s)
        return True
    except:
        return False


def is_wrapped_response(obj: dict) -> bool:
    if (
        "type" in obj
        and obj["type"] in ["simple", "composite", "binary"]
        and "data" in obj
    ):
        return True
    return False


def wrap_tool_response(obj: Any) -> dict | list | str | int | float | bool:
    """Wrap the response of tool to allow decoding.

    Format
    ======
    ```
    {
        'type': 'simple',       # for single return value like python basic types
        'data': obj
    },
    {
        'type': 'binary',       # for single return value like python basic types
        'media_type':'image/png',   # or other media types
        'name': 'xxx',             # file name of the binary data
        'data': obj             # base64 encoded binary data
    },
    str,int,float,bool,list is directly returned
    or
    {
        'type': 'composite',    # for multiple return values
        'data': [
            {
                'type': 'simple',
                'data': obj1
            },
            {
                'type': 'simple',
                'data': obj2
            }
        ]
    }
    ```
    """
    if isinstance(obj, tuple):
        if len(obj) == 0:
            ret = {"type": "simple", "data": None}
        elif len(obj) == 1:
            ret = {"type": "simple", "data": obj[0]}
        else:
            ret = {"type": "composite", "data": []}
            for o in obj:
                ret["data"].append(wrap_tool_response(o))
    elif isinstance(obj, bytes):
        ret = {
            "type": "binary",
            "media_type": "bytes",
            "name": None,
            "data": base64.b64encode(obj).decode(),
        }
    elif isinstance(obj, (str, int, float, bool, list)) or obj is None:
        ret = obj
    elif isinstance(obj, dict):
        # check if already wrapped
        if is_wrapped_response(obj):
            ret = obj
        else:
            ret = {"type": "simple", "data": obj}
    else:
        logger.warning(f"Unknown type {type(obj)} in wrap_tool_response")
        ret = {"type": "simple", "data": obj}
    return ret
