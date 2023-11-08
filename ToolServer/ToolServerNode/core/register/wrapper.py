import logging
import inspect
import docstring_parser

from typing import Optional,Callable,Any,Type,Union

from core.base import BaseEnv
from core.labels import ToolLabels,EnvLabels

from config import CONFIG

logger = logging.getLogger(CONFIG['logger'])

def generate_tool_labels(
    name: str = None,
    enabled: bool = True,
    disabled_reason: Optional[str] = None,
    func: Callable[..., Any] = None,
    visible:bool = True,
)->Union[ToolLabels,None]:
    """
    Generate and return tool labels for the provided function. If the tool is not enabled,
    then a debug log message is printed and None is returned.

    Args:
        name (str, optional): The name of the tool. If it's not specified, the function's name is used.
        enabled (bool, optional): Determines if the tool is enabled or not. Defaults to True.
        disabled_reason (Optional[str], optional): The reason why the tool is disabled. Defaults to None.
        func (Callable[..., Any], optional): The function for which the tool labels are generated. Defaults to None.
        visible(bool, optional): The visibility status of the tool. Defaults to True.

    Returns:
        Union[ToolLabels,None]: A ToolLabels object containing tool information or None if tool is not enabled. 
    """

    if not enabled:
        if disabled_reason is not None:
            logger.debug(f"tool '{func.__name__}' is disabled: {disabled_reason}")
        return None

    # check if the method have full annotations
    auto_signature = {}
    func_desc =  docstring_parser.parse(func.__doc__)
    required = []
    for arg in func_desc.params:
        auto_signature[arg.arg_name] = {
            'type':arg.type_name,           # TODO support self defined type
            'description':arg.description,
        }
        if arg.default is not None:
            auto_signature[arg.arg_name]['default'] = arg.default
        if not arg.is_optional:
            required.append(arg.arg_name)

    # for arg in inspect.getargs(func.__code__).args:
    #     if arg in auto_signature:
    #         continue
    #     if arg in ['self','cls','config','return']:
    #         continue
    #     # if arg not in func.__annotations__:
    #     #     raise SyntaxError(f'Signature is None and the annotation of varable {arg} in func {func.__name__} is not found!')
    #     auto_signature[arg] = {
    #         'type':'string',
    #         'description':''                # TODO try to generate description
    #     }

    tool_name = func.__name__ if name is None else name
    description = ''
    if func_desc.short_description is not None:
        description = func_desc.short_description
    if func_desc.long_description is not None:
        description += '\n' + func_desc.long_description

    return ToolLabels(
        name=tool_name,
        description=description,
        method=func,
        signature=auto_signature,
        required=required,
        enabled=enabled,
        disabled_reason=disabled_reason,
        visible=visible,
    )

def toolwrapper(
    name: str = None,
    enabled: bool = True,
    disabled_reason: Optional[str] = None,
    parent_tools_visible: bool = CONFIG['toolregister']['parent_tools_visible'],
    visible:bool = True,
)->Union[Type,Callable[..., Any]]:
    """The tool decorator for class, used to create tool objects from ordinary class."""

    def decorator(obj:object)->Union[Type,Callable[..., Any]]:
        if inspect.isclass(obj):
            cls = obj
            cls_name = name if name is not None else cls.__name__
            if not issubclass(cls,BaseEnv):
                raise Exception(f'The class {cls} is not a subclass of BaseEnv!')
            
            description = cls.__doc__ if cls.__doc__ is not None else ''
            if not visible:
                description = 'Note: All tools of this env are invisible during all tools display, please check this env\'s defination to show all tools.\n' + description
            
            
            subtools_labels = {}
            if BaseEnv not in cls.__bases__:
                direct_parents = [parent.__name__ for parent in cls.__bases__]
                if not parent_tools_visible:
                    description = f'Note: This env is subclass of {direct_parents}, and all tools of parent envs are inherited and not visible. You can try call parent tools or check this env\'s defination to show them.\n' + description
                else:
                    description = f'Note: This env is subclass of {direct_parents}, and all tools of parent envs are inherited.\n' + description
                for parent in cls.__bases__:
                    if hasattr(parent,'env_labels') and isinstance(parent.env_labels,EnvLabels):
                        subtools_labels.update(parent.env_labels.subtools_labels)
            
            cls_func_names = cls.__get_defined_func_name__()            
            for func_name in cls_func_names:
                origin_func = getattr(cls,func_name)
                tool_labels = generate_tool_labels(
                    name=func_name,
                    enabled=enabled,
                    disabled_reason=disabled_reason,
                    func=origin_func,
                    visible=visible)
                if tool_labels is None:
                    continue
                
                # label classmethod, staticmethod and instance method
                #check if the function is a classmethod
                if inspect.ismethod(origin_func) and not inspect.isfunction(origin_func):
                    tool_labels.func_type = 'classmethod'
                # check if the function is a staticmethod
                if 'self' in inspect.getargs(origin_func.__code__).args:
                    tool_labels.func_type = 'instancemethod'
                else:   
                    tool_labels.func_type = 'staticmethod'
                
                # tool_labels.dependent_cls = cls
                origin_func.tool_labels = tool_labels
                subtools_labels[tool_labels.name] = tool_labels
            

            cls.env_labels = EnvLabels(
                name=cls_name,
                description=description,
                subtools_labels=subtools_labels,
                defined_tools=cls_func_names,
                cls=cls,
                enabled=enabled,
                disabled_reason=disabled_reason,
                visible=visible
            )
            return cls
        elif inspect.isfunction(obj):
            func = obj
            tool_labels = generate_tool_labels(
                name=name,
                enabled=enabled, 
                disabled_reason=disabled_reason,
                func=func,
                visible=visible)
            func.tool_labels = tool_labels
            return func
        else:
            raise NotImplementedError(f'Object with type {type(obj)} not recognized!')
    return decorator
