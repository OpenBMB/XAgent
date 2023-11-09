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
        """Prepare the next try by returning a dictionary
           containing type, next calling event and arguments."""
        return {
            "type":self.type,
            "next_calling":self.next_calling,
            "arguments":self.arguments
        }
    
class ToolNotFound(Exception):
    """Custom exception class that is raised when the tool is not found.
    
    Args:
        *args (object): Variable length argument list.
        tool_name (str): The name of the tool.

    Attributes:
        tool_name (str): The name of the tool.
    """
    def __init__(self, *args: object,tool_name:str=None) -> None:
        super().__init__(*args)
        self.tool_name = tool_name
        
    def __str__(self) -> str:
        """Returns the formatted exception error message with the name of the tool"""
        s = super().__str__()
        if s != '':
            s += f'\nThe tool {self.tool_name} is not found!'
        else:
            s = f'The tool {self.tool_name} is not found!'
        return s 

    
class EnvNotFound(Exception):
    """Custom exception class that is raised when the environment variable is not found.
    
    Args:
        *args (object): Variable length argument list.
        env_name (str): The name of the environment variable.

    Attributes:
        addition_info (tuple): Additional information.
        env_name (str): The name of the environment variable.
    """
    def __init__(self, *args: object,env_name:str=None) -> None:
        super().__init__(*args)
        self.addition_info = args
        self.env_name =  env_name
        
    def __str__(self)->str:
        """Returns the formatted exception error message with the name of the environment variable"""
        s = super().__str__()
        if s != '':
            s += f'\nThe env {self.env_name} is not found!'
        else:
            s = f'The tool {self.env_name} is not found!'
        return s 
    
class ToolRegisterError(Exception):
    """Custom exception class that is raised when registering a tool encounters an error.
    
    Args:
        *args (object): Variable length argument list.
        tool_name (str): The name of the tool.

    Attributes:
        addition_info (tuple): Additional information.
        tool_name (str): The name of the tool.
    """
    def __init__(self, *args: object,tool_name:str=None) -> None:
        super().__init__(*args)
        self.addition_info = args
        self.tool_name = tool_name
        
    def __str__(self)->str:
        """Returns the formatted exception error message with the name of the tool"""
        s = super().__str__()
        if s != '':
            s += f'\nError happens when registering tool {self.tool_name}!'
        else:
            s = f'Error happens when registering tool {self.tool_name}!'
        return s 

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
def remove_color(text):
    """Removes ANSI escape sequences i.e. colors, from the text.

    Args:
        text (str): The text from which color needs to be removed.

    Returns:
        str: The filtered text with no color.
    """

    return ansi_escape.sub('', text)

class ToolExecutionError(HTTPException):
    """Custom exception class that is raised when the tool execution encounters an error.

    Args:
        error_msg (str): The error message during tool execution.
    """
    def __init__(self,error_msg:str):
        if isinstance(error_msg,str):
            error_msg = remove_color(error_msg)
        super().__init__(500,error_msg)