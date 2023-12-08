from typing import Callable, Dict, Any
from copy import deepcopy
from config import CONFIG

class BaseEnv:
    """
    BaseEnv class. It helps to handle functions and function names of the classes and subclasses.
    This class provides methods to get all functions, defined functions and their names.
    It also ensures the configuration updates if necessary.

    Attributes:
        config(Dict[str, Any], optional): A dictionary containing the configuration. Defaults to an empty dictionary.
    """
    def __init__(self, config: Dict[str, Any] = {}):
        """Initialize BaseEnv class with specified or default configuration.

        Args:
            config (Dict[str, Any], optional): A dictionary containing the configuration. Defaults to an empty dictionary.

        Notes:
            The configuration is deep copied to avoid modifications to the original object.
        """
        self.config = deepcopy(CONFIG)
        if isinstance(config, dict):
            self.config.update(config)
        
    @classmethod
    def __get_all_func_name__(cls) -> list[str]:
        """Get all the function names of the class, excluding methods starting with '_' character.

        Returns:
            list[str]: A list that contains function names.
        """
        return [name for name in dir(cls) 
        if not str(name).startswith('_') and callable(getattr(cls, name))]


    @classmethod
    def __get_all_func__(cls) -> list[Callable]:
        """Get all functions of the class, excluding methods starting with '__' characters.

        Returns:
            list[Callable]: A list that contains functions.
        """
        func_names = cls.__get_all_func_name__()
        return list(map(getattr, [cls]*len(func_names), func_names))

    @classmethod
    def __get_defined_func__(cls) -> list[Callable]:
        """Get all the functions of the subclass, excluding methods starting with '_' character.

        Returns:
            list[Callable]: A list that contains defined functions of the subclass.

        Notes:
            This method removes the parent class's methods from the functions list to 
            provide only the functions that are newly defined in the subclass.
        """
        functions = cls.__get_all_func__()
        for parent_cls in cls.__bases__:
            if not issubclass(parent_cls, BaseEnv):
                continue
            parent_functions = parent_cls.__get_all_func__()
            functions = list(filter(lambda x: x not in parent_functions, functions))
    
        return functions

    @classmethod
    def __get_defined_func_name__(cls) -> list[str]:
        """Get all the function names of the subclass, excluding methods starting with '_' character.

        Returns:
            list[str]: A list that contains function names of the subclass.
        """
        functions = cls.__get_defined_func__()
        return list(map(lambda x: x.__name__, functions))