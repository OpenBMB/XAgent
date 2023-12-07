# In this project, you need to follow the rules and precautions below to build new tools

## Tool Path Division

In XAgent, you will find two tool directories, `ToolServer/ToolServerNode/core/tools` and `ToolServer/ToolServerNode/extensions/tools`. These two directories are used to store core tools and extension tools respectively. Core tools are tools that must exist in the project. They provide the basic functions of the application and therefore cannot be removed or disabled. The tools in the `ToolServerNode/extensions/tools` directory are used to extend the functionality of the application. These tools provide some additional, optional functionality that can be added or removed as needed. We separate these two types of tools to make the structure of the application clearer and easier to manage and maintain.

## Difference between envs and tools

In the `extensions` or `core` directory, the `envs` and `tools` subdirectories are usually used to store different types of extension modules. The Python files in the `envs` directory usually define some environment classes, which inherit from the `BaseEnv` class and are used to describe and manage a specific runtime environment. For example, an **environment class** may describe a database environment, including how to connect to a database, how to query data, etc. The Python files in the `tools` directory usually define some tool functions, which can run in any environment and are used to perform specific tasks. For example, a tool function may be used to download a file pointed to by a URL or to send an HTTP request. So when you build a new tool, please pay attention to the focus and task characteristics of these two types of tools.

## Create new tools

According to the characteristics of your new tools, create a Python file in the `ToolServer/ToolServerNode/core/tools` or `ToolServer/ToolServerNode/extensions/tools` path and define your new tools in the file. This function needs to be decorated with the `@toolwrapper()` decorator to wrap it during tool registration.

Tool functions usually need to receive some parameters, which can be used to control the behavior of the tool. For example, in the `shell_command_executor` tool, the `command` parameter is used to specify the shell command to be executed, the `run_async` parameter is used to control whether the command is executed asynchronously, the `shell_id` parameter is used to specify which shell to execute the command in, and the `kill` parameter is used to control whether to kill the command.

In `wrapper.py`, the `toolwrapper` function is a decorator that converts ordinary classes or functions into tools. `toolwrapper` is mainly responsible for generating **tool labels, including tool name, description, parameters** and other information. If the decorated object is a class, it will check whether the class is a subclass of `BaseEnv`, and then generate tool labels for the class and all its methods, and store these labels in the class's `env_labels` attribute. If the decorated object is a function, it will generate tool labels for the function and store the labels in the function's `tool_labels` attribute.

**Important**: When defining a tool function, it is necessary to provide a detailed docstring. This docstring will be parsed and used to generate help information for the tool. It will also be checked during the `toolwrapper` function. The description information in the docstring will be stored in the tool labels and can be used to display information about the tool.

We highly recommend that you follow the example below when writing docstrings to enrich the description of the tool and avoid issues with parsing errors:
```python
The shell tool that execute shell command in root privilege, return the output and error. 
You can use this tool to install packages, download files, run programs, etc.
Set run_async=True to run the command in a new thread and return instantly if your command is time costly like install packages, host services. 
Example:

In: shell_command_executor(command='echo "hello world"')
Out: "hello world"
In: shell_command_executor(command='sleep 10', run_async=True)
Out: {'shell_id': 0} # You can use this id to read the output and error later.
In: shell_command_executor(shell_id=0, kill=True)
Out: "" # The shell 0 will be killed.

:param string? command: The shell command to be executed, must avoid command requiring additional user input. Default is empty string.
:param boolean? run_async: Whether to run the command asynchronously, default is False. If True, call this tool again with shell_id to get the final output and error. 
:param integer? shell_id: The id of shell to execute command, default is None, which means running in a new shell. Change this to execute command in the same shell.
:param boolean? kill: If True, kill the shell which runs the command after execution. Default is False. Don't use any other kill command!
```

**Note**: Please be aware that when you add a new tool function, if an error occurs during the tool's execution, you should throw a ToolExecutionError exception.

Here is an example code for creating a new tool:
```python
from core.register import toolwrapper
from core.exceptions import ToolExecutionError

@toolwrapper()
async def new_tool(param1: str = '', param2: bool = False):
    """
    This is a new tool that does something.

    :param param1: The first parameter of the new_tool function. It is a string.
    :param param2: The second parameter of the new_tool function. It is a boolean.
    :return: The output of the new_tool function as a string.
    :raises ToolExecutionError: If something goes wrong during the execution of the new_tool function.
    """
    # Do something with param1 and param2
    # If something goes wrong, raise a ToolExecutionError
    # Return the output as a string
    return "Output of the new tool"
```

We recommend defining new tools as asynchronous functions, as this can better utilize the features of asynchronous programming, improve the concurrency performance of the program, and reduce waiting time.
If you are not familiar with asynchronous programming, you can refer to [this article](https://realpython.com/async-io-python/)。

## Tool Configuration

After registering a new tool, please fill in the module name under the `enabled_extensions:` field in the `assets/config/node.yml` file to activate the new tool, for example:
```yaml
enabled_extensions:
  - extensions.envs.rapidapi
  - extensions.tools.my_new_tool
```
In this way, you can finally enable a tool dynamically in XAgent.