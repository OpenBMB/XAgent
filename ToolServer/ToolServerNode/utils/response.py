import base64
from typing import Callable,Dict,Any

from config import logger

def is_base64(s:str) -> bool:
    """
    Check if the given string is a base64 sting or not.

    Args:
        s (str): the string to be checked.

    Returns:
        bool: Returns True if the given string is a base64 string, False otherwise.
    """
    try:
        base64.b64decode(s)
        return True
    except:
        return False

def is_wrapped_response(obj:dict) -> bool:
    """
    Check if the dictionary object is a wrapped response.
    A dictionary is considered as wrapped response if it has 'type' and 'data' keys,
    and value of 'type' key is one of ['simple','composite','binary'].

    Args:
        obj (dict): the dictionary object to be checked.

    Returns:
        bool: Returns True if the dictionary is a wrapped response, False otherwise.
    """
    if 'type' in obj and obj['type'] in ['simple','composite','binary'] and 'data' in obj:
        return True
    return False

def wrap_tool_response(obj:Any) -> dict|list|str|int|float|bool:
    """
    Wrap the tool response in a standardized object structure (depending on its type) to allow decoding.
    
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
    Standardized Structures:
    - For simple data types (str, int, float, bool), the object is directly returned.
    - For composite types (tuples), data is wrapped in an object with a composite type.
    - For binary data, data is base64 encoded and wrapped in an object with a binary type.
     

    Args:
        obj (Any): any Python object that needs to be wrapped.

    Returns:
        Union[dict, list, str, int, float, bool]: the wrapped response.
        
    Raises:
        logger.warning: raises warning if the type of 'obj' is unknown.
    """
    if isinstance(obj,tuple):
        if len(obj) == 0:
            ret = {
                'type': 'simple',
                'data': None
            }
        elif len(obj) == 1:
            ret = {
                'type': 'simple',
                'data': obj[0]
            }
        else:
            ret = {
                'type': 'composite',
                'data': []
            }
            for o in obj:
                ret['data'].append(wrap_tool_response(o))
    elif isinstance(obj,bytes):
        ret = {
            'type': 'binary',
            'media_type': 'bytes',
            'name': None,
            'data': base64.b64encode(obj).decode()
        }
    elif isinstance(obj,(str,int,float,bool,list)) or obj is None:
        ret = obj
    elif isinstance(obj,dict):
        # check if already wrapped
        if is_wrapped_response(obj):
            ret = obj
        else:
            ret = {
                'type': 'simple',
                'data': obj
            }
    else:
        logger.warning(f'Unknown type {type(obj)} in wrap_tool_response')
        ret = {
            'type': 'simple',
            'data': obj
        }
    return ret