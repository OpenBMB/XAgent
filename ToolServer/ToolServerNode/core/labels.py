from typing import Optional,Callable,Any,Type,Union
from config import CONFIG

class ToolLabels:
    """A class representing a tool.

    Attributes:
        name (str): The name of the tool.
        description (str): A brief description of what the tool does.
        signature (str): The signature of the function that the tool executes. Defaults to None.
    """

    def __init__(
        self,
        name: str,
        description: str,
        method: Callable[..., Any],
        signature: dict = {},
        required:list = [],
        enabled: bool  = True,
        disabled_reason: Optional[str] = None,
        func_type:str = 'function',
        visible:bool = True,
    ):
        self.name = name
        self.description = description
        self.method = method
        self.signature = signature
        self.required = required
        self.enabled = enabled
        self.disabled_reason = disabled_reason
        self.func_type = func_type
        self.visible = visible
    
    def dict(self,name_overwrite:str='') -> dict:
        return {
            "name": self.name if name_overwrite=='' else name_overwrite,
            "description": self.description[:1024],
            "parameters": {
                "type": "object",
                "properties": self.signature,
                "required":self.required
            }
        }

    def __str__(self) -> str:
        return f"{self.name}: {self.description}, args: {self.signature}"
    
class EnvLabels:
    """A class representing a env.
    """
    def __init__(
        self,
        name: str,
        description: str,
        subtools_labels: dict[ToolLabels] = {},
        defined_tools:list[str] = [],
        cls: Type = None,
        enabled: bool  = True,
        disabled_reason: Optional[str] = None,
        visible:bool = True,
    ):
        self.name = name
        self.description = description
        self.subtools_labels = subtools_labels
        self.defined_tools = defined_tools
        self.cls = cls
        self.enabled = enabled
        self.disabled_reason = disabled_reason
        self.visible = visible
        
        
    
    def dict(self,
             include_invisible=False,
             max_show_tools:int=CONFIG['toolregister']['env_max_tools_display']) -> dict:
        if include_invisible:
            tools_name = list(self.subtools_labels.keys())
        else:
            if CONFIG['toolregister']['parent_tools_visible']:
                tools_name = [tool_name for tool_name in self.subtools_labels.keys() if self.subtools_labels[tool_name].visible]
            else:
                tools_name = self.defined_tools
        
        if max_show_tools != -1 and len(tools_name) > max_show_tools:
            # only show first max_show_tools tools
            tools_name = tools_name[:max_show_tools]
            tools_name.append('...')
        
        return {
            "name": self.name,
            "description": self.description,
            "total_tools": len(self.subtools_labels),
            "tools": tools_name,
        }

    def __str__(self)->str:
        return f"{self.name}: {self.description}"