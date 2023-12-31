# ClassDef FunctionHandler
**FunctionHandler函数**: 这个类的功能是处理函数。

FunctionHandler类是一个处理函数的类，它用于处理函数的调用和执行。它接收来自ToolServerInterface的工具调用请求，并根据请求的类型执行相应的操作。它还负责记录任务的提交和执行结果，并将结果返回给调用者。

该类的构造函数接受以下参数：
- toolserver_interface：ToolServerInterface对象，用于与工具服务器进行通信。
- config：配置对象，包含函数处理器的配置信息。
- interaction：XAgentInteraction对象，用于与用户进行交互。
- recorder：RunningRecoder对象，用于记录任务的提交和执行结果。
- logger：日志记录器对象，用于记录日志信息。

该类的方法包括：
- log_task_submit(arguments)：记录任务的提交信息。
- change_subtask_handle_function_enum(function_name_list)：更改子任务处理函数的枚举。
- intrinsic_tools(enable_ask_human_for_help)：获取内置工具。
- get_functions(config)：获取函数列表。
- long_result_summary(command, result)：对长结果进行摘要。
- handle_tool_call(node)：处理工具调用。
- handle_subtask_submit(arguments)：处理子任务提交。
- handle_human_help(arguments)：处理请求人工帮助。

注意事项：
- 该类依赖于ToolServerInterface、XAgentInteraction、RunningRecoder等其他类的实例对象。
- 在使用该类之前，需要先实例化相关的对象，并将其作为参数传递给FunctionHandler的构造函数。

输出示例：
```
Command subtask_submit returned: {"content": "you have successfully submit the subtask as XXX"}
TOOL STATUS CODE: TOOL_CALL_SUCCESS
```

以上是对FunctionHandler类的详细分析和描述。该类是XAgent项目中用于处理函数调用和执行的关键组件，它负责与工具服务器进行通信，并根据请求的类型执行相应的操作。通过使用该类，开发人员可以方便地处理函数调用，并记录任务的提交和执行结果。
## FunctionDef __init__
**__init__函数**：这个函数的作用是初始化FunctionHandler对象。

在这个函数中，有以下几个参数：
- toolserver_interface: ToolServerInterface对象，用于与ToolServer进行交互。
- config: 配置信息。
- interaction: XAgentInteraction对象，用于与用户进行交互。
- recorder: RunningRecoder对象，用于记录运行过程。
- logger: 日志记录器。

在函数体内，将传入的参数赋值给对应的成员变量。具体来说，将toolserver_interface赋值给self.toolserver_interface，将config赋值给self.config，将interaction赋值给self.interaction，将recorder赋值给self.recorder，将logger赋值给self.logger。

接下来，通过function_manager.get_function_schema函数获取subtask_submit、ask_human_for_help和human_interruption三个函数的函数模式，并将其赋值给对应的成员变量。具体来说，将subtask_submit的函数模式赋值给self.subtask_submit_function，将ask_human_for_help的函数模式赋值给self.ask_human_for_help_function，将human_interruption的函数模式赋值给self.human_interruption_function。

最后，初始化一个空的avaliable_tools_description_list列表，并将其赋值给self.avaliable_tools_description_list。

**注意**：在使用这段代码时需要注意以下几点：
- 需要传入正确的参数，包括toolserver_interface、config、interaction、recorder和logger。
- 需要确保function_manager中存在subtask_submit、ask_human_for_help和human_interruption这三个函数的函数模式。
## FunctionDef log_task_submit
**log_task_submit函数**: 这个函数的功能是记录任务提交。

该函数用于记录任务的提交信息，包括提交类型、成功与否、结论、里程碑等信息。它接受一个参数arguments，该参数是任务提交的参数。

在函数内部，首先使用logger.typewriter_log方法打印出"-=-=-=-=-=-=-= SUBTASK SUBMITTED -=-=-=-=-=-=-="，并设置打印颜色为黄色。然后打印出"submit_type:"、"success:"、"conclusion:"等信息，并将对应的值打印出来。如果arguments["result"]中存在"milestones"键，则打印出"milestones:"，并遍历arguments["result"]["milestones"]中的每个里程碑，将其打印出来。最后打印出"need_for_plan_refine:"和"plan_suggestions:"的值。

该函数在以下文件中被调用：
- XAgent/function_handler.py

在handle_tool_call函数中，根据command_name的不同，调用不同的处理函数。当command_name为"subtask_submit"时，调用handle_subtask_submit函数；当command_name为"ask_human_for_help"时，调用handle_human_help函数；当command_name为"human_interruption"时，抛出异常；当command_name为空或为None时，设置command_result为空字符串，tool_output_status_code为ToolCallStatusCode.TOOL_CALL_SUCCESS。对于其他情况，调用toolserver_interface.execute_command_client方法执行命令，并获取命令的结果和状态码。如果状态码为ToolCallStatusCode.TIMEOUT_ERROR且命令结果中包含"type"为"retry"的键值对，则进行重试，最多重试10次。如果重试次数达到最大值仍然超时，则将command_result设置为"Timeout and no content returned! Please check the content you submit!"。如果状态码为ToolCallStatusCode.TOOL_CALL_SUCCESS，则调用long_result_summary方法对结果进行摘要。最后，将结果打印出来，并将结果和状态码保存到node的data中。

如果tool_output_status_code为ToolCallStatusCode.TOOL_CALL_SUCCESS，则将结果设置为绿色；如果tool_output_status_code为ToolCallStatusCode.SUBMIT_AS_SUCCESS，则将结果设置为黄色；如果tool_output_status_code为ToolCallStatusCode.SUBMIT_AS_FAILED，则将结果设置为蓝色；否则将结果设置为红色。将工具调用的相关信息注册到recorder中，并返回结果、状态码、是否需要优化计划和使用的工具。

**注意**: 在调用该函数之前，需要确保参数arguments中包含必要的信息，并且已经初始化了logger和recorder对象。
## FunctionDef change_subtask_handle_function_enum
**change_subtask_handle_function_enum函数**：该函数用于更改子任务处理函数的枚举。

该函数接受一个参数function_name_list，该参数是一个字符串列表，包含了要更改的函数名称。

函数内部根据self.config.default_request_type的值进行不同的处理：
- 当self.config.default_request_type为'openai'时，通过调用function_manager.get_function_schema('subtask_handle')获取子任务处理函数的架构，并将其中的"tool_call"字段中的"tool_name"字段的枚举值更改为function_name_list。
- 当self.config.default_request_type为'xagent'时，不进行任何操作。
- 当self.config.default_request_type为其他值时，抛出NotImplementedError异常，提示该请求类型尚未实现。

**注意**：在使用该函数时需要注意以下几点：
- function_name_list参数必须是一个字符串列表。
- 调用该函数前需要确保self.config.default_request_type的值已经正确设置。

该函数在以下文件中被调用：
- 文件路径：XAgent/function_handler.py
- 调用代码：
```python
def get_functions(self, config):
    """
    Get the functions.

    Args:
        config: The configuration for the functions.

    Returns:
        The intrinsic tools and the description of the tools.
    """
    output = self.toolserver_interface.get_available_tools()

    available_tools: list = output['available_tools']
    openai_function_jsons: dict = output['tools_json']

    black_list = set(config.tool_blacklist)
    for item in black_list:
        try:
            available_tools.remove(item)
        except ValueError:
            pass
    openai_function_jsons = [
        openai_function_json for openai_function_json in openai_function_jsons if openai_function_json['name'] not in black_list]

    self.tool_names = available_tools
    self.change_subtask_handle_function_enum(available_tools)
    self.avaliable_tools_description_list = openai_function_jsons
    for tool_json in openai_function_jsons:
        function_manager.register_function(tool_json)
    return self.intrinsic_tools(config.enable_ask_human_for_help), self.avaliable_tools_description_list
```
- 代码分析：该函数在get_functions函数中被调用，用于根据获取到的可用工具列表来更改子任务处理函数的枚举值，以及注册工具函数。

- 文件路径：XAgent/workflow/task_handler.py
- 调用代码：
```python
def inner_loop(self, plan: Plan, ):
    """
    Generates search plan and process it for the current task.

    Args:
        plan (Plan): The plan to be processed.

    Raises:
        AssertionError: Raised if a not expected status is encountered while handling the plan.

    Returns:
        ReACTChainSearch: Instance of the search plan.
    """
    task_ids_str = plan.get_subtask_id(to_str=True)
    self.logger.typewriter_log(
        f"-=-=-=-=-=-=-= Performing Task {task_ids_str} ({plan.data.name}): Begin -=-=-=-=-=-=-=",
        Fore.GREEN,
        "",
    )
    self.xagent_core.print_task_save_items(plan.data)

    agent = self.agent_dispatcher.dispatch(
        RequiredAbilities.tool_tree_search,
        json.dumps(plan.data.to_json(), indent=2, ensure_ascii=False),
        # avaliable_tools_description_list=self.avaliable_tools_description_list
    )

    plan.data.status = TaskStatusCode.DOING

    if self.config.rapidapi_retrieve_tool_count > 0:
        retrieve_string = summarize_plan(plan.to_json())
        rapidapi_tool_names, rapidapi_tool_jsons = self.toolserver_interface.retrieve_rapidapi_tools(
            retrieve_string, top_k=self.config.rapidapi_retrieve_tool_count)
        if rapidapi_tool_names is not None:
            self.function_handler.change_subtask_handle_function_enum(
                self.function_handler.tool_names + rapidapi_tool_names)
            self.function_handler.avaliable_tools_description_list += rapidapi_tool_jsons
        else:
            print("bug: no rapidapi tool retrieved, need to fix here")

    search_method = ReACTChainSearch(
        xagent_core_components=self.xagent_core,)

    arguments = function_manager.get_function_schema('action_reasoning')[
        'parameters']
    search_method.run(config=self.config,
                      agent=agent,
                      arguments=arguments,
                      functions=self.function_handler.intrinsic_tools(
                          self.config.enable_ask_human_for_help),
                      task_id=task_ids_str,
                      now_dealing_task=self.now_dealing_task,
                      plan_agent=self.plan_agent)

    if search_method.status == SearchMethodStatusCode.SUCCESS:
        plan.data.status = TaskStatusCode.SUCCESS
        self.logger.typewriter_log(
            f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Solved -=-=-=-=-=-=-=",
            Fore.GREEN,
            "",
        )
    elif search_method.status == SearchMethodStatusCode.FAIL:
        plan.data.status = TaskStatusCode.FAIL
        self.logger.typewriter_log(
            f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Failed -=-=-=-=-=-=-=",
            Fore.RED,
            "",
        )
    else:
        assert False, f"{plan.data.name}"
    return search_method
```
- 代码分析：该函数在inner_loop函数中被调用，用于在处理当前任务之前，根据配置中的rapidapi_retrieve_tool_count的值来获取RapidAPI工具，并将获取到的工具名称添加到子任务处理函数的枚举值中。

[End of XAgent/function_handler.py]
[End of XAgent/workflow/task_handler.py]
## FunctionDef intrinsic_tools
**intrinsic_tools函数**：该函数的作用是获取内置工具。

该函数接受一个参数enable_ask_human_for_help，用于确定是否启用ask_human_for_help函数。

函数返回一个包含内置工具的列表。

该函数首先创建一个名为tools的列表，初始值为[self.subtask_submit_function]。

如果enable_ask_human_for_help为True，则将self.ask_human_for_help_function添加到tools列表中。

然后将self.avaliable_tools_description_list中的元素添加到tools列表中。

最后返回tools列表作为函数的输出。

**注意**：在使用该函数时需要注意以下几点：
- enable_ask_human_for_help参数决定是否启用ask_human_for_help函数。
- 函数的返回值是一个包含内置工具的列表。

**输出示例**：假设enable_ask_human_for_help为True，self.avaliable_tools_description_list为['tool1', 'tool2']，则函数的返回值为[self.subtask_submit_function, self.ask_human_for_help_function, 'tool1', 'tool2']。
## FunctionDef get_functions
**get_functions函数**：该函数的作用是获取可用的函数。

该函数接受一个配置参数config作为输入，返回内置工具和工具描述的列表。

具体代码分析和描述如下：
- 首先，通过调用toolserver_interface的get_available_tools方法获取可用的工具和工具的描述信息。
- 然后，根据配置参数中的tool_blacklist，将黑名单中的工具从可用工具列表中移除，并将不在黑名单中的工具描述信息保存在openai_function_jsons列表中。
- 接下来，将可用工具列表保存在self.tool_names中，并根据可用工具列表更新子任务处理函数的枚举类型。
- 将可用工具的描述信息保存在self.avaliable_tools_description_list中。
- 遍历openai_function_jsons列表中的每个工具描述信息，通过调用function_manager的register_function方法注册工具。
- 最后，返回内置工具和工具描述的列表。

**注意**：使用该代码时需要注意以下几点：
- 需要提供一个有效的配置参数config。
- 需要确保toolserver_interface的get_available_tools方法能够正常返回可用的工具和工具描述信息。

**输出示例**：模拟代码返回值的可能外观。
```
([
    'subtask_function_1',
    'subtask_function_2',
    ...
], [
    {
        'name': 'tool_1',
        'description': '工具1的描述信息'
    },
    {
        'name': 'tool_2',
        'description': '工具2的描述信息'
    },
    ...
])
```
## FunctionDef long_result_summary
**long_result_summary函数**：该函数用于对长结果进行摘要。

该函数接受两个参数：command和result。其中，command是一个字典，表示命令；result是命令的执行结果。

函数内部根据不同的命令类型进行不同的处理。如果命令的名称是'WebEnv_browse_website'，则将结果进行解析，并截取网页内容的前8096个字符，然后调用function_manager函数进行处理。如果命令的名称是'WebEnv_search_and_browse'，则使用线程池并发处理多个结果，同样截取网页内容的前8096个字符，并调用function_manager函数进行处理。

如果结果是字符串且长度超过2000个字符，则需要进行摘要处理。

最后，函数返回处理后的结果。

**注意**：在使用该函数时，需要注意命令的格式和结果的类型。

**输出示例**：假设命令名称为'WebEnv_browse_website'，结果为解析后的网页内容和有用的超链接。

```python
{
    'text': '摘要后的结果',
    'useful_hyperlinks': ['超链接1', '超链接2', '超链接3']
}
```
## FunctionDef handle_tool_call
**handle_tool_call函数**：此函数的功能是处理工具调用。

该函数接受一个ToolNode对象作为参数，用于处理工具调用。根据传入的工具节点，函数会根据节点中的命令名称和参数执行相应的操作，并返回结果、工具输出状态码、是否需要优化计划以及使用的工具。

函数首先获取工具节点中的命令名称和参数，然后根据命令名称执行相应的操作。如果命令名称为"subtask_submit"，则调用handle_subtask_submit函数处理子任务提交；如果命令名称为"ask_human_for_help"，则调用handle_human_help函数处理向人类寻求帮助；如果命令名称为"human_interruption"，则抛出异常，因为不应该调用该函数；如果命令名称为空或为None，则将命令结果和工具输出状态码设置为空字符串和工具调用成功状态码。

如果命令名称不属于上述情况，则调用toolserver_interface的execute_command_client方法执行命令，并根据返回的结果和状态码进行处理。如果状态码为超时错误且命令结果中包含重试信息，则进行最多10次的重试，直到获取到结果或达到最大重试次数。如果状态码为超时错误且达到最大重试次数，则将命令结果设置为超时错误提示信息。

如果工具调用成功，则调用long_result_summary方法对命令结果进行摘要处理。最后，将结果存储到工具节点的data属性中，并根据工具输出状态码的不同，将相应的信息记录到日志中。

函数返回结果、工具输出状态码、是否需要优化计划以及使用的工具。

**注意**：在使用该函数时，需要注意以下几点：
- 函数的参数node必须是ToolNode类型的对象。
- 函数会根据命令名称执行相应的操作，因此需要确保命令名称的准确性。
- 函数会根据工具输出状态码的不同，记录相应的信息到日志中。

**输出示例**：假设命令名称为"subtask_submit"，参数为{"task_id": 123}，工具输出状态码为TOOL_CALL_SUCCESS，结果为"任务提交成功"，是否需要优化计划为False，使用的工具为{"tool_name": "subtask_submit", "tool_input": {"task_id": 123}, "tool_output": "任务提交成功", "tool_status_code": "TOOL_CALL_SUCCESS", "thought_data": {"thought": "思考内容", "content": "
## FunctionDef handle_subtask_submit
**handle_subtask_submit函数**：此函数的功能是处理子任务的提交。

该函数接受一个参数arguments，表示子任务的提交参数。

函数返回三个值：是否需要优化计划、工具输出状态码、结果。

在函数内部，首先初始化plan_refine为False。然后根据arguments中的"result"字段判断子任务是否成功，如果成功，则将tool_output_status_code设置为ToolCallStatusCode.SUBMIT_AS_SUCCESS；否则，将tool_output_status_code设置为ToolCallStatusCode.SUBMIT_AS_FAILED。接下来，根据arguments中的"suggestions_for_latter_subtasks_plan"字段判断是否需要优化计划，如果需要，则将plan_refine设置为True。然后，构造一个包含成功提交信息的answer字典，并将其转换为JSON格式的字符串赋值给command_result。最后，返回plan_refine、tool_output_status_code和command_result。

**注意**：在调用该函数之前，需要确保arguments参数的正确性。

**输出示例**：假设arguments为{"result": {"success": True}, "submit_type": "type1"}，则函数的返回值为(False, ToolCallStatusCode.SUBMIT_AS_SUCCESS, '{"content": "you have successfully submit the subtask as type1"}')。
## FunctionDef handle_human_help
**handle_human_help函数**：这个函数的功能是处理请求人工帮助。

该函数接受一个参数arguments，用于请求人工帮助。

函数首先通过logger.typewriter_log方法打印一条日志，提示用户输入反馈意见并按下Enter键以发送并继续循环。

接下来，函数构造了一个url和payload，并通过recorder.query_tool_server_cache方法查询工具服务器缓存。如果缓存中存在对应的工具输出和响应状态码，则将其赋值给command_result和status_code变量。

如果缓存中不存在对应的工具输出和响应状态码，则通过interaction.ask_for_human_help方法向用户询问反馈意见，并将用户的回答作为工具输出赋值给command_result变量。同时，将status_code赋值为"human has no status :)"。

最后，函数通过recorder.regist_tool_server方法将url、payload、command_result和status_code注册到工具服务器。

函数返回三个值：plan_refine（布尔值，表示是否需要优化计划）、ToolCallStatusCode.TOOL_CALL_SUCCESS（工具调用状态码）和command_result（工具输出结果）。

**注意**：在使用该函数时需要注意以下几点：
- 需要提供arguments参数来请求人工帮助。
- 函数会通过logger.typewriter_log方法打印提示信息，用户需要按照提示输入反馈意见。

**输出示例**：假设用户输入了反馈意见"请提供更多示例代码"，则函数的返回值可能如下所示：
```
(
    False,
    ToolCallStatusCode.TOOL_CALL_SUCCESS,
    '{"output": "请提供更多示例代码"}'
)
```
***
