from typing import Callable,Dict,Any
from copy import deepcopy
from config import CONFIG

class BaseEnv:
    def __init__(self,config:Dict[str,Any]={}):
        self.config = deepcopy(CONFIG)
        if isinstance(config,dict):
            self.config.update(config)
        
    @classmethod
    def __get_all_func_name__(cls)->list[str]:
        '''Get all the function names of the class, except the methods start with `_`.'''
        return [name for name in dir(cls) 
        if not str(name).startswith('_') and callable(getattr(cls,name))]


    @classmethod
    def __get_all_func__(cls)->list[Callable]:
        '''Get all functions of the class, except the methods start with `__`.'''
        func_names = cls.__get_all_func_name__()
        return list(map(getattr, [cls]*len(func_names),func_names))

    @classmethod
    def __get_defined_func__(cls)->list[Callable]:
        '''Get all the function of the subclass, except the methods start with `_`.'''
        functions = cls.__get_all_func__()
        for parent_cls in cls.__bases__:
            if not issubclass(parent_cls, BaseEnv):
                continue
            parent_functions = parent_cls.__get_all_func__()
            functions = list(filter(lambda x: x not in parent_functions, functions))
    
        return functions

    @classmethod
    def __get_defined_func_name__(cls)->list[str]:
        '''Get all the function names of the subclass, except the methods start with `_`.'''
        functions = cls.__get_defined_func__()
        return list(map(lambda x: x.__name__, functions))