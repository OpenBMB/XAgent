# ClassDef TaskHandler
**TaskHandler函数**：TaskHandler类是XAgent系统中处理任务的主要类。

该类具有以下属性：
- config：任务处理器的配置设置。
- function_list：当前任务可用函数的列表。
- tool_functions_description_list：当前任务可用工具函数的描述列表。
- query：当前任务的查询。
- tool_call_count：用于跟踪工具调用次数的变量。
- plan_agent：用于生成和处理当前任务计划的PlanAgent类的实例。
- interaction：与外部世界进行交互的XAgentInteraction类的实例。

该类具有以下方法：
- \_\_init\_\_(self, xagent_core: XAgentCoreComponents, xagent_param: XAgentParam)：使用提供的输入参数初始化TaskHandler对象。
- outer_loop(self)：执行外部循环中的主要任务序列。
- inner_loop(self, plan: Plan)：生成搜索计划并处理当前任务的内部循环。
- posterior_process(self, terminal_plan: Plan)：对终端计划执行后处理步骤，包括提取后知识和更新计划数据。

**注意**：该类用于处理XAgent系统中的任务，包括生成和处理计划、执行搜索计划、后处理等操作。

**输出示例**：
```
# TaskHandler对象示例
task_handler = TaskHandler(xagent_core, xagent_param)

# 执行外部循环
task_handler.outer_loop()

# 执行内部循环
task_handler.inner_loop(plan)

# 执行后处理
task_handler.posterior_process(terminal_plan)
```
## FunctionDef __init__
**__init__函数**：该函数的作用是初始化TaskHandler对象。

该函数接受两个参数：xagent_core和xagent_param。xagent_core是XAgentCoreComponents类的实例，xagent_param是XAgentParam类的实例。

函数内部将传入的参数赋值给TaskHandler对象的属性。具体赋值如下：
- self.xagent_core = xagent_core：将xagent_core赋值给self.xagent_core。
- self.xagent_param = xagent_param：将xagent_param赋值给self.xagent_param。
- self.config = xagent_param.config：将xagent_param的config属性赋值给self.config。
- self.function_list = self.xagent_core.function_list：将xagent_core的function_list属性赋值给self.function_list。
- self.tool_functions_description_list = self.xagent_core.tool_functions_description_list：将xagent_core的tool_functions_description_list属性赋值给self.tool_functions_description_list。
- self.query = self.xagent_param.query：将xagent_param的query属性赋值给self.query。
- self.tool_call_count = 0：将工具调用计数器初始化为0。
- self.plan_agent = PlanAgent(...)：创建PlanAgent对象，并将config、query和tool_functions_description_list作为参数传入。
- self.logger = self.xagent_core.logger：将xagent_core的logger属性赋值给self.logger。
- self.interaction = self.xagent_core.interaction：将xagent_core的interaction属性赋值给self.interaction。
- self.recorder = self.xagent_core.recorder：将xagent_core的recorder属性赋值给self.recorder。
- self.agent_dispatcher = self.xagent_core.agent_dispatcher：将xagent_core的agent_dispatcher属性赋值给self.agent_dispatcher。
- self.function_handler = self.xagent_core.function_handler：将xagent_core的function_handler属性赋值给self.function_handler。
- self.toolserver_interface = self.xagent_core.toolserver_interface：将xagent_core的toolserver_interface属性赋值给self.toolserver_interface。
- self.working_memory_agent = self.xagent_core.working_memory_agent：将xagent_core的working_memory_agent属性赋值给self.working_memory_agent。
- self.now_dealing_task = None：将当前正在处理的任务初始化为None。

**注意**：在使用该代码时需要注意以下几点：
- 该函数需要传入两个参数：xagent_core和xagent_param。
- xagent_core必须是XAgentCoreComponents类的实例。
- xagent_param必须是XAgentParam类的实例。
- 函数内部会根据传入的参数进行属性的赋值操作，确保传入的参数类型正确。
## FunctionDef outer_loop
**outer_loop函数**：该函数的功能是执行外部循环中的主要任务序列。

该函数首先打印日志，然后记录查询的详细信息。接下来，调用plan_agent的initial_plan_generation方法生成初始计划，并将agent_dispatcher作为参数传递给该方法。然后，打印最新计划的摘要信息。

接着，将最新计划的JSON表示打印出来，并将其作为参数传递给interaction的insert_data方法，将计划的详细信息插入到数据库中。

然后，调用plan_agent的plan_iterate_based_on_memory_system方法，根据内存系统迭代计划。

接下来，定义了一个名为rewrite_input_func的内部函数，用于重写输入数据。然后，将当前处理的任务设置为最新计划的第一个子任务。

在while循环中，处理当前任务，如果interaction的interrupt属性为True，则接收用户输入，并根据用户输入重写当前任务的目标。然后，调用inner_loop方法处理当前任务，并获取搜索方法的完成节点。

接下来，调用posterior_process方法处理当前任务，并将当前任务注册到working_memory_agent中。

然后，打印当前任务的保存项。

接着，构建了一个包含当前任务信息的字典，并将其作为参数传递给interaction的insert_data方法，将任务的详细信息插入到数据库中。

如果搜索方法需要进行计划细化，则调用plan_agent的plan_refine_mode方法进行计划细化。否则，打印一条消息表示不需要进行计划细化。

最后，通过调用Plan类的pop_next_subtask方法获取下一个子任务，并将其设置为当前任务。如果当前任务为空，则将一个空列表插入到数据库中，表示任务已完成。否则，获取当前任务的子任务列表，并将其插入到数据库中。

最后，打印一条消息表示所有任务已完成，并返回None。

**注意**：在使用该代码时需要注意以下几点：
- 该函数依赖于其他类和方法，确保在使用之前已经正确初始化和配置了这些依赖项。
- 该函数会修改当前任务的目标和其他属性，确保在使用之前已经正确设置了这些属性。
- 该函数会将任务的详细信息插入到数据库中，确保数据库连接正常并具有正确的权限。

**输出示例**：
```
-=-=-=-=-=-=-= BEGIN QUERY SOVLING -=-=-=-=-=-=-=
查询日志信息
最新计划的摘要信息
任务详细信息已插入到数据库中
当前任务的保存项已打印
任务详细信息已插入到数据库中
计划细化完成，或者不需要细化
当前任务的子任务列表已插入到数据库中
...
ALL Tasks Done
```
### FunctionDef rewrite_input_func
**rewrite_input_func函数**：此函数的功能是根据新的输入重写旧的输入。

该函数接受两个参数，old和new。首先，它会检查new是否为None或者不是字典类型，如果是的话，它会直接返回old和False。否则，它会获取new字典中的"goal"键对应的值，并将其赋给old。最后，函数返回old和True。

该函数主要用于重写旧的输入，以便在用户输入中更新任务的目标。如果用户提供了新的目标，那么将使用新的目标替换旧的目标，否则将保持不变。

**注意**：在使用此函数时需要注意以下几点：
- 函数的参数old和new必须符合函数的要求，old为旧的输入，new为新的输入。
- new必须是一个字典类型，且包含"goal"键。

**输出示例**：
假设旧的输入为"old_input"，新的输入为{"goal": "new_goal"}，则函数的返回值为("new_goal", True)。
## FunctionDef inner_loop
**inner_loop函数**：该函数的功能是生成搜索计划并处理当前任务。

该函数接受一个参数plan，表示要处理的计划。

该函数首先将任务的子任务ID转换为字符串，并打印日志。然后调用xagent_core的print_task_save_items方法打印任务的保存项。

接下来，通过调用agent_dispatcher的dispatch方法，根据plan的JSON表示和所需的能力生成一个代理。

然后将任务的状态设置为DOING。

如果配置中的rapidapi_retrieve_tool_count大于0，则调用toolserver_interface的retrieve_rapidapi_tools方法，根据计划生成一个检索字符串，并获取相应数量的rapidapi工具。如果获取到了工具，则更新function_handler的avaliable_tools_description_list和subtask_handle_function_enum。

接下来，创建一个ReACTChainSearch实例，并调用其run方法，传入配置、代理、参数、函数、任务ID等参数。

根据搜索方法的状态，更新任务的状态，并打印相应的日志。

最后，返回search_method实例。

**注意**：在调用该函数之前，需要确保已经初始化了相关的对象和参数。

**输出示例**：一个可能的返回值的示例。
## FunctionDef posterior_process
**posterior_process函数**：此函数的功能是对终端计划执行后处理步骤，包括提取后验知识和更新计划数据。

该函数接受一个参数terminal_plan，表示完成所有内循环任务后的终端计划。

函数内部首先调用get_posterior_knowledge函数，传入多个参数，包括最新的计划、终端计划、完成节点、工具函数描述列表、配置和代理调度器。该函数用于获取后验知识，并将结果保存在posterior_data变量中。

接下来，将posterior_data中的summary赋值给terminal_plan.data.action_list_summary，用于更新终端计划的动作列表摘要。

然后，检查posterior_data中是否存在reflection_of_plan和reflection_of_tool，如果存在，则将其分别赋值给terminal_plan.data.posterior_plan_reflection和terminal_plan.data.tool_reflection。

最后，函数执行完毕，返回None。

**注意**：使用此代码时需要注意以下几点：
- 函数需要一个Plan类型的参数terminal_plan作为输入。
- 函数内部调用了get_posterior_knowledge函数，需要确保该函数已经定义并可用。
- 函数会更新终端计划的数据，包括动作列表摘要、后验计划反思和工具反思。
***
