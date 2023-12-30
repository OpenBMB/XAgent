# FunctionDef dump_common_things
**dump_common_things函数**: 这个函数的功能是将对象转换为可序列化的形式。

该函数接受一个对象作为参数，并根据对象的类型进行不同的处理。如果对象的类型是字符串、整数、浮点数或布尔值之一，则直接返回该对象。如果对象是字典类型，则递归地对字典的键和值进行处理，并返回处理后的字典。如果对象是列表类型，则递归地对列表中的每个元素进行处理，并返回处理后的列表。

如果对象具有名为"to_json"的方法，并且该方法是可调用的，则调用该方法并返回其结果。

该函数的主要作用是将复杂的对象转换为可序列化的形式，以便在存储或传输数据时使用。

**注意**: 
- 该函数对于复杂对象的处理是递归的，因此需要确保对象的属性和方法能够正确地处理。
- 该函数假设对象的属性和方法都是可序列化的，否则可能会导致错误或异常。

**输出示例**:
- 示例1:
  ```
  object = "Hello World"
  result = dump_common_things(object)
  print(result)
  输出: "Hello World"
  ```

- 示例2:
  ```
  object = {"name": "John", "age": 30}
  result = dump_common_things(object)
  print(result)
  输出: {"name": "John", "age": 30}
  ```

- 示例3:
  ```
  object = [1, 2, 3, {"name": "John"}]
  result = dump_common_things(object)
  print(result)
  输出: [1, 2, 3, {"name": "John"}]
  ```

- 示例4:
  ```
  class Person:
      def __init__(self, name):
          self.name = name
      def to_json(self):
          return {"name": self.name}
  
  object = Person("John")
  result = dump_common_things(object)
  print(result)
  输出: {"name": "John"}
  ```

以上是对dump_common_things函数的详细分析和说明。该函数的主要作用是将对象转换为可序列化的形式，以便在存储或传输数据时使用。需要注意的是，该函数对于复杂对象的处理是递归的，因此需要确保对象的属性和方法都是可序列化的。
***
# FunctionDef get_db
**get_db函数**：该函数的功能是提供一个围绕一系列操作的事务范围。

该函数使用了一个上下文管理器（context manager）来创建一个数据库会话（session），并在操作完成后进行提交或回滚。具体流程如下：

1. 创建一个数据库会话（session）。
2. 使用yield语句将会话（session）作为生成器的返回值，使得函数可以在yield处暂停执行，并在下次调用时从yield处继续执行。
3. 在try块中执行yield语句，将会话（session）作为生成器的返回值返回给调用者，并等待调用者继续执行。
4. 如果try块中的代码执行出现异常，则执行except块中的代码，回滚会话（session）中的操作，并重新抛出异常。
5. 无论try块中的代码是否出现异常，都会执行finally块中的代码，关闭会话（session）。

**注意**：在使用get_db函数时，需要将其放在with语句中，以确保会话（session）能够正确地进行提交或回滚，并在使用完毕后关闭会话（session）。
***
# ClassDef RunningRecoder
**RunningRecoder函数**：这个类的功能是记录程序的运行序列，包括程序查询状态和配置数据。

该类具有以下方法：

- `__init__(self, record_id: str, newly_start=True, root_dir=None, logger: Logger=None)`：初始化方法，用于创建RunningRecoder对象。参数`record_id`表示记录的唯一标识符，`newly_start`表示是否是全新启动的程序，`root_dir`表示记录的根目录，`logger`表示日志记录器。

- `change_now_task(self, new_subtask_id)`：更改当前任务的方法。参数`new_subtask_id`表示新的子任务的ID。

- `generate_record(self, current, node_id, node_type, data)`：生成记录的方法。参数`current`表示当前子任务的ID，`node_id`表示节点的ID，`node_type`表示节点的类型，`data`表示要记录的数据。

- `regist_plan_modify(self, refine_function_name, refine_function_input, refine_function_output, plan_after)`：注册一个plan_refine的记录的方法。参数`refine_function_name`表示refine函数的名称，`refine_function_input`表示refine函数的输入，`refine_function_output`表示refine函数的输出，`plan_after`表示refine后的计划。

- `regist_llm_inout(self, messages, functions, function_call, model, stop, other_args, output_data)`：注册一个llm_inout的记录的方法。参数`messages`表示消息列表，`functions`表示函数列表，`function_call`表示函数调用，`model`表示模型，`stop`表示停止标志，`other_args`表示其他参数，`output_data`表示输出数据。

- `query_llm_inout(self, restrict_cache_query, messages, functions, function_call, model, stop, other_args)`：查询llm_inout记录的方法。参数`restrict_cache_query`表示是否要求llm_interface_id也一样，`messages`表示消息列表，`functions`表示函数列表，`function_call`表示函数调用，`model`表示模型，`stop`表示停止标志，`other_args`表示其他参数。

- `regist_tool_call(self, tool_name, tool_input, tool_output, tool_status_code, thought_data=None)`：注册一个tool_call的记录的方法。参数`tool_name`表示工具的名称，`tool_input`表示工具的输入，`tool_output`表示工具的输出，`tool_status_code`表示工具的状态码，`thought_data`表示思考数据。

- `regist_tool_server(self, url, payload, tool_output, response_status_code)`：注册一个tool_server的记录的方法。参数`url`表示服务器的URL，`payload`表示工具的payload，`tool_output`表示工具的输出，`response_status_code`表示响应的状态码。

- `query_tool_server_cache(self, url, payload)`：查询tool_server缓存的方法。参数`url`表示服务器的URL，`payload`表示工具的payload。

- `regist_query(self, query)`：记录查询信息的方法。参数`query`表示查询对象。

- `get_query(self)`：从数据库中获取查询信息的方法。

- `regist_config(self, config: XAgentConfig)`：记录配置信息的方法。参数`config`表示配置对象。

- `get_config(self)`：从数据库中获取运行配置的方法。

- `load_from_db(self, record_id)`：从数据库中加载记录的方法。参数`record_id`表示记录的ID。

**注意**：该类用于记录程序的运行序列和配置信息，以及查询和工具调用的记录。可以通过调用不同的方法来注册和查询记录。

**输出示例**：
```
RunningRecoder对象已成功创建。
```
## FunctionDef __init__
**__init__函数**：这个函数的作用是初始化一个Recorder对象。

在代码中，我们可以看到__init__函数有以下几个参数：
- record_id: str类型，表示记录的ID。
- newly_start: bool类型，表示是否是全新启动的Recorder对象。
- root_dir: str类型，表示记录的根目录。
- logger: Logger类型，表示记录器的日志对象。

在函数内部，首先将传入的参数赋值给对应的实例变量。然后，通过判断记录的根目录是否存在，如果不存在则创建该目录。

接下来，初始化一些实例变量，包括query和config，它们分别用于存储查询和配置信息。

然后，初始化一些用于记录接口和调用的ID的实例变量，包括llm_interface_id、toolserver_interface_id、tool_call_id和plan_refine_id。

接着，初始化一些用于缓存的列表，包括llm_server_cache、tool_server_cache、tool_call_cache和plan_refine_cache。

最后，初始化一个用于记录当前子任务ID的实例变量now_subtask_id。

**注意**：在使用这段代码时，需要注意传入正确的参数，并确保记录的根目录存在。
## FunctionDef change_now_task
**change_now_task函数**: 这个函数的功能是改变当前任务。

该函数用于改变当前任务的子任务ID，以便在工作流中处理下一个子任务。它接受一个新的子任务ID作为参数，并将当前子任务ID、工具调用ID和计划细化ID重置为0。这样可以确保在处理下一个子任务时，这些变量的初始状态是正确的。

**注意**: 在使用这段代码时需要注意以下几点：
- 确保传入的新子任务ID是有效的，并且与工作流中的子任务ID相对应。
- 在调用这个函数之前，确保已经初始化了相关的变量，以免出现意外的结果。
- 这个函数只负责改变当前任务的子任务ID，不涉及其他与任务相关的操作。
## FunctionDef generate_record
**generate_record函数**：此函数的功能是生成一个记录。

该函数接受四个参数：current（当前子任务ID）、node_id（节点ID）、node_type（节点类型）和data（数据）。函数首先使用logger对象将一些信息打印到日志中，然后将data转换为JSON字符串，并对其中的敏感信息进行脱敏处理。最后，函数返回一个XAgentRunningRecord对象，其中包含了记录的各个字段。

该函数在以下文件中被调用：
- XAgent/recorder.py：regist_plan_modify函数中调用了generate_record函数，用于注册一个plan_refine的记录。
- XAgent/recorder.py：regist_llm_inout函数中调用了generate_record函数，用于注册一个llm_inout的记录。
- XAgent/recorder.py：regist_tool_call函数中调用了generate_record函数，用于注册一个tool_call的记录。
- XAgent/recorder.py：regist_tool_server函数中调用了generate_record函数，用于注册一个tool_server的记录。
- XAgent/recorder.py：regist_query函数中调用了generate_record函数，用于注册一个query的记录。
- XAgent/recorder.py：regist_config函数中调用了generate_record函数，用于注册一个config的记录。

**注意**：在使用该函数时需要注意以下几点：
- 函数的四个参数都是必填项，不能省略。
- data参数必须是一个可转换为JSON格式的对象。

**输出示例**：以下是该函数可能返回值的示例：
```
{
    "record_id": 1,
    "current": 1,
    "node_id": 1,
    "node_type": "PLAN_REFINE",
    "data": {
        "refine_function_name": "refine_function",
        "refine_function_input": "input_data",
        "refine_function_output": "output_data",
        "plan_after": "new_plan"
    },
    "create_time": "2022-01-01 00:00:00",
    "update_time": "2022-01-01 00:00:00",
    "is_deleted": false
}
```
## FunctionDef regist_plan_modify
**regist_plan_modify函数**：该函数的功能是注册一个plan_refine的记录。

该函数接受四个参数：refine_function_name，refine_function_input，refine_function_output和plan_after。其中，refine_function_name表示refine函数的名称，refine_function_input表示refine函数的输入，refine_function_output表示refine函数的输出，plan_after表示refine函数执行后的plan。

在函数内部，首先创建一个plan_refine_record字典，包含了refine_function_name、refine_function_input、refine_function_output和plan_after这四个字段。这些字段的值通过调用dump_common_things函数对参数进行序列化处理。

接下来，调用self.generate_record函数生成一个记录。该记录包含了当前子任务的ID（current）、plan_refine的节点ID（node_id）、节点类型（node_type）和plan_refine_record数据。

然后，通过调用get_db函数获取数据库连接，并使用RunningRecordCRUD的insert_record方法将记录插入数据库。

最后，将plan_refine_id加1，以便下次注册时使用。

**注意**：在使用该函数时需要注意以下几点：
- 确保传入的参数refine_function_name、refine_function_input、refine_function_output和plan_after的类型正确。
- 确保数据库连接正常，并且RunningRecordCRUD的insert_record方法能够正确插入记录。
- 每次注册plan_refine记录后，需要将plan_refine_id加1，以保证下次注册时使用的ID是唯一的。
## FunctionDef regist_llm_inout
**regist_llm_inout函数**: 这个函数的作用是注册一个llm_inout的记录。

该函数接受以下参数：
- messages: 一个消息列表，包含了与当前记录相关的所有消息。
- functions: 一个函数列表，包含了与当前记录相关的所有函数。
- function_call: 一个函数调用列表，包含了与当前记录相关的所有函数调用。
- model: 一个模型对象，包含了与当前记录相关的模型信息。
- stop: 一个布尔值，表示当前记录是否停止。
- other_args: 一个其他参数列表，包含了与当前记录相关的其他参数。
- output_data: 一个输出数据对象，包含了与当前记录相关的输出数据。

该函数首先创建了一个llm_inout_record字典，其中包含了输入和输出的相关信息。输入信息包括了messages、functions、function_call、model、stop和other_args，这些信息都通过dump_common_things函数进行了转换。输出信息则通过dump_common_things函数将output_data转换为字符串。

接下来，函数调用了generate_record方法，生成了一个record对象。该record对象包含了当前子任务的ID、llm_interface_id、RecorderTypeEnum.LLM_INPUT_PAIR和llm_inout_record。

然后，函数使用get_db函数获取数据库连接，并调用RunningRecordCRUD的insert_record方法将record插入到数据库中。

最后，函数将llm_interface_id加1，以便下次记录时使用。

**注意**: 使用该代码时需要注意以下几点：
- 确保传入的参数类型正确，否则可能会导致错误。
- 确保数据库连接正常，否则无法插入记录。
## FunctionDef query_llm_inout
**query_llm_inout函数**：这个函数的作用是查询LLM的输入输出。

该函数接受以下参数：
- restrict_cache_query：是否要求LLM接口ID也一样。
- messages：消息列表。
- functions：函数列表。
- function_call：函数调用列表。
- model：模型列表。
- stop：停止标志列表。
- other_args：其他参数列表。

该函数首先判断是否是新启动的LLM，如果是，则返回None。

然后，将输入数据以字典形式存储在input_data变量中，包括了messages、functions、function_call、model、stop和other_args。

接下来，遍历llm_server_cache列表中的缓存项，判断输入数据是否与缓存项的input字段相等。如果相等，则根据restrict_cache_query的值判断是否要求llm_interface_id也一样。如果要求一样且llm_interface_id不一样，则继续遍历下一个缓存项。如果不要求一样或者llm_interface_id一样，则返回缓存项的output字段。

如果遍历完所有缓存项后仍未找到匹配的缓存项，则返回None。

**注意**：在使用该代码时需要注意以下几点：
- 需要提供正确的参数。
- 需要正确设置restrict_cache_query参数。
- 需要正确设置llm_interface_id参数。

**输出示例**：返回缓存项的output字段的值。
## FunctionDef regist_tool_call
**regist_tool_call函数**：这个函数的作用是代管tool server上的所有操作。

该函数接受以下参数：
- tool_name：工具的名称。
- tool_input：工具的输入。
- tool_output：工具的输出。
- tool_status_code：工具的状态码。
- thought_data：思考数据（可选）。

该函数的主要功能是生成工具调用的记录，并将记录插入到运行记录中。具体步骤如下：
1. 将工具的名称、输入、输出和状态码存储到tool_record字典中。
2. 如果存在思考数据，则将思考数据存储到tool_record字典中。
3. 调用generate_record函数生成记录，并传入当前子任务ID、工具调用ID、记录类型和数据。
4. 使用get_db函数获取数据库连接，并调用RunningRecordCRUD的insert_record方法将记录插入到数据库中。
5. 增加工具调用ID的值。

**注意**：在使用该函数时，需要注意以下几点：
- 需要提供正确的工具名称、输入、输出和状态码。
- 如果有思考数据，需要将其传入thought_data参数。
- 在调用该函数之前，需要确保已经正确配置了数据库连接。
- 在调用该函数之后，可以通过查询数据库来获取工具调用的记录。
## FunctionDef regist_tool_server
**regist_tool_server函数**：该函数用于注册工具服务器。

该函数接受以下参数：
- url（str）：服务器的URL。
- payload（Any）：工具的payload。
- tool_output（Any）：工具的输出。
- response_status_code（int）：响应状态码。

该函数的作用是将工具服务器的信息注册到记录器中，并将记录插入到运行记录中。

使用示例：
```python
regist_tool_server(url, payload, tool_output, response_status_code)
```

**注意**：在使用该函数时，需要确保传入正确的参数，并且保证服务器的URL、payload、工具输出和响应状态码的正确性。
## FunctionDef query_tool_server_cache
**query_tool_server_cache函数**：该函数用于查询工具服务器缓存。

该函数的作用是查询工具服务器缓存，根据给定的URL和payload参数，从缓存中查找匹配的工具服务器响应。如果找到匹配的缓存，则返回缓存中的工具服务器响应；如果未找到匹配的缓存，则返回None。

函数参数说明：
- url：工具服务器的URL。
- payload：请求的参数。

函数内部逻辑说明：
1. 首先判断是否是新启动的工具服务器，如果是，则直接返回None。
2. 如果工具服务器缓存为空，则从数据库中获取工具服务器记录，并将其转换为JSON格式的列表，存储在self.tool_server_cache中。
3. 遍历self.tool_server_cache列表，逐个比较缓存中的URL和payload与给定的url和payload是否匹配。如果匹配，则打印匹配的工具服务器响应，并返回该响应。
4. 如果遍历完整个self.tool_server_cache列表仍未找到匹配的缓存，则返回None。

**注意**：在使用该函数时，需要确保工具服务器缓存已经被正确初始化，并且传入的url和payload参数与缓存中的URL和payload格式一致。

**输出示例**：假设工具服务器缓存中存在匹配的缓存，返回工具服务器响应的示例：
```
get a tool_server response from Record: {"output": "example output"}
```
## FunctionDef regist_query
**regist_query函数**：该函数的功能是记录query的相关信息。

该函数接受一个参数query，用于记录相关信息。首先，通过调用generate_record函数生成一个记录对象record，该对象包含了当前子任务ID、节点ID、节点类型和query的JSON数据。然后，使用get_db函数获取数据库连接，并调用RunningRecordCRUD的insert_record方法将记录插入数据库。

该函数在以下文件中被调用：
文件路径：XAgent/core.py
调用代码如下：
```python
def resister_recorder(self, param: XAgentParam):
    """
    register a recorder to the core components
    """
    self.recorder = RunningRecoder(
        record_id=self.interaction.base.interaction_id,
        newly_start=param.newly_created,
        root_dir=self.base_dir,
        logger=self.logger
    )
    if param.newly_created:
        self.recorder.regist_query(param.query)
        self.recorder.regist_config(param.config)
    else:
        self.recorder.load_from_db(self.interaction.base.recorder_root_dir)
        self.recorder.regist_query(param.query)
        self.recorder.regist_config(param.config)

    XAgentCoreComponents.global_recorder = self.recorder
```
该函数在resister_recorder函数中被调用，用于向核心组件注册一个记录器。首先，创建一个RunningRecoder对象，传入记录ID、是否新创建、根目录和日志记录器等参数。然后，根据是否新创建的标志，调用记录器的regist_query方法和regist_config方法注册query和config。最后，将记录器赋值给全局变量XAgentCoreComponents.global_recorder。

**注意**：使用该函数时需要注意以下几点：
- 需要提供一个有效的query参数。
- 在调用该函数之前，需要确保数据库连接已经建立。
- 调用该函数后，相关信息将被记录到数据库中。
## FunctionDef get_query
**get_query函数**：该函数的功能是从数据库中获取查询。

该函数首先使用`get_db()`函数获取数据库连接，并在`with`语句块中使用该连接。然后，通过调用`RunningRecordCRUD.get_record_by_type()`函数从数据库中获取记录。该函数接受以下参数：
- `db`：数据库连接对象。
- `record_id`：记录ID。
- `node_id`：节点ID，此处为0。
- `node_type`：节点类型，此处为RecorderTypeEnum.QUERY。

获取到的记录存储在`records`变量中。接下来，通过调用`AutoGPTQuery.from_json()`函数将记录中的数据转换为`AutoGPTQuery`对象，并将其赋值给`self.query`变量。最后，函数返回`self.query`。

**注意**：使用该函数前需要确保数据库连接已经建立，并且需要传入正确的记录ID、节点ID和节点类型。

**输出示例**：假设从数据库中获取的记录数据为`{"query": "SELECT * FROM table"}`，则函数返回的`self.query`对象为`AutoGPTQuery(query="SELECT * FROM table")`。
## FunctionDef regist_config
**regist_config函数**: 这个函数的功能是记录config的相关信息。

这个函数的作用是将传入的config对象的相关信息记录下来，并保存到数据库中。具体实现过程如下：

1. 首先，通过调用self.generate_record方法生成一个记录对象record，该记录对象包含了当前子任务的ID（current）、节点ID（node_id）、节点类型（node_type）和config对象的字典形式数据（data）。

2. 然后，通过调用get_db函数获取数据库连接，并将record插入到数据库中，实现记录的持久化。

在项目中的调用情况如下：

文件路径：XAgent/core.py
调用代码如下：
```python
def resister_recorder(self, param: XAgentParam):
    """
    register a recorder to the core components
    """
    self.recorder = RunningRecoder(
        record_id=self.interaction.base.interaction_id,
        newly_start=param.newly_created,
        root_dir=self.base_dir,
        logger=self.logger
    )
    if param.newly_created:
        self.recorder.regist_query(param.query)
        self.recorder.regist_config(param.config)
    else:
        self.recorder.load_from_db(self.interaction.base.recorder_root_dir)
        self.recorder.regist_query(param.query)
        self.recorder.regist_config(param.config)

    XAgentCoreComponents.global_recorder = self.recorder
```

这段代码的作用是将一个recorder对象注册到核心组件中。在注册过程中，会根据传入的参数判断是否为新创建的recorder，如果是，则会先注册查询参数（param.query）和config参数（param.config），然后将recorder对象赋值给XAgentCoreComponents.global_recorder；如果不是新创建的recorder，则会从数据库中加载recorder，并进行相同的注册操作。

**注意**：在使用regist_config函数时，需要传入一个XAgentConfig对象作为参数。
## FunctionDef get_config
**get_config函数**：该函数的功能是从数据库中获取运行配置。

该函数使用了一个数据库操作函数`get_db()`来获取数据库连接，然后使用`RunningRecordCRUD.get_record_by_type()`函数从数据库中获取指定类型的记录。具体来说，该函数会根据`record_id`、`node_id`和`node_type`参数来查询数据库中的记录。查询结果是一个记录列表，然后通过`json.loads()`函数将第一个记录的数据解析为JSON格式。

**注意**：使用该函数前需要确保数据库连接已经建立，并且需要传入正确的`record_id`参数。

**输出示例**：模拟该函数返回值的可能外观。

```python
{
    "key1": "value1",
    "key2": "value2",
    ...
}
```
## FunctionDef load_from_db
**load_from_db函数**: 这个函数的功能是从本地文件夹加载record，用于后面的直接复现。

该函数接受一个record_id作为参数，用于指定要加载的record的ID。函数首先将self.newly_start设置为False，表示不是新的record。

然后，通过调用get_db()函数获取数据库连接，并使用RunningRecordCRUD的get_record_by_type方法从数据库中获取指定record_id的记录。

接下来，对于每个获取到的record，根据其node_type的不同，将其data加载到相应的缓存中。具体的加载方式如下：
- 如果node_type为RecorderTypeEnum.QUERY，则将record的data转换为AutoGPTQuery对象，并将其赋值给self.query。
- 如果node_type为RecorderTypeEnum.CONFIG，则创建一个XAgentConfig对象，并使用record的data更新该对象的属性。
- 如果node_type为RecorderTypeEnum.LLM_INPUT_PAIR，则将record的data添加到self.llm_server_cache列表中。
- 如果node_type为RecorderTypeEnum.TOOL_SERVER_PAIR，则将record的data添加到self.tool_server_cache列表中。
- 如果node_type为RecorderTypeEnum.PLAN_REFINE，则将record的data添加到self.plan_refine_cache列表中。
- 如果node_type为RecorderTypeEnum.TOOL_CALL，则将record的data添加到self.tool_call_cache列表中。
- 如果node_type为其他类型，则抛出NotImplementedError异常。

**注意**: 使用该函数时需要确保传入正确的record_id参数，并且该record_id对应的记录存在于数据库中。
***
