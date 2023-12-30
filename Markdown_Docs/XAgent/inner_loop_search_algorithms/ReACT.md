# FunctionDef make_message
**make_message函数**：此函数用于为每个节点生成消息。

该函数接受以下参数：
- now_node：当前的ToolNode实例。
- max_length：子任务链的最大长度。
- config：配置设置。
- now_dealing_task：当前处理的任务。

该函数返回当前节点的消息序列。

函数内部逻辑如下：
1. 如果配置中启用了摘要功能（enable_summary为True），则使用summarize_plan函数对当前处理的任务进行摘要，将结果赋值给terminal_task_info变量。
2. 否则，将当前处理的任务转换为JSON格式，并使用json.dumps函数将其格式化为字符串，设置缩进为2，确保不转义非ASCII字符，将结果赋值给terminal_task_info变量。
3. 创建一个空的消息序列列表。
4. 构建当前子任务的提示信息now_subtask_prompt，包含terminal_task_info的内容，并将其作为Message对象添加到消息序列中。
5. 获取当前节点的process属性，赋值给action_process变量。
6. 如果配置中启用了摘要功能（enable_summary为True），则使用summarize_action函数对action_process进行摘要，将结果赋值给action_process变量。
7. 构建用户提示信息user_prompt，包含action_process的内容，并将其作为Message对象添加到消息序列中。
8. 返回消息序列。

**注意**：使用此函数时需要注意以下几点：
- 需要传入正确的参数，包括now_node、max_length、config和now_dealing_task。
- 如果配置中启用了摘要功能（enable_summary为True），则会对任务和动作进行摘要处理。
- 函数返回的是一个消息序列，可以根据需要进行进一步处理或展示。

**输出示例**：以下是函数返回值的示例：
```
[
    Message("user", "Now you will perform the following subtask:\n"""\n{terminal_task_info}\n"""\n"),
    Message("user", "The following steps have been performed (you have already done the following and the current file contents are shown below):\n\n{action_process}")
]
```
***
# ClassDef ReACTChainSearch
**ReACTChainSearch函数**: 这个类的功能是执行ReACT链式搜索，它用于执行基于链式搜索的任务。

该类继承自BaseSearchMethod类，用于实现ReACT链式搜索的功能。它通过维护一个任务树的列表来表示处理过的任务，并提供了一系列方法来操作任务树。

**__init__函数**:
- xagent_core_components: XAgentCoreComponents对象，用于初始化ReACTChainSearch对象。它维护一个任务树的列表来表示处理过的任务。

**run函数**:
- config: 搜索的配置信息。
- agent: 负责链式搜索的基础代理。
- arguments: 当前任务的参数。
- functions: 可用的函数列表。
- task_id: 当前任务的ID。
- max_try: 最大尝试次数。
- max_answer: 最大接收答案的数量。

**get_finish_node函数**:
- 返回任务树中的完成节点。

**get_origin_data函数**:
- data: 初始输入数据列表。
- 返回初始输入数据的字典形式。

**rewrite_input_func函数**:
- old: 旧的输入项。
- new: 替换旧输入项的新输入项。
- 返回更新后的输入列表和重写状态。

**generate_chain函数**:
- config: 搜索的配置信息。
- agent: 负责链式搜索的基础代理。
- arguments: 当前任务的参数。
- functions: 可用的函数列表。
- task_id: 当前任务的ID。
- now_dealing_task: 当前处理的任务。
- plan_agent: 计划代理。
- 运行链式搜索任务。

**to_json函数**:
- 将ReACTChainSearch对象转换为JSON格式。

**is_include_pictures函数**:
- 判断是否包含图片。

**注意**: 
- ReACTChainSearch类用于执行基于链式搜索的任务。
- 该类维护一个任务树的列表来表示处理过的任务。
- run函数用于运行链式搜索任务。
- get_finish_node函数用于获取任务树中的完成节点。
- get_origin_data函数用于获取初始输入数据。
- rewrite_input_func函数用于检查新输入是否有效，并更新旧输入。
- generate_chain函数用于运行链式搜索任务。
- to_json函数用于将对象转换为JSON格式。
- is_include_pictures函数用于判断是否包含图片。

**输出示例**:
```python
search_method = ReACTChainSearch(xagent_core_components=core_components)
search_method.run(config, agent, arguments, functions, task_id, now_dealing_task, plan_agent)
finish_node = search_method.get_finish_node()
origin_data = search_method.get_origin_data(data)
updated_input, rewrite_status = search_method.rewrite_input_func(old, new)
search_method.generate_chain(config, agent, arguments, functions, task_id, now_dealing_task, plan_agent)
search_method.to_json()
include_pictures = search_method.is_include_pictures(using_tools)
```
## FunctionDef __init__
**__init__函数**：该函数的功能是初始化ReACTChainSearch对象。它维护一个树的列表来表示已处理的任务。

在这个函数中，我们首先调用父类的构造函数`super().__init__()`来初始化父类的属性。然后，我们定义了以下属性：

- `tree_list`：表示已处理任务的树的列表。
- `finish_node`：表示任务的结束节点。
- `xagent_core_components`：一个XAgentCoreComponents对象，用于初始化ReACTChainSearch对象。

在这个函数中，我们没有返回任何值。

**注意**：在使用这段代码时需要注意以下几点：
- 在使用该函数之前，需要先创建一个XAgentCoreComponents对象，并将其作为参数传入该函数。
- 在初始化ReACTChainSearch对象后，可以通过访问`tree_list`属性来获取已处理任务的树的列表。
- 可以通过访问`finish_node`属性来获取任务的结束节点。
## FunctionDef run
**run函数**：此函数的功能是运行链式搜索任务。

该函数接受以下参数：
- config：搜索的配置信息。
- agent：负责链式搜索的基础代理。
- arguments：当前任务的参数。
- functions：可供代理使用的可用函数。
- task_id：当前任务的ID。
- max_try：最大尝试次数，默认为1。
- max_answer：最大接收答案的数量，默认为1。

该函数通过循环尝试执行generate_chain函数，直到达到最大尝试次数为止。

如果搜索的状态为HAVE_AT_LEAST_ONE_ANSWER，则将状态设置为SUCCESS，否则设置为FAIL。

**注意**：在使用该函数时需要注意以下几点：
- 需要提供正确的配置信息和代理对象。
- 参数arguments需要符合函数'action_reasoning'的参数规范。
- 函数functions需要包含代理所需的内置工具。
- task_id需要提供正确的任务ID。
- max_try和max_answer可以根据需要进行调整。
## FunctionDef get_finish_node
**get_finish_node函数**：该函数用于检索任务树中已完成的节点。

该函数没有参数。

返回值：
- 已完成的节点。

该函数用于获取任务树中已完成的节点。在任务处理过程中，当一个节点完成时，可以通过调用该函数获取已完成的节点。

**注意**：无

**输出示例**：假设已完成的节点为node1，则函数返回值为node1。
## FunctionDef get_origin_data
**get_origin_data函数**：该函数的功能是检索最初输入的数据。

该函数接受一个数据列表作为参数，并将最初输入的数据转换为字典形式返回。

在函数内部，首先初始化了一些变量，如assistant_thoughts_reasoning、assistant_thoughts_plan、assistant_thoughts_speak和assistant_thoughts_criticism等。

然后，通过获取输入数据中的"thoughts"字段，进一步获取"reasoning"、"plan"和"criticism"等属性的值。

最后，将获取到的数据以字典形式返回。

**注意**：该函数的参数data应为一个字典，其中包含了最初输入的数据。

**输出示例**：返回一个包含最初输入数据的字典，格式如下：
```
{
    "args": {
        "thoughts": "XXX",
        "reasoning": "XXX",
        "plan": "XXX",
        "criticism": "XXX"
    }
}
```
## FunctionDef rewrite_input_func
**rewrite_input_func函数**：该函数的功能是检查新输入是否有效，如果有效则用新输入更新旧输入。

该函数接受两个参数：
- old：旧的输入条目。
- new：要替换旧输入的新输入条目。

该函数的返回值为更新后的输入列表和重写状态。

函数内部逻辑如下：
1. 首先判断新输入是否为字典类型，如果不是则不进行任何操作。
2. 如果新输入为None，则返回旧输入和False。
3. 否则，从新输入中获取args字段的值，并初始化assistant_thoughts_reasoning、assistant_thoughts_plan、assistant_thoughts_speak和assistant_thoughts_criticism变量。
4. 从旧输入中获取thoughts字段的值，并将其赋值给assistant_thoughts变量。
5. 从assistant_thoughts中获取properties字段的值，并将其赋值给assistant_thoughts_text变量。
6. 如果assistant_thoughts不为空，则从args中检查是否存在"thoughts"和"thought"字段，并将其值更新到旧输入中的thoughts字段中。
7. 同样地，如果args中存在"reasoning"和"reasoning"字段，则将其值更新到旧输入中的thoughts字段中。
8. 如果args中存在"plan"和"plan"字段，则将其值更新到旧输入中的thoughts字段中。
9. 如果args中存在"criticism"和"criticism"字段，则将其值更新到旧输入中的thoughts字段中。
10. 返回更新后的旧输入和True。

**注意**：关于代码使用的注意事项
**输出示例**：模拟代码返回值的可能外观。

请注意：
- 生成的文档内容中不要包含Markdown的标题和分隔符语法。
- 主要使用中文进行描述，如果需要，可以在分析和描述中使用一些英文单词，以提高文档的可读性，因为不需要将函数名或变量名翻译成目标语言。
## FunctionDef generate_chain
**generate_chain函数**：此函数的功能是运行链式搜索任务。

该函数接受以下参数：
- config：搜索的配置信息。
- agent：负责链式搜索的基础代理。
- arguments：当前任务的参数。
- functions：可供代理使用的可用函数。
- task_id：当前任务的ID。

该函数没有返回值。

该函数的作用是运行链式搜索任务。它通过循环迭代来生成任务搜索树，并根据配置的最大子任务链长度来限制搜索的深度。在每次迭代中，函数会调用代理的parse方法，将当前节点的数据转换为消息，并将消息传递给工具节点进行处理。函数还会处理工具节点的输出，并根据输出的状态码来判断是否需要进行计划的优化。最后，函数会更新搜索树的节点，并根据工具节点的输出状态码来判断搜索任务是否完成。

**注意**：在每次迭代中，函数会根据配置的enable_ask_human_for_help参数来判断是否允许用户向人类寻求帮助。如果允许，函数会在消息中添加相应的提示信息。另外，函数还会根据配置的enable_summary参数来决定是否对计划进行摘要。

**输出示例**：无返回值。
## FunctionDef to_json
**to_json函数**: 这个函数的功能是将ReACTChainSearch对象转换为JSON。

这个函数是一个占位函数，目前没有实现具体的功能。它的返回值是None。

**注意**: 目前这个函数没有实现具体的功能，所以在使用时需要注意。
## FunctionDef is_include_pictures
**is_include_pictures函数**：该函数的功能是判断给定的工具列表中是否包含png文件。

该函数接受一个参数using_tools，该参数是一个字典，包含了使用的工具的相关信息。函数首先从using_tools中获取工具的名称tool_name和工具的输出tool_output。如果using_tools不是字典类型，则将tool_name和tool_output设置为空字符串和空字典。

接下来，函数判断tool_name是否为"PythonNotebook_execute_cell"。如果是，则遍历tool_output列表，对于每个输出output，判断其是否为字典类型且是否包含'file_name'键。如果是，则说明输出中包含了png文件，函数返回True。

如果tool_name不是"PythonNotebook_execute_cell"，或者tool_output中没有包含png文件的输出，则函数返回False。

**注意**：使用该函数时需要传入一个包含工具信息的字典using_tools。函数会判断工具列表中是否包含png文件，并返回相应的结果。

**输出示例**：假设using_tools为{"tool_name": "PythonNotebook_execute_cell", "tool_output": [{"file_name": "image1.png"}, {"file_name": "image2.jpg"}]}，则函数返回True。
***
