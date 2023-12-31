# FunctionDef dump_common_things
**dump_common_things函数**: 这个函数的功能是将常用的数据类型（如str、int、float、bool、字典和列表）进行序列化。

该函数接受一个参数object，表示要序列化的对象。根据对象的类型，函数会执行不同的操作：

- 如果对象的类型是str、int、float或bool，直接返回该对象。
- 如果对象的类型是字典，遍历字典中的每个键值对，对键和值分别调用dump_common_things函数进行递归序列化，并返回序列化后的字典。
- 如果对象的类型是列表，遍历列表中的每个元素，对每个元素调用dump_common_things函数进行递归序列化，并返回序列化后的列表。
- 如果对象具有to_json方法，调用该方法并返回结果。

**注意**: 
- 该函数会递归地序列化对象，直到对象的类型为str、int、float、bool、字典或列表。
- 如果对象具有to_json方法，该方法将被调用并返回结果。
- 如果对象的类型不属于上述情况，函数将返回None。

**输出示例**:
- 输入: "Hello World"
  输出: "Hello World"
- 输入: {"name": "John", "age": 30}
  输出: {"name": "John", "age": 30}
- 输入: [1, 2, 3, 4, 5]
  输出: [1, 2, 3, 4, 5]
- 输入: datetime.datetime(2022, 1, 1)
  输出: None
***
# ClassDef RunningRecoder
**RunningRecoder函数**：这个类用于记录程序的运行序列，包括程序的查询状态和配置数据。

详细代码分析和描述：
- `__init__(self, record_root_dir="./running_records/")`：初始化RunningRecorder对象。接受一个可选的参数`record_root_dir`，表示运行记录的根目录。在初始化过程中，会根据当前时间和随机生成的字符串创建一个唯一的子目录，作为记录的存储路径。同时，会在子目录下创建两个子目录"LLM_inout_pair"和"tool_server_pair"，用于存储LLM输入输出对和工具服务器的记录。其他属性的初始值为默认值。

- `get_query_id(self)`：获取查询的ID。每次调用该方法，会返回当前查询计数，并将计数加1。

- `decrease_query_id(self)`：减少查询的ID。每次调用该方法，会将查询计数减1。

- `change_now_task(self, new_subtask_id)`：更改当前子任务。接受一个参数`new_subtask_id`，表示新子任务的ID。在调用该方法后，会将当前子任务ID更新为新的ID，并将工具调用ID和计划细化ID重置为0。

- `regist_plan_modify(self, refine_function_name, refine_function_input, refine_function_output, plan_after)`：注册计划修改。接受四个参数：`refine_function_name`表示计划修改函数的名称，`refine_function_input`表示计划修改函数的输入，`refine_function_output`表示计划修改函数的输出，`plan_after`表示修改后的计划。在注册过程中，会将计划修改记录以JSON格式保存到当前子任务的目录下。

- `regist_llm_inout(self, llm_query_id, messages, functions=None, function_call=None, model=None, stop=None, output_data=None, **other_args)`：注册LLM输入输出对。接受多个参数：`llm_query_id`表示LLM查询的ID，`messages`表示通信的消息，`functions`表示使用的函数列表，`function_call`表示调用的函数，`model`表示使用的模型，`stop`表示是否停止，`output_data`表示输出数据，`other_args`表示其他参数。在注册过程中，会将LLM输入输出对以JSON格式保存到"LLM_inout_pair"目录下，并将LLM输入输出对添加到缓存中。

- `query_llm_inout(self, llm_query_id, messages, functions=None, function_call=None, model=None, stop=None, **other_args)`：查询LLM输入输出对。接受多个参数：`llm_query_id`表示LLM查询的ID，`messages`表示通信的消息，`functions`表示使用的函数列表，`function_call`表示调用的函数，`model`表示使用的模型，`stop`表示是否停止，`other_args`表示其他参数。在查询过程中，会根据输入参数和缓存中的LLM输入输出对进行匹配，如果匹配成功，则返回对应的输出数据。

- `regist_tool_call(self, tool_name, tool_input, tool_output, tool_status_code, thought_data=None)`：注册工具调用。接受五个参数：`tool_name`表示工具的名称，`tool_input`表示工具的输入，`tool_output`表示工具的输出，`tool_status_code`表示工具的状态码，`thought_data`表示思考数据。在注册过程中，会将工具调用记录以JSON格式保存到当前子任务的目录下。

- `regist_tool_server(self, url, payload, tool_output, response_status_code)`：注册工具服务器。接受四个参数：`url`表示服务器的URL，`payload`表示工具的负载，`tool_output`表示工具的输出，`response_status_code`表示响应的状态码。在注册过程中，会将工具服务器记录以JSON格式保存到"tool_server_pair"目录下。

- `query_tool_server_cache(self, url, payload)`：查询工具服务器缓存。接受两个参数：`url`表示服务器的URL，`payload`表示要发送的负载。在查询过程中，会根据输入参数和缓存中的工具服务器记录进行匹配，如果匹配成功，则返回工具服务器的输出和响应状态码。

- `regist_query(self, query)`：注册查询。接受一个参数`query`，表示要注册的查询。在注册过程中，会将查询以JSON格式保存到记录的根目录下的"query.json"文件中。

- `get_query(self)`：获取注册的查询。在调用该方法后，会从记录的根目录下的"query.json"文件中读取查询，并返回查询对象。

- `regist_config(self, config: XAgentConfig)`：注册配置。接受一个参数`config`，表示要注册的配置。在注册过程中，会将配置以YAML格式保存到记录的根目录下的"config.yml"文件中。

- `get_config(self)`：获取注册的配置。在调用该方法后，会从记录的根目录下的"config.yml"文件中读取配置，并返回配置对象。

- `regist_father_info(self, record_dir)`：注册父信息。接受一个参数`record_dir`，表示记录的目录。在注册过程中，会将父信息以YAML格式保存到记录的根目录下的"This-Is-A-Reload-Run.yml"文件中。

- `load_from_disk(self, record_dir)`：从磁盘加载记录。接受一个参数`record_dir`，表示记录的目录。在加载过程中，会读取记录目录下的相关文件，并将数据加载到对象的属性中。

**注意**：在使用RunningRecoder类时，需要注意以下几点：
- 在初始化对象时，可以指定记录的根目录，如果不指定，默认为"./running_records/"。
- 在注册LLM输入输出对和工具服务器记录时，会将记录以JSON格式保存到相应的目录下。
- 在查询LLM输入输出对和工具服务器缓存时，会根据输入参数和缓存中的记录进行匹配，如果匹配成功，则返回相应的输出数据。
- 在注册查询和配置时，会将查询和配置以JSON和YAML格式保存到相应的文件中。
- 在加载记录时，会读取记录目录下的相关文件，并将数据加载到对象的属性中。

**输出示例**：
```python
running_recorder = RunningRecoder()
running_recorder.regist_llm_inout(1, "Hello", output_data="World")
running_recorder.query_llm_inout(1, "Hello")  # 返回 "World"
```
## FunctionDef __init__
**__init__函数**：该函数的功能是初始化RunningRecorder。

该函数接受一个参数record_root_dir，用于指定运行记录的根目录，默认为"./running_records/"。函数内部首先获取当前时间戳now，并将其转换为毫秒级别的时间戳。然后使用time模块将时间戳格式化为"%Y_%m_%d_%H_%M_%S"的字符串形式，并结合一个随机生成的8位十六进制字符串，生成一个唯一的strip字符串作为子目录的名称。

接下来，函数将record_root_dir和strip拼接起来作为运行记录的根目录，并使用os.makedirs函数创建该目录（如果目录不存在）。

然后，函数使用os.makedirs函数分别创建"LLM_inout_pair"和"tool_server_pair"两个子目录，用于存储LLM和工具服务器的运行记录。

接下来，函数将self.newly_start设置为True，表示Recorder刚刚启动。

然后，函数将self.toolserver_interface_id、self.tool_call_id和self.plan_refine_id都设置为0，用于记录工具服务器接口、工具调用和计划细化的ID。

接下来，函数分别创建self.llm_server_cache、self.tool_server_cache、self.tool_call_cache和self.plan_refine_cache四个空列表，用于缓存LLM服务器、工具服务器、工具调用和计划细化的记录。

最后，函数将self.query_count设置为0，用于记录查询次数。

**注意**：使用该代码时需要注意以下几点：
- record_root_dir参数用于指定运行记录的根目录，默认为"./running_records/"。
- 该函数会根据当前时间和随机字符串生成一个唯一的子目录，用于存储运行记录。
- 函数内部会创建"LLM_inout_pair"和"tool_server_pair"两个子目录，用于存储LLM和工具服务器的运行记录。
- 使用该函数时，需要确保运行记录的根目录存在，并有足够的权限进行创建子目录和文件的操作。
## FunctionDef get_query_id
**get_query_id函数**：该函数的作用是获取查询的id。

该函数首先使用深拷贝将查询计数器的值赋给query_id变量，然后将查询计数器的值加1。最后返回query_id作为查询的id。

该函数没有任何参数。

**注意**：在调用该函数之前，需要确保查询计数器的值已经正确初始化。

**输出示例**：假设查询计数器的初始值为0，调用get_query_id函数后，返回值为1。
## FunctionDef decrease_query_id
**decrease_query_id函数**：该函数的功能是减少查询ID。

该函数用于减少查询ID。在调用该函数时，会将查询计数减1。

**注意**：在使用该代码时需要注意以下几点：
- 该函数只能在ToolServerManager类的实例对象中调用。
- 调用该函数后，查询计数会减少1。
## FunctionDef change_now_task
**change_now_task函数**: 这个函数的功能是改变当前子任务。

这个函数接受一个参数new_subtask_id，它是新子任务的id。在函数内部，它将当前子任务的id（now_subtask_id）设置为new_subtask_id，将工具调用的id（tool_call_id）设置为0，将计划细化的id（plan_refine_id）设置为0。

**注意**: 使用这段代码时需要注意以下几点：
- 确保传入的new_subtask_id是一个整数类型的值。
- 在调用这个函数之后，当前子任务的id将被改变，工具调用的id和计划细化的id将被重置为0。
## FunctionDef regist_plan_modify
**regist_plan_modify函数**：该函数的功能是注册计划修改。

该函数用于注册计划的修改，接收四个参数：refine_function_name（修改函数的名称）、refine_function_input（修改函数的输入）、refine_function_output（修改函数的输出）和plan_after（修改后的计划）。该函数会将修改后的计划记录到文件中。

在函数内部，首先会创建一个目录，用于存储记录文件。然后，使用`open`函数创建一个文件对象，将修改后的计划记录写入文件中。计划的记录以JSON格式保存，包括修改函数的名称、输入、输出以及修改后的计划。最后，通过`json.dump`函数将记录写入文件。

需要注意的是，函数中使用了`os.makedirs`函数创建目录，确保目录存在。同时，使用`json.dump`函数将记录以JSON格式写入文件时，需要指定`indent`参数为2，以便以缩进的形式保存JSON数据。

**注意**：在使用该函数时，需要确保`self.record_root_dir`和`self.now_subtask_id`的值已经正确设置，以便正确创建记录文件的路径。此外，还需要注意确保文件的编码为UTF-8。
## FunctionDef regist_llm_inout
**regist_llm_inout函数**：这个函数的功能是注册llm的输入输出对。

该函数用于注册llm的输入输出对。它接受以下参数：
- llm_query_id（int）：llm查询的id。
- messages（Any）：通信的消息。
- functions（list，可选）：使用的函数列表。
- function_call（Any，可选）：调用的函数。
- model（Any，可选）：使用的模型。
- stop（bool，可选）：一个标志，指示是否停止。
- output_data（Any，可选）：输出数据。
- other_args（dict，可选）：其他参数。

该函数首先将llm的输入输出对记录到文件中。它创建一个包含输入和输出信息的字典，并将其转换为JSON格式后写入文件。然后，它将记录添加到llm_server_cache列表中，并使用logger.typewriter_log函数打印日志信息。

在项目中的XAgent/ai_functions/request/obj_generator.py文件中的chatcompletion函数中调用了regist_llm_inout函数。在调用之前，先获取了llm_query_id，并将其作为参数传递给regist_llm_inout函数。调用regist_llm_inout函数后，将llm_query_id、copyed_kwargs和response作为参数传递给regist_llm_inout函数。

**注意**：在使用regist_llm_inout函数时，需要注意传递正确的参数，并确保llm_query_id的唯一性。
## FunctionDef query_llm_inout
**query_llm_inout函数**：该函数的功能是查询llm的输入和输出对。

该函数接受以下参数：
- llm_query_id（int）：llm查询的id。
- messages（Any）：通信的消息。
- functions（list，可选）：使用的函数列表。
- function_call（Any，可选）：调用的函数。
- model（Any，可选）：使用的模型。
- stop（bool，可选）：一个标志，指示是否停止。
- other_args（dict，可选）：其他参数。

该函数的返回值为任意类型的输出数据。

该函数首先判断是否是新启动的状态，如果是，则返回None。接着，将输入数据以字典形式存储在input_data变量中。然后，判断llm_query_id是否超过了llm_server_cache的长度，如果是，则打印日志信息并返回None。接下来，将llm_query_id对应的缓存数据存储在cache变量中。如果input_data与cache["input"]相等，则打印日志信息并返回cache["output"]。否则，返回None。

该函数在以下文件中被调用：
文件路径：XAgent/ai_functions/request/obj_generator.py
调用代码如下：
```python
def chatcompletion(self, *, schema_validation=True, **kwargs):
    """
    处理聊天完成请求并获取响应。

    参数：
        kwargs：请求数据参数。

    返回值：
        从AI服务调用中检索到的字典格式响应。

    异常：
        Exception：处理请求时发生错误。
        NotImplementedError：接收到的请求类型当前未实现。
    """
    
    request_type = kwargs.pop('request_type', CONFIG.default_request_type)
    for k in list(kwargs.keys()):
        if kwargs[k] is None:
            kwargs.pop(k)
    
    llm_query_id = recorder.get_query_id()
    try:   
        copyed_kwargs = deepcopy(kwargs)
        if (response := recorder.query_llm_inout(llm_query_id=llm_query_id, **copyed_kwargs)) is None:
            response = self._get_chatcompletion_request_func(request_type)(**kwargs)
        recorder.regist_llm_inout(llm_query_id=llm_query_id, **copyed_kwargs, output_data=response)
    except Exception as e:
        traceback.print_exc()
        logger.typewriter_log(f"chatcompletion error: {e}", Fore.RED)
        recorder.decrease_query_id()
        raise e

    if schema_validation:
        # refine the response
        match request_type:
            case 'openai':                
                response = self.function_call_refine(kwargs, response)
            case 'xagent':
                pass
            case _:
                raise NotImplementedError(f"Request type {request_type} not implemented")
    
    return response
```

**注意**：关于代码使用的注意事项。

**输出示例**：模拟代码返回值的可能外观。
## FunctionDef regist_tool_call
**regist_tool_call函数**：该函数的功能是注册工具调用。

该函数用于注册工具的调用信息，包括工具的名称、输入、输出、状态码以及思考数据。具体参数说明如下：

- tool_name (str)：工具的名称。
- tool_input (Any)：工具的输入。
- tool_output (Any)：工具的输出。
- tool_status_code (int)：工具的状态码。
- thought_data (Any, 可选)：思考数据。

函数内部首先创建一个目录，用于存储记录的信息。然后将工具的调用信息以JSON格式写入文件中。具体步骤如下：

1. 使用`os.makedirs`函数创建目录，目录路径为`self.record_root_dir`和`self.now_subtask_id`的组合。如果目录已存在，则不进行任何操作。
2. 使用`open`函数打开文件，文件路径为`self.record_root_dir`、`self.now_subtask_id`和`tool_{self.tool_call_id:05d}.json`的组合。以写入模式打开文件，并指定编码为UTF-8。
3. 创建一个字典`tool_record`，包含工具的名称、输入、输出和状态码。使用`dump_common_things`函数对这些信息进行序列化处理。
4. 如果存在思考数据，则将思考数据添加到`tool_record`字典中，同样使用`dump_common_things`函数进行序列化处理。
5. 使用`json.dump`函数将`tool_record`字典以缩进为2的格式写入文件中，同时确保不进行ASCII编码。
6. 增加`self.tool_call_id`的值，用于记录下一个工具调用的ID。

**注意**：在使用该函数时，需要确保`self.record_root_dir`和`self.now_subtask_id`的值已经正确设置，并且`dump_common_things`函数能够正确序列化工具的输入、输出和状态码。
## FunctionDef regist_tool_server
**regist_tool_server函数**：这个函数的功能是注册工具服务器。

该函数的作用是将工具服务器的相关信息记录下来，并保存到文件中。具体来说，该函数接收四个参数：url（服务器的URL）、payload（工具的输入参数）、tool_output（工具的输出结果）和response_status_code（响应状态码）。然后，函数将这些信息以JSON格式保存到文件中。

在函数内部，首先使用`open`函数打开一个文件，将文件路径设置为`self.record_root_dir`下的`tool_server_pair`目录，并以`self.toolserver_interface_id:05d`作为文件名。然后，创建一个字典`tool_record`，将传入的参数以及一些其他信息存储在其中。接下来，使用`json.dump`函数将`tool_record`以缩进为2的格式写入文件中。

最后，将`self.toolserver_interface_id`加1，以便下一次记录时使用新的文件名。

**注意**：在使用该函数时，需要确保传入正确的参数，并且`self.record_root_dir`和`self.toolserver_interface_id`的值已经正确设置。另外，需要注意文件的编码格式为UTF-8。
## FunctionDef query_tool_server_cache
**query_tool_server_cache函数**：该函数的功能是查询工具服务器。

该函数接受两个参数，url和payload。url是服务器的URL地址，payload是要发送的数据。

函数首先会检查是否是新启动的工具服务器，如果是，则返回None。然后会检查toolserver_interface_id是否超过了工具服务器缓存的长度，如果超过了，则返回None。

接下来，函数会获取tool_server_cache中对应toolserver_interface_id的缓存数据。

函数会比较缓存数据中的url和payload是否与传入的参数相匹配，如果匹配，则返回缓存数据中的工具服务器响应结果和响应状态码。

如果没有匹配的缓存数据，则返回None。

**注意**：使用该代码时需要注意以下几点：
- 需要传入正确的url和payload参数。
- 需要确保工具服务器缓存中存在对应的数据。

**输出示例**：模拟代码返回值的可能外观。

{
    "tool_output": "工具服务器响应结果",
    "response_status_code": "响应状态码"
}
## FunctionDef regist_query
**regist_query函数**：该函数的功能是注册一个查询。

该函数接受一个名为query的参数，该参数是一个AutoGPTQuery对象，表示要注册的查询。

函数内部通过打开一个名为"query.json"的文件，并以写入模式打开，将query对象转换为JSON格式，并写入文件中。写入时使用了UTF-8编码，并设置了缩进为2个空格，确保写入的内容是可读的，并且不使用ASCII编码。

**注意**：使用该代码时需要注意以下几点：
- 确保self.record_root_dir变量指向正确的目录，以便正确保存查询文件。
- 确保query对象是AutoGPTQuery类型的对象，否则可能会导致写入的内容不符合预期。
## FunctionDef get_query
**get_query函数**：该函数的功能是获取已注册的查询。

该函数用于从记录中获取已注册的查询，并返回该查询。在函数内部，首先使用logger.typewriter_log函数记录一条日志，表示正在从记录中加载查询。然后，函数返回已注册的查询。

**注意**：使用该函数前需要确保已注册查询。

**输出示例**：返回已注册的查询对象。
## FunctionDef regist_config
**regist_config函数**：这个函数的功能是注册一个配置。

该函数接受一个名为config的参数，类型为XAgentConfig，表示要注册的配置。

函数内部通过打开一个名为config.yml的文件，并将config对象转换为字典形式后写入文件中。写入时使用了yaml.safe_dump函数将字典转换为yaml格式，并设置了参数allow_unicode=True以支持中文字符。

**注意**：使用该代码时需要注意以下几点：
- 确保record_root_dir变量指定的目录存在，并且有写入权限。
- 确保XAgentConfig对象的to_dict方法能够正确地将配置转换为字典形式。
## FunctionDef get_config
**get_config函数**：该函数的功能是获取已注册的配置。

该函数用于从记录中获取已注册的配置，并返回一个XAgentConfig对象。在函数内部，首先使用logger.typewriter_log函数记录一条日志，该日志内容为"load a config from Record"，并设置日志颜色为蓝色。然后，函数返回self.config，即已注册的配置。

**注意**：使用该函数前需要确保已注册配置，并且需要导入XAgentConfig类。

**输出示例**：返回一个已注册的配置对象XAgentConfig。
## FunctionDef regist_father_info
**regist_father_info函数**: 这个函数的功能是注册父信息。

该函数接受一个参数record_dir，表示记录的目录。函数的作用是将记录的目录信息写入到文件中。

在函数内部，使用open函数创建一个文件，文件名为"This-Is-A-Reload-Run.yml"，并以写入模式打开。然后使用yaml.safe_dump函数将record_dir的值以字典的形式写入文件中。写入的内容是一个字典，包含一个键值对，键为"load_record_dir"，值为record_dir。最后关闭文件。

**注意**: 使用该函数时需要传入正确的record_dir参数，确保目录存在且具有写入权限。
## FunctionDef load_from_disk
**load_from_disk函数**：该函数的功能是从磁盘中加载记录。

该函数接受一个参数record_dir，表示记录的目录。

函数首先使用logger.typewriter_log函数打印一条日志，指示正在从磁盘记录中加载数据，并覆盖所有现有的配置信息。日志的内容为"load from a disk record, overwrite all the existing config-info"，使用蓝色字体显示，并附带record_dir作为参数。

接下来，函数调用self.regist_father_info函数，将record_dir作为参数传递给该函数。

然后，函数将self.newly_start设置为False。

接下来，函数遍历record_dir目录下的所有文件和文件夹。对于每个文件夹，函数根据文件夹的名称进行不同的处理。

如果文件夹的名称为"query.json"，则打开该文件并使用json.load函数将其内容加载为self.query_json。然后，函数调用AutoGPTQuery.from_json函数，将self.query_json转换为AutoGPTQuery对象，并将其赋值给self.query。

如果文件夹的名称为"config.yml"，则调用CONFIG.reload函数，将该文件的路径作为参数传递给该函数。

如果文件夹的名称为"LLM_inout_pair"，则遍历该文件夹下的所有文件。对于每个文件，函数解析文件名中的数字作为inout_id，并使用json.load函数将文件内容加载为llm_pair。然后，将llm_pair存储在self.llm_server_cache列表的相应位置。

如果文件夹的名称为"tool_server_pair"，则遍历该文件夹下的所有文件。对于每个文件，函数解析文件名中的数字作为inout_id，并使用json.load函数将文件内容加载为tool_pair。然后，将tool_pair存储在self.tool_server_cache列表的相应位置。

如果文件夹的名称为其他名称，并且该文件夹是一个子文件夹，则遍历该子文件夹下的所有文件。对于每个文件，函数根据文件名的前缀进行不同的处理。如果文件名以"plan_refine"开头，则使用json.load函数将文件内容加载为plan_refine，并将其添加到self.plan_refine_cache列表中。如果文件名以"tool"开头，则使用json.load函数将文件内容加载为tool_call，并将其添加到self.tool_call_cache列表中。否则，抛出NotImplementedError异常。

**注意**：在使用该函数时需要注意以下几点：
- 函数需要传入一个有效的记录目录，否则会出现错误。
- 记录目录中需要包含特定的文件和文件夹，否则函数无法正确加载数据。
- 函数会覆盖所有现有的配置信息，需要谨慎使用。
***
