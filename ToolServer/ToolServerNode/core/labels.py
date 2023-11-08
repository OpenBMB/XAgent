from typing import Optional,Callable,Any,Type,Union
from config import CONFIG


class ToolLabels:
    """A class representing a tool.

    When invoked, this object runs the associated method using parameters defined in the signature.

    Attributes:
        name (str): The name of the tool.
        description (str): Description of the tool.
        method (Callable): The function/method that the tool executes.
        signature (dict): Argument keys and values needed by the method to execute.
        required (list): List of required arguments for the method.
        enabled (bool): Flag indicating whether the tool is enabled or not.
        disabled_reason (str): Reason for disabling the tool, if applicable.
        func_type (str): Type of function for the tool, defaults to 'function'.
        visible (bool): Flag indicating whether the tool is visible or not.
    """

    def __init__(
        self,
        name: str,
        description: str,
        method: Callable[..., Any],
        signature: dict = {},
        required: list = [],
        enabled: bool = True,
        disabled_reason: Optional[str] = None,
        func_type: str = 'function',
        visible: bool = True,
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

    def dict(self, name_overwrite: str = '') -> dict:
        """Returns the tool information as a dictionary.

        Args:
            name_overwrite (str): Replacement string for tool name, defaults to empty string.

        Returns:
            dict: Dictionary of tool attributes.
        """
        
        return {
            "name": self.name if name_overwrite == '' else name_overwrite,
            "description": self.description[:1024],
            "parameters": {
                "type": "object",
                "properties": self.signature,
                "required": self.required
            }
        }

    def __str__(self) -> str:
        """Returns the tool information in a formatted string.

        Returns:
            str: Formatted string containing tool attributes.
        """
        return f"{self.name}: {self.description}, args: {self.signature}"


class EnvLabels:
    """A class representing an environment.

    Each environment has a set of subtools associated with it. This object manages the collection of tools.

    Attributes:
        name (str): Name of the environment.
        description (str): Description of the environment.
        subtools_labels (dict): Collection of tools associated to the environment.
        defined_tools (list): List of tool names defined in the environment.
        cls (Type): Class that the environment pertains to.
        enabled (bool): Flag indicating whether the environment is enabled or not.
        disabled_reason (str): Reason for disabling the environment, if applicable.
        visible (bool): Flag indicating whether the environment is visible or not.
    """

    def __init__(
        self,
        name: str,
        description: str,
        subtools_labels: dict[ToolLabels] = {},
        defined_tools:list[str] = [],
        cls: Type = None,
        enabled: bool = True,
        disabled_reason: Optional[str] = None,
        visible: bool = True,
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
             max_show_tools: int = CONFIG['toolregister']['env_max_tools_display']) -> dict:
        """
        Returns the environment's tools as a dictionary.

        Args:
            include_invisible (bool): If true, includes tools even if they're set as invisible.
            max_show_tools (int): Maximum number of tools to display in the output.

        Returns:
            dict: Dictionary of environment attributes and associated tools.
        """
        
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

    def __str__(self) -> str:
        """Returns the environment information as a formatted string.

        Returns:
            str: Formatted string containing environment attributes.
        """
        return f"{self.name}: {self.description}"