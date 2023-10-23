import os
import glob
import yaml
import json5

from typing import Optional, Tuple
from colorama import Fore

from XAgent.config import CONFIG
from XAgent.logs import logger
from .request import objgenerator

class FunctionManager:
    def __init__(self,
                 function_cfg_dir=os.path.join(os.path.dirname(__file__),'functions'),
                 pure_function_cfg_dir=os.path.join(os.path.dirname(__file__),'pure_functions'),):
        self.function_cfg_dir = function_cfg_dir
        self.pure_function_cfg_dir = pure_function_cfg_dir
        self.function_cfgs = {}
        
        for cfg_file in glob.glob(os.path.join(self.function_cfg_dir,'*.yaml')) + glob.glob(os.path.join(self.function_cfg_dir,'*.yml')):
            with open(cfg_file,'r') as f:
                function_cfg = yaml.load(f,Loader=yaml.FullLoader)
            self.function_cfgs[function_cfg['function']['name']] = function_cfg

        for cfg_file in glob.glob(os.path.join(self.pure_function_cfg_dir,'*.yaml')) + glob.glob(os.path.join(self.pure_function_cfg_dir,'*.yml')):
            with open(cfg_file,'r') as f:
                function_cfg = yaml.load(f,Loader=yaml.FullLoader)
            for function in function_cfg['functions']:
                self.function_cfgs[function['name']] = function
    
    def get_function_schema(self,function_name:str)->dict|None:
        return self.function_cfgs.get(function_name,None)
    
    def register_function(self,function_schema:dict):
        if function_schema['name'] in self.function_cfgs:
            return
        self.function_cfgs[function_schema['name']] = function_schema
        
    def execute(self,function_name:str,return_generation_usage:bool=False,function_cfg:dict=None,**kwargs,)->Tuple[dict,Optional[dict]]:
        if function_cfg is None and function_name in self.function_cfgs:
            function_cfg = self.function_cfgs.get(function_name)
        else:
            raise KeyError(f'Configure for function {function_name} not found.')
        
        
        logger.typewriter_log(f'Executing AI Function: {function_name}', Fore.YELLOW)

        completions_kwargs:dict = function_cfg.get('completions_kwargs',CONFIG.default_completion_kwargs)
        function_prompt = str(function_cfg['function_prompt'])
        function_prompt = function_prompt.format(**kwargs)
        messages = [{'role':'user','content':function_prompt}]
        
        match CONFIG.default_request_type:
            case 'openai':                
                response = objgenerator.chatcompletion(
                    messages=messages,
                    functions=[function_cfg['function']],
                    function_call={'name':function_cfg['function']['name']},
                    **completions_kwargs
                )
                returns = json5.loads(response['choices'][0]['message']['function_call']['arguments'])
            case 'xagent':
                arguments = function_cfg['function']['parameters']
                response = objgenerator.chatcompletion(
                    messages=messages,
                    arguments=arguments,
                    **completions_kwargs
                )
                returns = json5.loads(response['choices'][0]['message']['content'])['arguments']
        
        if return_generation_usage:
            return returns, response['usage']
        return returns
    
    def __getitem__(self,function_name,return_generation_usage=False,**kwargs):
        return self.execute(function_name,return_generation_usage,**kwargs)
    def __call__(self, function_name,return_generation_usage=False,**kwargs):
        return self.execute(function_name,return_generation_usage,**kwargs)

function_manager = FunctionManager()