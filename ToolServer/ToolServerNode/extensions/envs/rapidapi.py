import os
import json
import httpx

from typing import Type
from copy import deepcopy
from config import CONFIG
from core.base import BaseEnv
from core.register import toolwrapper
from utils.retriever import standardizing

API_INFOS = {}

def generate_arg_doc(arg_name,arg_type,arg_desc,arg_default=None,arg_optional=None):
    """
    Generates argument documentation with type, name, description and default value.

    Args:
        arg_name (str): Argument name.
        arg_type (str): Argument type.
        arg_desc (str): Argument description.
        arg_default (str, optional): Default value of the argument. Defaults to None.
        arg_optional (bool, optional): Whether the argument is optional. Defaults to None.

    Returns:
        str: Formatted argument documentation.
    """
    match arg_type:
        case 'NUMBER':
            arg_type = 'integer'
        case 'STRING':
            arg_type = 'string'
        case 'BOOLEAN':
            arg_type = 'boolean'
        case 'ARRAY':
            arg_type = 'array'
        case 'OBJECT':
            arg_type = 'object'

    if arg_optional:
        arg_type += '?'
    if arg_default:
        return f':param {arg_type} {arg_name}: {arg_desc} defaults to {arg_default}'
    else:
        return f':param {arg_type} {arg_name}: {arg_desc}'

def convert_rapidapi_desc_to_code(rapidapi_desc:dict)->list[dict]:
    """
    Converts the rapidAPI description to a list of dictionaries.

    Args:
        rapidapi_desc (dict): The rapidAPI description in dictionary format.

    Returns:
        list[dict]: A list of dictionaries containing API information.
    """
    tool_desc = {
        'category':rapidapi_desc['category'],
        'tool_name':standardizing(rapidapi_desc['tool_name']),
    }
    api_infos = {}
    for api_desc in rapidapi_desc['api_list']:
        api_name = standardizing(api_desc['name'])
        if api_name in ['from','class','return','false','true','id','and']:
            api_name = 'is_'+ api_name
        api_info = {'api_name':api_name}
        api_info.update(tool_desc)
        
        api_uri = '_'.join(['rapi',tool_desc['tool_name'],api_name])
        
        
        args_doc = []
        
        for param in api_desc['required_parameters']:
            args_doc.append(generate_arg_doc(
                param['name'],
                param['type'],
                param['description'],
                param['default'] if 'default' in param else None,
                ))
        
        for param in api_desc['optional_parameters']:
            args_doc.append(generate_arg_doc(
                param['name'],
                param['type'],
                param['description'],
                param['default'] if 'default' in param else None,
                True))
        
        args_doc = '\n    '.join(args_doc)
        code = f"""async def {api_uri}(self,*args,**kwargs):
    '''{rapidapi_desc['tool_description']}
    {api_info['description'] if 'description' in api_info else ''}
    

    {args_doc}
    '''
    return await self._request_rapid_api('{api_uri}',kwargs)
        """
        api_info['code'] = code
        
        api_infos[api_uri] = api_info
    return api_infos

def rapid_api_mapper(cls:Type):
    """
    Dynamically adds API functions to RapidAPIENnv. 
    
    Args:
        cls (Type): Class of RapidAPIENnv.
    
    Returns:
        Type: Updated class with added API functions.
    
    Raises:
        FileNotFoundError: If both api_infos_json and api_raw_json are not found.
    """
    #reading api list
    if not os.path.exists(CONFIG['rapidapi']['api_infos_json']):
        try:
            api_list = json.load(open(CONFIG['rapidapi']['api_raw_json']))
        except:
            raise FileNotFoundError(f'Both api_infos_json and api_raw_json are not found! Failed to setup RapidAPIEnv!')
        
        for rapidapi_desc in api_list:
            API_INFOS.update(convert_rapidapi_desc_to_code(rapidapi_desc))
        
        json.dump(API_INFOS,open(CONFIG['rapidapi']['api_infos_json'],'w'),indent=4)
    else:
        API_INFOS.update(json.load(open(CONFIG['rapidapi']['api_infos_json'])))
    
    for api_uri,api_info in API_INFOS.items():
        exec(api_info['code'])
        setattr(cls,api_uri,eval(api_uri))
    
    return cls


@toolwrapper(visible=False)
@rapid_api_mapper
class RapidAPIEnv(BaseEnv):
    """
    Class that delivers rapidAPI for tool server.

    Attributes:
        api_infos (dict): Contains the information related to different APIs.
    """
    
    def __init__(self,config:dict={}):
        """
        Constructor for RapidAPIEnv class.

        Args:
            config (dict, optional): Configurations for the RapidAPIEnv. Defaults to {}.
        """
        super().__init__(config=config)
        
        self.rapidapi_cfg = self.config['rapidapi']
        self.api_key = self.rapidapi_cfg['api_key']
        self.endpoint = self.rapidapi_cfg['endpoint']
        
        self.api_infos = deepcopy(API_INFOS)
        
    async def _request_rapid_api(self,api_uri:str,arguments:dict={}):
        """
        Sends a request to the rapidAPI using the provided parameters and API URI.

        Args:
            api_uri (str): The API URI for the specific rapidAPI service.
            arguments (dict, optional): Arguments to be used in the API call. Defaults to {}.

        Returns:
            dict: Response from the rapidAPI service in dictionary format.

        Raises:
            HTTPError: If the response from the server has an error.
        """
        api_info = self.api_infos[api_uri]
        payload = {
            'category':api_info['category'],
            'tool_name':api_info['tool_name'],
            'api_name':api_info['api_name'],
            'tool_input':arguments,
            'strip':'truncate',
            'toolbench_key':self.api_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.endpoint,json=payload,headers={'toolbench_key':self.api_key})
        
        response.raise_for_status()
        
        return response.json()