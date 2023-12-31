# ClassDef WorkingMemoryAgent
**WorkingMemoryAgent函数**：这个类的函数是用来表示一个agent的工作内存。

工作内存是一个agent在执行任务过程中用来存储信息的地方。它包含了两个属性：subtask_handle_mapping和execute_process。

- subtask_handle_mapping是一个字典，用来存储子任务的映射关系。它将子任务的id与终止计划进行映射。
- execute_process是一个列表，用来存储待执行的进程。

**构造函数**：WorkingMemoryAgent类的构造函数。

参数：
- logger（对象）：日志记录器对象。

**get_working_memory_function方法**：从函数管理器中获取'chat_with_other_subtask'函数的模式。

返回值：
- 列表：包含'chat_with_other_subtask'函数模式的列表。

**register_task方法**：注册一个任务，将任务的终止计划添加到执行进程中，并在subtask_handle_mapping中将子任务id与终止计划进行映射。

参数：
- terminal_plan（对象）：任务的终止计划。

**handle方法**：处理名为'chat_with_other_subtask'的工具。

参数：
- tool_name（字符串）：工具的名称。
- tool_input（字符串）：工具的输入。

抛出：
- AssertionError：如果工具名称不是'chat_with_other_subtask'。

**注意**：在使用该类时需要注意以下几点：
- WorkingMemoryAgent类用于表示一个agent的工作内存，可以用来存储任务的信息。
- 通过调用register_task方法可以注册一个任务，并将任务的终止计划添加到执行进程中。
- 通过调用handle方法可以处理名为'chat_with_other_subtask'的工具。

**输出示例**：
```
Working Memory: Register a new subtask=subtask_id Process length=finish_node.get_depth().
```
## FunctionDef __init__
**__init__函数**：该函数是WorkingMemoryAgent类的构造函数。

该函数接受一个logger对象作为参数，并将其赋值给self.logger属性。self.subtask_handle_mapping属性被初始化为空字典。self.execute_process属性被初始化为空列表。

**注意**：在使用该代码时需要注意以下几点：
- 该函数用于初始化WorkingMemoryAgent类的实例。
- 可以通过传入logger对象来设置self.logger属性。
- self.subtask_handle_mapping属性用于存储子任务的处理映射关系。
- self.execute_process属性用于存储执行过程的列表。
## FunctionDef get_working_memory_function
**get_working_memory_function函数**：该函数用于从函数管理器中获取'chat_with_other_subtask'函数的模式。

该函数的返回值是一个包含'chat_with_other_subtask'函数模式的列表。

**代码分析和描述**：
该函数通过调用函数管理器的get_function_schema方法，传入'chat_with_other_subtask'作为参数，来获取'chat_with_other_subtask'函数的模式。

**注意**：使用该代码时需要注意以下几点：
- 需要确保函数管理器中存在'chat_with_other_subtask'函数的模式。
- 返回值是一个包含'chat_with_other_subtask'函数模式的列表。

**输出示例**：假设'chat_with_other_subtask'函数的模式如下：
```
{
    'name': 'chat_with_other_subtask',
    'description': 'This function is used to chat with other subtasks.',
    'parameters': [
        {
            'name': 'message',
            'type': 'str',
            'description': 'The message to be sent.'
        }
    ],
    'return': {
        'type': 'str',
        'description': 'The response message.'
    }
}
```
则该函数的返回值为：
```
[{
    'name': 'chat_with_other_subtask',
    'description': 'This function is used to chat with other subtasks.',
    'parameters': [
        {
            'name': 'message',
            'type': 'str',
            'description': 'The message to be sent.'
        }
    ],
    'return': {
        'type': 'str',
        'description': 'The response message.'
        }
}]
```
## FunctionDef register_task
**register_task函数**：该函数的功能是注册一个任务，即将任务的终端计划添加到执行过程中，并在subtask_handle_mapping中将子任务ID与终端计划进行映射。

该函数接受一个参数terminal_plan，表示任务的终端计划。

函数内部首先获取终端计划的子任务ID，并将终端计划的处理节点保存在finish_node变量中。

然后创建一个名为datapoint的字典，其中包含以下键值对：
- "plan"：终端计划
- "task_id"：子任务ID
- "qa_sequence"：空列表

接着将datapoint添加到execute_process列表中，并将子任务ID与datapoint的映射关系保存在subtask_handle_mapping字典中。

最后使用logger.typewriter_log方法打印一条日志，内容为"Working Memory: Register a new subtask=xxx Process length=xxx."，其中xxx分别为子任务ID和finish_node的深度。

**注意**：使用该代码时需要注意以下几点：
- 参数terminal_plan必须是一个对象，表示任务的终端计划。
- 执行过程中会修改execute_process列表和subtask_handle_mapping字典的内容。
## FunctionDef handle
**handle函数**：这个函数的功能是处理名为'chat_with_other_subtask'的工具。

这个函数有两个参数，分别是tool_name和tool_input。tool_name是工具的名称，tool_input是工具的输入。

在函数内部，首先使用断言语句assert来判断tool_name是否等于"chat_with_other_subtask"，如果不等于，则会抛出AssertionError异常。

接着，函数会调用self.logger.log方法，记录一条日志，内容为"handle chat with other subtask"。

**注意**：使用这段代码时需要注意以下几点：
- 调用handle函数时，需要传入正确的工具名称和工具输入。
- 如果工具名称不是"chat_with_other_subtask"，会抛出AssertionError异常。
***
