import os
import glob
import yaml
import json5

from typing import Optional, Tuple
from colorama import Fore

from XAgent.config import CONFIG,get_apiconfig_by_model
from XAgent.logs import logger
from .request import objgenerator

class FunctionManager:
    """
    This class provides methods to manage functions including registration and execution of functions.
    The functions are defined and loaded from YAML configuration files located in the local directory
    under subdirectories 'functions' and 'pure_functions'.

    Attributes:
      function_cfg_dir (str): The directory path where the function configuration files are located.
      pure_function_cfg_dir (str): The directory path where the pure function configuration files are located.
      function_cfgs (dict): A dictionary to store all loaded function configurations.
    """

    def __init__(self,
                 function_cfg_dir=os.path.join(os.path.dirname(__file__),'functions'),
                 pure_function_cfg_dir=os.path.join(os.path.dirname(__file__),'pure_functions'),):
        """
        Initializes the FunctionManager class with given directories for function configuration files.

        Args:
            function_cfg_dir (str): The directory path where the function configuration files are located.
            pure_function_cfg_dir (str): The directory path where the pure function configuration files are located.
        """
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
        """
        Gets the schema of the function by its name.

        Args:
            function_name (str): The name of the function.

        Returns:
            dict: The schema of the function if found.
            None: If the function is not found.
        """
        return self.function_cfgs.get(function_name,None)
    
    def register_function(self,function_schema:dict):
        """
        Registers a new function with its schema.

        Args:
            function_schema (dict): The schema of the function to register.
        """
        if function_schema['name'] in self.function_cfgs:
            return
        self.function_cfgs[function_schema['name']] = function_schema
        
    def execute(self,function_name:str,return_generation_usage:bool=False,function_cfg:dict=None,**kwargs,)->Tuple[dict,Optional[dict]]:
        """
        Executes a function by its name.

        Args:
            function_name (str): The name of the function to execute.
            return_generation_usage (bool, optional): If set to True, also returns the usage of the function execution.
            function_cfg (dict, optional): The configuration of the function. If not provided, retrieves it from the loaded functions.
            **kwargs: The parameters of the function to execute.

        Returns:
            Tuple[dict,Optional[dict]]: A tuple containing the returns and optionally the usage of the executed function.

        Raises:
            KeyError: If the function configuration is not found.
        """
        if function_cfg is None and function_name in self.function_cfgs:
            function_cfg = self.function_cfgs.get(function_name)
        else:
            raise KeyError(f'Configure for function {function_name} not found.')
        
        
        logger.typewriter_log(f'Executing AI Function: {function_name}', Fore.YELLOW)

        completions_kwargs:dict = function_cfg.get('completions_kwargs',{})
        if 'model' in completions_kwargs:
            # check whether model is configured
            try:
                get_apiconfig_by_model(completions_kwargs['model'])
            except:
                logger.typewriter_log("Fallback",Fore.YELLOW,f"Model {completions_kwargs['model']} is not configured. Using default model instead.")
                completions_kwargs = {}
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
        """
        Allows the FunctionManager instance to behave like a dictionary, calling the execute method by key (which is actually the function name).

        Args:
            function_name (str): The name of the function to execute.
            return_generation_usage (bool, optional): If set to True, also returns the usage of the function execution.
            **kwargs: The parameters of the function to execute.

        Returns:
            The return of the execute method.
        """
        return self.execute(function_name,return_generation_usage,**kwargs)

    def __call__(self, function_name,return_generation_usage=False,**kwargs):
        """
        Allows the FunctionManager instance to be callable, calling the execute method directly.

        Args:
            function_name (str): The name of the function to execute.
            return_generation_usage (bool, optional): If set to True, also returns the usage of the function execution.
            **kwargs: The parameters of the function to execute.

        Returns:
          The return of the execute method.
        """
        return self.execute(function_name,return_generation_usage,**kwargs)

function_manager = FunctionManager()