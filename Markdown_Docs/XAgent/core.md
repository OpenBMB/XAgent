# ClassDef XAgentParam
**XAgentParam函数**: 这个类的功能是XAgent参数。

XAgentParam是一个抽象基类，用于定义XAgent的参数。它具有以下属性和方法：

- 属性：
  - config：XAgent的配置信息。
  - query：XAgent的查询对象。
  - newly_created：一个布尔值，表示是否是新创建的XAgent。

- 方法：
  - `__init__(self, config=None, query: BaseQuery = None, newly_created: bool = True) -> None`：初始化XAgentParam对象。可以传入config、query和newly_created参数，分别用于设置XAgent的配置信息、查询对象和新创建标志。

  - `build_query(self, query: dict)`：构建查询对象。接受一个字典作为参数，用于构建AutoGPTQuery对象，并将其赋值给query属性。

  - `build_config(self, config)`：构建配置信息。接受一个config对象作为参数，并将其赋值给config属性。

**注意**：在使用XAgentParam类时，可以通过传入config、query和newly_created参数来初始化对象，并使用build_query和build_config方法来构建查询对象和配置信息。
## FunctionDef build_query
**build_query函数**：此函数的功能是构建查询。

该函数接受一个名为query的字典作为参数，并使用该参数构建一个AutoGPTQuery对象，并将其赋值给self.query属性。

**注意**：在使用此代码时需要注意以下几点：
- query参数必须是一个字典类型。
- 构建的AutoGPTQuery对象将被赋值给self.query属性，可以在函数外部访问该属性。
## FunctionDef build_config
**build_config函数**：这个函数的功能是构建配置。

该函数接受一个config参数，并将其赋值给self.config。这个函数没有返回值。

在XAgentServer/server.py文件中的interact函数中调用了build_config函数。在调用之前，先重新加载配置文件，然后根据传入的参数args构建查询参数xagent_param，并调用xagent_param的build_config方法将config配置传入。最后，通过XAgentCoreComponents类的实例xagent_core调用build方法，将xagent_param和interaction作为参数传入，构建XAgent核心组件。

需要注意的是，build_config函数没有返回值。

**注意**：在使用该函数时需要注意以下几点：
- 该函数需要传入一个config参数，确保参数的正确性和完整性。
- 该函数没有返回值，只是将传入的config参数赋值给self.config属性。
***
# ClassDef XAgentCoreComponents
**XAgentCoreComponents函数**: 这个类的功能是XAgent核心组件集，它包含了XAgent的核心组件，用于处理交互、记录运行记录、与工具服务接口通信、处理功能、管理工作记忆、调度代理、与向量数据库接口通信等。

该类的构造函数初始化了所有的组件，并提供了注册和启动这些组件的方法。以下是该类的主要方法和功能：

- `register_interaction(interaction: XAgentInteraction)`: 注册一个交互对象到核心组件中。
- `register_logger()`: 注册一个日志记录器到核心组件中。
- `resister_recorder(param: XAgentParam)`: 注册一个运行记录器到核心组件中。
- `register_toolserver_interface(param: XAgentParam)`: 注册一个工具服务接口到核心组件中。
- `register_function_handler(config)`: 注册一个功能处理器到核心组件中。
- `register_working_memory_function()`: 注册一个工作记忆代理到核心组件中。
- `register_agent_dispatcher(param: XAgentParam)`: 注册一个代理调度器到核心组件中。
- `register_vector_db_interface()`: 注册一个向量数据库接口到核心组件中。
- `register_all(param: XAgentParam, interaction: XAgentInteraction)`: 注册所有组件到核心组件中。
- `build(param: XAgentParam, interaction: XAgentInteraction)`: 构建所有组件。
- `start()`: 启动所有组件。
- `close()`: 关闭所有组件。
- `print_task_save_items(item: TaskSaveItem)`: 打印任务保存项的信息。
- `print_assistant_thoughts(assistant_reply_json_valid: object, speak_mode: bool = False)`: 打印助手的思考信息。

**注意**: 
- 该类的所有组件在组件集中是全局唯一的。
- 注册方法用于将各个组件注册到核心组件中，构建方法用于初始化所有组件，启动方法用于启动所有组件，关闭方法用于关闭所有组件。
- `print_task_save_items`方法用于打印任务保存项的详细信息，包括任务名称、目标、前期批评、后期批评、里程碑等。
- `print_assistant_thoughts`方法用于打印助手的思考信息，包括思考、推理、计划、批评等。

**输出示例**:
```
XAgentCoreComponents函数: 这个类的功能是XAgent核心组件集，它包含了XAgent的核心组件，用于处理交互、记录运行记录、与工具服务接口通信、处理功能、管理工作记忆、调度代理、与向量数据库接口通信等。

该类的构造函数初始化了所有的组件，并提供了注册和启动这些组件的方法。以下是该类的主要方法和功能：

- register_interaction(interaction: XAgentInteraction): 注册一个交互对象到核心组件中。
- register_logger(): 注册一个日志记录器到核心组件中。
- resister_recorder(param: XAgentParam): 注册一个运行记录器到核心组件中。
- register_toolserver_interface(param: XAgentParam): 注册一个工具服务接口到核心组件中。
- register_function_handler(config): 注册一个功能处理器到核心组件中。
- register_working_memory_function(): 注册一个工作记忆代理到核心组件中。
- register_agent_dispatcher(param: XAgentParam): 注册一个代理调度器到核心组件中。
- register_vector_db_interface(): 注册一个向量数据库接口到核心组件中。
- register_all(param: XAgentParam, interaction: XAgentInteraction): 注册所有组件到核心组件中。
- build(param: XAgentParam, interaction: XAgentInteraction): 构建所有组件。
- start(): 启动所有组件。
- close(): 关闭所有组件。
- print_task_save_items(item: TaskSaveItem): 打印任务保存项的信息。
- print_assistant_thoughts(assistant_reply_json_valid: object, speak_mode: bool = False): 打印助手的思考信息。

注意: 
- 该类的所有组件在组件集中是全局唯一的。
- 注册方法用于将各个组件注册到核心组件中，构建方法用于初始化所有组件，启动方法用于启动所有组件，关闭方法用于关闭所有组件。
- print_task_save_items方法用于打印任务保存项的详细信息，包括任务名称、目标、前期批评、后期批评、里程碑等。
- print_assistant_thoughts方法用于打印助手的思考信息，包括思考、推理、计划、批评等。
```
## FunctionDef __init__
**__init__函数**：这个函数的作用是初始化一个对象。

在这个函数中，有以下几个属性被初始化：
- interaction：用于与用户进行交互的对象。
- logger：用于记录日志的对象。
- recorder：用于记录用户操作的对象。
- toolserver_interface：与工具服务器进行通信的接口对象。
- function_handler：用于处理函数的对象。
- tool_functions_description_list：工具函数的描述列表。
- function_list：函数列表。
- working_memory_function：工作内存函数。
- agent_dispatcher：用于分发代理的对象。
- vector_db_interface：与向量数据库进行通信的接口对象。
- base_dir：基础目录。
- extract_dir：提取目录。
- available_agents：可用的代理列表，包括PlanGenerateAgent、PlanRefineAgent、ToolAgent和ReflectAgent。

**注意**：在使用这段代码时需要注意以下几点：
- 在使用这个对象之前，需要先对其进行初始化，即调用`__init__`函数。
- 在初始化对象时，可以根据需要设置各个属性的值。
- 可以根据需要对属性进行修改或访问。

以上是对该对象的详细解释和说明。
## FunctionDef register_interaction
**register_interaction函数**：此函数的功能是将一个interaction对象注册到核心组件中。

该函数接受一个interaction参数，该参数是一个XAgentInteraction对象，用于表示一个交互。

在XAgent/core.py文件中的register_all函数中，调用了register_interaction函数。register_all函数用于将所有组件注册到核心组件中。在register_all函数中，首先调用了register_interaction函数，将interaction对象注册到核心组件中。

**注意**：使用此代码时需要注意以下几点：
- 确保传入的interaction参数是一个有效的XAgentInteraction对象。
- 注册interaction对象后，可以在核心组件中使用该对象进行后续操作。
## FunctionDef register_logger
**register_logger函数**：该函数的功能是将一个日志记录器注册到核心组件中。

该函数的详细代码分析和描述如下：
- 首先，通过拼接路径的方式创建一个基础目录base_dir，该目录用于存储交互记录。拼接路径的方式是将XAgentServerEnv.base_dir、"localstorage"、"interact_records"、当前日期和交互记录的ID依次拼接而成。其中，XAgentServerEnv.base_dir是一个全局变量，表示XAgentServer的基础目录；"localstorage"和"interact_records"是两个子目录；当前日期通过datetime.now().strftime("%Y-%m-%d")获取；交互记录的ID通过self.interaction.base.interaction_id获取。如果base_dir目录不存在，则会创建该目录。
- 然后，通过拼接路径的方式创建一个提取目录extract_dir，该目录用于存储工作空间。拼接路径的方式是将base_dir和"workspace"依次拼接而成。如果extract_dir目录不存在，则会创建该目录。
- 最后，将self.interaction.logger赋值给self.logger，将交互记录的日志记录器注册到核心组件中。

**注意**：使用该代码需要注意以下几点：
- 该函数依赖于XAgentServerEnv.base_dir、datetime.now().strftime("%Y-%m-%d")和self.interaction.base.interaction_id等变量的值，需要确保这些变量的值正确且已经初始化。
- 该函数会在指定路径下创建目录，需要确保对应的文件系统权限和目录结构正确。
- 该函数会将交互记录的日志记录器注册到核心组件中，需要确保核心组件已经初始化并正确运行。

以上是对register_logger函数的详细分析和描述，希望能帮助您理解该函数的功能和使用方式。
## FunctionDef resister_recorder
**resister_recorder函数**：该函数的功能是将一个记录器注册到核心组件中。

该函数接受一个参数param，类型为XAgentParam。函数内部首先创建一个RunningRecoder对象，并将其赋值给self.recorder属性。RunningRecoder对象的构造函数接受以下参数：
- record_id：交互的唯一标识符，即interaction_id。
- newly_start：一个布尔值，表示是否是新创建的交互。
- root_dir：记录器的根目录，即base_dir。
- logger：日志记录器。

接下来，根据param.newly_created的值，分别执行不同的逻辑：
- 如果param.newly_created为True，表示是新创建的交互，那么调用self.recorder的regist_query方法，将param.query注册到记录器中；调用self.recorder的regist_config方法，将param.config注册到记录器中。
- 如果param.newly_created为False，表示不是新创建的交互，那么调用self.recorder的load_from_db方法，从数据库中加载记录器；然后调用self.recorder的regist_query方法，将param.query注册到记录器中；调用self.recorder的regist_config方法，将param.config注册到记录器中。

最后，将self.recorder赋值给XAgentCoreComponents类的global_recorder属性。

**注意**：使用该代码时需要注意以下几点：
- 该函数需要一个XAgentParam类型的参数param，确保传入正确的参数类型。
- 在调用该函数之前，需要先调用register_all函数，将param和interaction参数传入。
## FunctionDef register_toolserver_interface
**register_toolserver_interface函数**：该函数的功能是将一个工具服务器接口注册到核心组件中。

该函数的详细代码分析和描述如下：
- 首先，函数使用self.logger.info()方法记录一条日志，表示正在注册工具服务器接口。
- 然后，创建一个ToolServerInterface对象，并将其赋值给self.toolserver_interface属性。在创建对象时，传入self.recorder和self.logger作为参数。
- 接着，使用self.logger.info()方法记录一条日志，表示正在延迟初始化工具服务器接口。
- 调用self.toolserver_interface的lazy_init()方法，传入param.config作为参数，完成工具服务器接口的延迟初始化。
- 最后，调用self.interaction的register_toolserver_interface()方法，将self.toolserver_interface作为参数，注册工具服务器接口。

**注意**：使用该代码时需要注意以下几点：
- 在调用register_toolserver_interface()函数之前，需要先调用register_interaction()、register_logger()、resister_recorder()等函数，确保相关组件已经注册。
- 在调用register_toolserver_interface()函数之前，需要传入一个XAgentParam对象和一个XAgentInteraction对象作为参数。
- 在调用register_toolserver_interface()函数之前，需要确保param对象中的config属性已经设置。

该函数在以下文件中被调用：
- 文件路径：XAgent/core.py
- 调用代码：
  ```
  def register_all(self, param: XAgentParam, interaction: XAgentInteraction):
      """
      register all components to the core components
      """
      self.register_interaction(interaction)
      self.register_logger()
      self.resister_recorder(param)
      self.register_toolserver_interface(param)
      self.register_function_handler(param.config)
      self.register_working_memory_function()
      self.register_agent_dispatcher(param=param)
      self.register_vector_db_interface()
  ```
  在register_all()函数中，先调用了register_interaction()、register_logger()、resister_recorder()等函数，然后调用了register_toolserver_interface()函数。在调用register_toolserver_interface()函数时，传入了param作为参数。
## FunctionDef register_function_handler
**register_function_handler函数**：此函数的功能是将一个函数处理程序注册到核心组件中。

该函数用于将一个函数处理程序注册到核心组件中。函数处理程序负责处理来自工具服务器的请求，并将结果返回给工具服务器。注册函数处理程序需要传入以下参数：
- toolserver_interface：工具服务器接口，用于与工具服务器进行通信。
- config：配置信息，包含函数处理程序的相关配置。
- interaction：交互对象，用于与用户进行交互。
- recorder：记录器，用于记录交互过程和结果。
- logger：日志记录器，用于记录日志信息。

在函数内部，首先使用日志记录器记录一条信息，表示正在注册函数处理程序。然后，创建一个FunctionHandler对象，并将上述参数传递给它进行初始化。

需要注意的是：
- 函数处理程序负责处理来自工具服务器的请求，并将结果返回给工具服务器，因此在注册函数处理程序之前，需要确保已经注册了与工具服务器的接口。
- 注册函数处理程序需要传入合适的配置信息，以确保函数处理程序能够正常运行。
- 函数处理程序需要与交互对象和记录器进行交互，因此在注册函数处理程序之前，需要确保已经注册了交互对象和记录器。
- 注册函数处理程序需要使用日志记录器进行日志记录，因此在注册函数处理程序之前，需要确保已经注册了日志记录器。
## FunctionDef register_working_memory_function
**register_working_memory_function函数**：该函数的功能是注册一个工作内存代理到核心组件中。

该函数用于将一个工作内存代理注册到核心组件中，以便于不同处理不同子任务的代理之间进行通信。

在函数内部，首先通过日志记录器记录一条信息，表示正在注册工作内存函数。然后创建一个工作内存代理对象，并将其赋值给self.working_memory_agent。接着调用WorkingMemoryAgent类的get_working_memory_function方法，将返回的工作内存函数赋值给self.working_memory_function。

需要注意的是，该函数在XAgent/core.py文件中被调用，具体调用位置为register_all函数中的self.register_working_memory_function()。

**注意**：使用该代码时需要注意以下几点：
- 该函数用于注册工作内存代理到核心组件中，确保在需要使用工作内存的场景中调用该函数。
- 在调用该函数之前，需要确保已经注册了其他必要的组件，如交互对象、日志记录器、录制器等。
- 该函数会创建一个工作内存代理对象，并将其赋值给self.working_memory_agent，因此在使用工作内存代理对象时，可以通过self.working_memory_agent进行访问。
## FunctionDef register_agent_dispatcher
**register_agent_dispatcher函数**：这个函数的作用是将一个代理调度器注册到核心组件中。

该函数接受一个参数param，类型为XAgentParam。函数内部首先打印日志信息"register agent dispatcher"，然后创建一个XAgentDispatcher对象，并将其赋值给self.agent_dispatcher。创建XAgentDispatcher对象时，传入了param.config、enable=False和self.logger作为参数。接下来，通过循环遍历self.available_agents列表，将每个代理(agent)注册到agent_dispatcher中。

在项目中，该函数被以下文件调用：
文件路径：XAgent/core.py
调用代码如下：
```python
def register_all(self, param: XAgentParam, interaction: XAgentInteraction):
    """
    register all components to the core components
    """
    self.register_interaction(interaction)
    self.register_logger()
    self.resister_recorder(param)
    self.register_toolserver_interface(param)
    self.register_function_handler(param.config)
    self.register_working_memory_function()
    self.register_agent_dispatcher(param=param)
    self.register_vector_db_interface()
```

**注意**：使用该代码时需要注意以下几点：
- 在调用register_agent_dispatcher函数之前，需要先调用其他相关函数，如register_interaction、register_logger等，以确保所需的组件已经注册到核心组件中。
- 通过传入不同的参数，可以控制代理调度器的配置和启用状态。
## FunctionDef register_vector_db_interface
**register_vector_db_interface函数**：此函数的功能是将一个向量数据库接口注册到核心组件中。

该函数没有具体的实现代码，只有一个占位符的pass语句。这意味着该函数目前没有实际的功能代码，只是一个空函数。

该函数被调用的地方是在XAgent/core.py文件中的register_all函数中。在register_all函数中，register_vector_db_interface函数被调用以注册向量数据库接口到核心组件中。

**注意**：目前register_vector_db_interface函数没有实际的功能代码，需要根据实际需求进行具体的实现。
## FunctionDef register_all
**register_all函数**：该函数的功能是将所有组件注册到核心组件中。

在XAgent/core.py文件中，register_all函数被build函数调用。build函数的作用是启动所有组件。在register_all函数中，首先调用self.register_interaction方法将interaction注册到核心组件中，然后调用self.register_logger方法注册日志记录器，接着调用self.resister_recorder方法注册记录器，再调用self.register_toolserver_interface方法注册ToolServer接口，然后调用self.register_function_handler方法注册函数处理器，接着调用self.register_working_memory_function方法注册工作内存函数，然后调用self.register_agent_dispatcher方法注册代理调度器，最后调用self.register_vector_db_interface方法注册向量数据库接口。

在register_all函数中，通过调用各个注册方法，将不同的组件注册到核心组件中，以便后续使用。这些组件包括interaction、日志记录器、记录器、ToolServer接口、函数处理器、工作内存函数、代理调度器和向量数据库接口。

**注意**：在使用该代码时需要注意以下几点：
- 确保在调用register_all函数之前已经初始化了param和interaction参数。
- 确保在调用register_all函数之前已经初始化了self.register_interaction、self.register_logger、self.resister_recorder、self.register_toolserver_interface、self.register_function_handler、self.register_working_memory_function、self.register_agent_dispatcher和self.register_vector_db_interface等方法。
- 确保在调用register_all函数之前已经初始化了self.function_handler、self.working_memory_function和self.logger等属性。
## FunctionDef build
**build函数**：该函数的功能是启动所有组件。

在该函数中，首先调用了`register_all`函数，该函数用于注册所有组件。然后，通过日志记录了"build all components, done!"的信息。

接下来，通过调用`function_handler`对象的`get_functions`函数，获取了子任务函数列表`subtask_functions`和工作内存函数列表`self.working_memory_function`。同时，将工具函数的描述信息保存在`self.tool_functions_description_list`中。

**注意**：在使用该函数时需要注意以下几点：
- 在调用`build`函数之前，需要先调用`register_all`函数进行组件的注册。
- 在调用`build`函数之后，可以通过`self.tool_functions_description_list`获取工具函数的描述信息。
## FunctionDef start
**start函数**：该函数的功能是启动所有组件。

该函数用于启动所有组件，并在日志中记录“start all components”。

**注意**：无特殊注意事项。
## FunctionDef close
**close函数**：该函数的功能是关闭所有组件。

该函数主要有两个步骤：
1. 调用toolserver_interface的download_all_files方法，下载所有文件。
2. 调用toolserver_interface的close方法，关闭组件。

在项目中，该函数被以下文件调用：
文件路径：XAgentServer/server.py
调用代码如下：
```python
def interact(self, interaction: XAgentInteraction):
    # query = message
    """
    XAgent Server Start Function
    """
    from XAgent.config import CONFIG as config
    xagent_core = None
    try:
        config.reload()
        args = {}
        # args
        args = interaction.parameter.args

        self.logger.info(
            f"server is running, the start query is {args.get('goal', '')}")
        xagent_param = XAgentParam()

        # build query
        xagent_param.build_query({
            "role_name": "Assistant",
            "task": args.get("goal", ""),
            "plan": args.get("plan", ["Pay attention to the language in initial goal, always answer with the same language of the initial goal given."]),
        })
        xagent_param.build_config(config)
        xagent_core = XAgentCoreComponents()
        # build XAgent Core Components
        xagent_core.build(xagent_param, interaction=interaction)
        json_str = json.dumps(
            xagent_param.config.to_dict(), indent=2)
        json_str=re.sub(r'"api_key": "(.+?)"', r'"api_key": "**"', json_str)
        self.logger.info(json_str)
        self.logger.typewriter_log(
            "Human-In-The-Loop",
            Fore.RED,
            str(xagent_param.config.enable_ask_human_for_help),
        )

        file_list = interaction.base.file_list
        for file in file_list:
            file_uuid = file.get("uuid", "")
            file_name = file.get("name", "")
            if file_uuid.startswith("/"):
                file_path = file_uuid
            else:
                file_path = os.path.join(XAgentServerEnv.Upload.upload_dir,
                                         interaction.base.user_id, file_uuid)

            upload_dir = os.path.join(
                xagent_core.base_dir, "upload")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            # 拷贝到workspace
            if interaction.call_method == "web":
                shutil.copy(file_path, os.path.join(upload_dir, file_name))
            else:
                if os.path.exists(file_path):
                    if os.path.samefile(file_path, os.path.join(upload_dir, file_name)):
                        # 文件路径相同,跳过复制
                        pass
                    else:
                        shutil.copy(file_path, os.path.join(upload_dir, file_name))
                    # shutil.copy(file_path, os.path.join(upload_dir, file_name))

            new_file = os.path.join(upload_dir, file_name)
            try:
                xagent_core.toolserver_interface.upload_file(new_file)
            except Exception as e:
                self.logger.typewriter_log(
                    "Error happens when uploading file",
                    Fore.RED,
                    f"{new_file}\n{e}",
                )
                raise XAgentUploadFileError(str(e)) from e

        task_handler = TaskHandler(xagent_core=xagent_core,
                                   xagent_param=xagent_param)
        self.logger.info("Start outer loop async")
        task_handler.outer_loop()
    except Exception as e:
        raise XAgentRunningError(str(e)) from e
    finally:
        if xagent_core is not None:
            xagent_core.close()
```

**注意**：使用该代码时需要注意以下几点：
- 在调用close函数之前，需要先调用download_all_files方法下载所有文件。
- 该函数需要在XAgent Server的交互函数interact中调用，用于启动XAgent Server。
## FunctionDef print_task_save_items
**print_task_save_items函数**: 这个函数的功能是打印任务的保存项。

该函数用于打印任务的保存项，包括任务名称、任务目标、任务前期批评、任务后期批评、任务里程碑、后续工具反思、任务状态和动作摘要。函数接受一个TaskSaveItem对象作为参数，该对象包含了任务的各个属性。

函数首先使用logger.typewriter_log方法打印任务名称和任务目标，并使用不同的颜色进行标记。然后，如果任务的后期批评不为空，函数会遍历后期批评列表，并使用logger.typewriter_log方法打印每一行。类似地，如果任务的里程碑不为空，函数会遍历里程碑列表，并使用logger.typewriter_log方法打印每一行。接下来，函数会判断任务的预期工具列表是否为空，如果不为空，则遍历预期工具列表，并使用logger.typewriter_log方法打印每个工具的名称和原因。最后，如果任务的工具反思列表不为空，函数会遍历工具反思列表，并使用logger.typewriter_log方法打印每个工具的名称和反思。

在打印完任务的保存项后，函数会使用logger.typewriter_log方法打印任务的状态和动作摘要。

**注意**: 在使用该函数时，需要将一个TaskSaveItem对象作为参数传入。该对象应包含任务的各个属性，并且属性的值应符合预期的格式。
## FunctionDef print_assistant_thoughts
**print_assistant_thoughts函数**：该函数的功能是打印助手的思考。

该函数接受三个参数：assistant_reply_json_valid（助手回复的有效JSON对象）、speak_mode（是否为语音模式，默认为False）。该函数没有返回值。

函数内部首先初始化了四个变量：assistant_thoughts_reasoning、assistant_thoughts_plan、assistant_thoughts_speak和assistant_thoughts_criticism，它们的初始值都为None。

接下来，函数从assistant_reply_json_valid中获取助手的思考内容，并将其存储在assistant_thoughts变量中。然后，函数从assistant_thoughts中获取具体的思考属性，并将其存储在assistant_thoughts_reasoning、assistant_thoughts_plan和assistant_thoughts_criticism变量中。

如果assistant_thoughts_text不为None且不为空字符串，则函数使用logger.typewriter_log方法打印出"THOUGHTS"和助手的思考内容。

如果assistant_thoughts_reasoning不为None且不为空字符串，则函数使用logger.typewriter_log方法打印出"REASONING"和助手的推理内容。

如果assistant_thoughts_plan不为None且长度大于0，则函数使用logger.typewriter_log方法打印出"PLAN"和助手的计划内容。如果assistant_thoughts_plan是一个列表，则将其转换为字符串；如果是一个字典，则将其转换为字符串。然后，函数使用换行符将计划内容拆分成多行，并使用logger.typewriter_log方法逐行打印。

如果assistant_thoughts_criticism不为None且不为空字符串，则函数使用logger.typewriter_log方法打印出"CRITICISM"和助手的批评内容。

最后，函数返回一个字典，包含助手的思考内容、推理内容、计划内容、批评内容和一个随机生成的node_id。

**注意**：该函数依赖于logger.typewriter_log方法和assistant_reply_json_valid对象的结构。

**输出示例**：假设助手的思考内容为"这是一个测试"，推理内容为"这是一个推理"，计划内容为["步骤1", "步骤2"]，批评内容为"这是一个批评"，则函数的返回值为：
{
  "thoughts": "这是一个测试",
  "reasoning": "这是一个推理",
  "plan": "步骤1\n步骤2",
  "criticism": "这是一个批评",
  "node_id": "随机生成的node_id"
}
***
