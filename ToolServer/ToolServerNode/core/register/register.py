import logging
import importlib
import traceback

from copy import deepcopy
from typing import Optional,Callable,Any,Type,Union

from core.base import BaseEnv
from core.labels import ToolLabels,EnvLabels
from core.exceptions import ToolNotFound,EnvNotFound,ToolRegisterError

from config import CONFIG

logger = logging.getLogger(CONFIG['logger'])

def get_func_name(func:Callable,env:BaseEnv=None)->str:
    if env is None or not hasattr(env,'env_labels'):
        if hasattr(func,'tool_labels'):
            return func.tool_labels.name
        else:
            return func.__name__
    else:
        if hasattr(func,'tool_labels'):
            return env.env_labels.name + '_' + func.tool_labels.name
        else:
            return env.env_labels.name + '_' + func.__name__


class ToolRegister:
    def __init__(self,
                 config:dict = {},
                 ):
        self.config = deepcopy(CONFIG)
        for k in config:
            self.config[k] = config[k]
        self.toolregister_cfg = self.config['toolregister']
        self.tool_creation_doc = open(self.toolregister_cfg['tool_creation_doc']).read()
        self.tool_creation_context = {}
        self.tool_creation_context_load_code = []
        for k in self.toolregister_cfg['tool_creation_context']:
            # load
            load_code = f"from {self.toolregister_cfg['tool_creation_context'][k]} import {k}"
            exec(load_code)
            self.tool_creation_context[k] = eval(k)
            self.tool_creation_context_load_code.append(load_code)
        # load modules
        self.tools = {}
        self.envs = {}
        for module_name in ['core.envs','core.tools']:            
            sub_modules = importlib.import_module(module_name).__all__
            for module in sub_modules:
                for attr_name in dir(module):
                    attr = getattr(module,attr_name)
                    self.check_and_register(attr)
            
        # load extensions
        if 'enabled_extensions' in self.config.cfg and isinstance(self.config['enabled_extensions'],list):
            for extension in self.config['enabled_extensions']:
                self.dynamic_extension_load(extension)
        
        logger.info(f'Loaded {len(self.tools)} tools and {len(self.envs)} envs!')
        # print(self.tools)
    def check_and_register(self,attr:Any):
        if hasattr(attr,'tool_labels') and isinstance(attr.tool_labels,ToolLabels):
            tool_name = get_func_name(attr)
            if tool_name in self.tools:
                logger.warning(f'Tool {tool_name} is replicated! The new one will be replaced!')
                return None
            
            self.tools[tool_name] = attr
            logger.info(f'Register tool {tool_name}!')
            return attr
            
        if hasattr(attr,'env_labels') and isinstance(attr.env_labels,EnvLabels):
            # attr is a cls, need get instance
            if attr.env_labels.name in self.envs:
                return
            if not issubclass(attr,BaseEnv):
                raise Exception(f'The env {attr.env_labels.name} is not a subclass of BaseEnv!')
            env = attr(config=self.config.dict())
            env_tools = {}
            
            if self.toolregister_cfg['parent_tools_visible']:
                func_names = env.__get_all_func_name__()
            else:
                func_names = env.__get_defined_func_name__()
            
            for func_name in func_names:
                func = getattr(env,func_name)
                if hasattr(func,'tool_labels'):
                    env_tools[get_func_name(func,env)] = func
            
            env_keys = set(env_tools.keys())
            tools_keys = set(self.tools.keys())
            if env_keys & tools_keys:
                logger.warning(f'Env {env.env_labels.name} has tools with same name as other tools! The new one will be ignored!')
                for tool_name in env_keys & tools_keys:
                    env_tools.pop(tool_name)

            self.tools.update(env_tools)
            
            self.envs[attr.env_labels.name] = env
            logger.info(f'Register env {env.env_labels.name} with {len(env_tools)} tools!')
            
            return env
            
        return None

    def register_tool(self,tool_name:str,code:str)->str:
        try:
            exec(code,self.tool_creation_context)
        except Exception as e:
            error_report =  traceback.format_exc()
            logger.error(error_report)
            raise ToolRegisterError(f'Failed to execute new tool code: {e}\n\n' + error_report,tool_name=tool_name)
        
        try:
            tool_func = eval(tool_name,self.tool_creation_context)
        except:
            raise ToolRegisterError(f'Failed to find tool, please verify the tool_name!',tool_name=tool_name)
        
        tool_func = self.check_and_register(tool_func)
        if tool_func is None:
            raise ToolRegisterError(f'Tool: {tool_name} has no labels or replicated! Ensuring wrap the tool with `@toolwrapper()`.',tool_name=tool_name)
        
        # write the tool into file under extensions/tools
        code = '\n'.join(self.tool_creation_context_load_code) +'\n# Tool Creation Context Load Ended.\n'+ code
        tool_file = f'extensions/tools/{tool_name}.py'
        with open(tool_file,'w') as f:
            f.write(code)
        
        return self.get_tool_dict(tool_name)
    
    def dynamic_extension_load(self,extension:str)->bool:
        '''Load extension dynamically.
        
        :param string extension: The load path of the extension.
        :return boolean: True if success, False if failed.
        '''
        try:
            module = importlib.import_module(extension)
            for attr_name in dir(module):
                attr = getattr(module,attr_name)
                self.check_and_register(attr)
        except Exception as e:
            logger.error(f'Failed to load extension {extension}! Exception: {e}')
            # logger.error(traceback.format_exc())
            return False
        
        return True
        
    def get_tool_dict(self,tool_name:str)->dict:
        return self[tool_name].tool_labels.dict(name_overwrite=tool_name)
    
    def get_env_dict(self,env_name:str)->dict:
        if env_name not in self.envs:
            raise EnvNotFound(env_name=env_name)
        return self.envs[env_name].env_labels.dict(include_invisible=True,max_show_tools = -1)
    
    def get_all_envs(self)->list[dict]:
        return [self.envs[env_name].env_labels.dict()  for env_name in self.envs]
    
    def get_all_tools(self,include_invisible=False)->list[str]:
        if include_invisible:
            return [tool_name  for tool_name in self.tools]
        else:
            return [tool_name  for tool_name in self.tools if self.tools[tool_name].tool_labels.visible]
    
    def get_all_tools_dict(self,include_invisible=False)->list[dict]:
        return [self.tools[tool_name].tool_labels.dict(name_overwrite=tool_name)  for tool_name in self.get_all_tools(include_invisible)]
    
    def __getitem__(self, key)->Callable[..., Any]:
        # two stage index, first find env, then find tool
        if isinstance(key,str):
            if key not in self.tools:
                # check if the tool is a env subtool which not visible
                try:
                    tool_name = key.split('_')
                    env_name = tool_name[0]
                    tool_name = '_'.join(tool_name[1:])
                    return self[env_name,tool_name]
                except:
                    if self.dynamic_extension_load(f'extensions.tools.{key}') and key in self.tools:
                        # try to find tool in unloaded extensions
                        return self.tools[key]
                    else:
                        raise ToolNotFound(tool_name=key)
            return self.tools[key]
        elif isinstance(key,tuple):
            if len(key) != 2:
                raise NotImplementedError(f'Key {key} is not valid!')
            env_name,tool_name = key
            if env_name not in self.envs:
                # try to find env in unloaded extensions
                if self.dynamic_extension_load(f'extensions.envs.{env_name}') and env_name in self.envs:
                    env = self.envs[env_name]
                raise EnvNotFound(env_name=env_name)
            env = self.envs[env_name]
            if tool_name not in env.env_labels.subtools_labels:
                raise ToolNotFound(tool_name=env_name+'_'+tool_name)
            else:
                func = getattr(env,env.env_labels.subtools_labels[tool_name].method.__name__)
                return func
        raise NotImplementedError(f'Key {key} is not valid!')