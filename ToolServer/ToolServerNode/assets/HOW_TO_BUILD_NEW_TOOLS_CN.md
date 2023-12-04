# 在这个项目中，您需要遵循以下规则及注意事项以新建工具

## 工具路径划分
在项目中您会发现`ToolServer/ToolServerNode/core/tools`和`ToolServer/ToolServerNode/extensions/tools`两个工具目录，这两个目录分别用于存放核心工具和扩展工具。核心工具是指在项目中必须存在的工具，它们提供了应用程序的基本功能，因此不能被移除或禁用。而在`ToolServerNode/extensions/tools`目录中的工具则是用来扩展应用程序的功能的。这些工具提供了一些额外的、可选的功能，可以根据需要添加或移除。我们将这两部分工具分开定义，是为了使应用程序的结构更清晰且易于管理和维护。

## envs和tools的区别
在`extensions`或`core`目录下，`envs`和`tools`两个子目录通常用于存放不同类型的扩展模块。`envs`目录下的Python文件通常定义了一些环境类，这些类继承自`BaseEnv`类，用于描述和管理一个特定的运行环境。比如一个**环境类**可能描述了一个数据库环境，包括如何连接到数据库，如何查询数据等。`tools`目录下的Python文件则通常定义了一些工具函数，这些函数可以在任何环境下运行，用于执行一些特定的任务。比如一个工具函数可能用于下载一个URL指向的文件，或者发送一个HTTP请求。所以在您构建新工具的时候请注意区分这两者的关注点和任务特性。

## 新建工具

根据您新建工具的特性，在 `ToolServer/ToolServerNode/core/tools` 或`ToolServer/ToolServerNode/extensions/tools`路径下新建一个 Python 文件，在文件中定义您的新工具。这个函数需要使用 `@toolwrapper()` 装饰器进行装饰，以便在工具注册时进行包装。

工具函数通常需要接收一些参数，这些参数可以用来控制工具的行为。例如，在 `shell_command_executor` 工具中，`command` 参数用于指定要执行的 shell 命令，`run_async` 参数用于控制命令是否异步执行，`shell_id` 参数用于指定在哪个 shell 中执行命令，`kill` 参数用于控制是否杀死命令。

在 `wrapper.py` 中，`toolwrapper` 函数是一个装饰器，用于将普通的类或函数转换为工具。`toolwrapper` 主要负责生成**工具的标签，包括工具的名称、描述、参数**等信息。如果装饰的对象是一个类，它会检查这个类是否是 `BaseEnv` 的子类，然后为这个类和它的所有方法生成工具标签，并将这些标签存储在类的 `env_labels` 属性中。如果装饰的对象是一个函数，它会为这个函数生成工具标签，并将这个标签存储在函数的 `tool_labels` 属性中。

**重要**: 在定义工具函数时，需要给出详细的 `docstring`，这个 `docstring` 会被解析并被用于生成工具的帮助信息，并且会在 `toolwrapper` 函数执行工具注册时被检查，`docstring` 描述信息会被存储在工具标签中，可以用于显示工具的信息。

我们十分建议您依照以下规范来编写docstring，以丰富工具的描述并避免解析错误等可能的问题：
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

**注意**:请注意当您新增了一个工具函数，如果工具执行过程中出现错误，请抛出一个`ToolExecutionError`异常。

这是一个新建工具的示例代码：
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
我们建议将新工具定义为异步函数，这样能够更好地利用异步编程的特性，提高程序的并发性能，减少等待时间。
如果您不熟悉异步编程，可以参考[这篇文章](https://realpython.com/async-io-python/)。

## 工具配置文件

新工具注册后，请在`assets/config/node.yml`中的`enabled_extensions:`字段下填写模块名称，激活新工具，例如：
```yaml
enabled_extensions:
  - extensions.envs.rapidapi
  - extensions.tools.my_new_tool
```
通过这种方式，就最终能在XAgent中动态启用一个工具了。
