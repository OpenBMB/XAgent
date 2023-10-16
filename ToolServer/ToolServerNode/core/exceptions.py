import re
from fastapi import HTTPException

class OutputNotReady(Exception):
    """The output is not ready.
    """
    def __init__(self, *args: object,type:str='retry',next_calling:str=None,arguments:dict={}) -> None:
        super().__init__(*args)
        self.type = type
        self.next_calling = next_calling
        self.arguments = arguments
        
        
    def next_try(self):
        return {
            "type":self.type,
            "next_calling":self.next_calling,
            "arguments":self.arguments
        }
    
class ToolNotFound(Exception):
    """The tool is not found.
    """
    def __init__(self, *args: object,tool_name:str=None) -> None:
        super().__init__(*args)
        self.tool_name = tool_name
        
    def __str__(self) -> str:
        s = super().__str__()
        if s != '':
            s += f'\nThe tool {self.tool_name} is not found!'
        else:
            s = f'The tool {self.tool_name} is not found!'
        return s 

    
class EnvNotFound(Exception):
    """The env is not found.
    """
    def __init__(self, *args: object,env_name:str=None) -> None:
        super().__init__(*args)
        self.addition_info = args
        self.env_name =  env_name
        
    def __str__(self)->str:
        s = super().__str__()
        if s != '':
            s += f'\nThe env {self.env_name} is not found!'
        else:
            s = f'The tool {self.env_name} is not found!'
        return s 
    
class ToolRegisterError(Exception):
    """Error happens when registering a tool.
    """
    def __init__(self, *args: object,tool_name:str=None) -> None:
        super().__init__(*args)
        self.addition_info = args
        self.tool_name = tool_name
        
    def __str__(self)->str:
        s = super().__str__()
        if s != '':
            s += f'\nError happens when registering tool {self.tool_name}!'
        else:
            s = f'Error happens when registering tool {self.tool_name}!'
        return s 

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
def remove_color(text):
    return ansi_escape.sub('', text)
class ToolExecutionError(HTTPException):
    def __init__(self,error_msg:str):
        if isinstance(error_msg,str):
            error_msg = remove_color(error_msg)
        super().__init__(500,error_msg)