# FunctionDef plan_function_output_parser
**plan_function_output_parser函数**：该函数的功能是将函数输出项解析为一个Plan对象。

该函数接受一个表示函数输出项的字典作为参数，并将其解析为一个Plan对象。

参数：
- function_output_item (dict): 表示函数输出项的字典。

返回值：
- Plan: 解析后的Plan对象。

该函数在以下文件中被调用，文件路径和相应的调用代码如下：
文件路径：XAgent/workflow/plan_exec.py
相应代码如下：
    def initial_plan_generation(self, agent_dispatcher):
        """生成初始计划。

        该方法通过调用计划生成代理生成初始计划。
        """
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= 生成初始计划 -=-=-=-=-=-=-=",
            Fore.GREEN,
            "",
        )

        split_functions = deepcopy(function_manager.get_function_schema('subtask_split_operation'))

        agent = agent_dispatcher.dispatch(
            RequiredAbilities.plan_generation,
            target_task=f"生成一个完成任务的计划：{self.query.task}",
            # avaliable_tools_description_list=self.avaliable_tools_description_list
        )

        # TODO: 不够健壮。调度生成的提示信息可能不包含这些指定的占位符？
        new_message , _ = agent.parse(
            placeholders={
                "system": {
                    # "avaliable_tool_descriptions": json.dumps(self.avaliable_tools_description_list, indent=2, ensure_ascii=False),
                    "avaliable_tool_names": str([cont["name"] for cont in self.avaliable_tools_description_list]),
                },
                "user": {
                    "query": self.plan.data.raw
                }
            },
            arguments=deepcopy(function_manager.get_function_schema('simple_thought')['parameters']),
            functions=[split_functions], 
        )
        
        subtasks = json5.loads(new_message["function_call"]["arguments"])

        for subtask_item in subtasks["subtasks"]:
            subplan = plan_function_output_parser(subtask_item)
            Plan.make_relation(self.plan, subplan)

[代码片段结束]
相应代码如下：
    def deal_subtask_split(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode):
        """处理子任务拆分。

        该方法处理子任务拆分。

        参数：
        - function_input (dict): 函数输入。
        - now_dealing_task (Plan): 当前正在处理的任务。

        返回值：
        - str: 函数输出。
        - PlanOperationStatusCode: 状态码。
        """
        print(json.dumps(function_input,indent=2,ensure_ascii=False))

        inorder_subtask_stack = Plan.get_inorder_travel(self.plan)
        target_subtask_id = function_input["target_subtask_id"].strip()
        all_subtask_ids = [cont.get_subtask_id(to_str=True) for cont in inorder_subtask_stack]

        can_edit = False
        for k, subtask in enumerate(inorder_subtask_stack):
            if subtask.get_subtask_id(to_str=True) == now_dealing_task.get_subtask_id(to_str=True):
                
                can_edit = True

            if subtask.get_subtask_id(to_str=True) == target_subtask_id:
                if not can_edit:
                    return json.dumps({"error": f"您只能与当前正在处理的子任务一起拆分待办子任务计划，例如 '>= {now_dealing_task.get_subtask_id(to_str=True)}'。没有发生任何操作。"}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
                
                # if not subtask.data.status == TaskStatusCode.FAIL:
                #     return json.dumps({"error": f"You can only split the FAIL subtask plans together. This is a '{subtask.data.status
***
# ClassDef PlanRefineChain
**PlanRefineChain函数**：这个类的功能是表示一系列计划细化。

这个类用于跟踪细化计划和相关的细化函数。

**属性**：
- plans（List[Plan]）：细化计划的列表。
- functions（List[dict]）：细化函数的列表。

**__init__函数**：
- 初始化一个PlanRefineChain对象。
- 参数：
  - init_plan：初始计划。

**register函数**：
- 注册一个计划细化。
- 参数：
  - function_name（str）：细化函数的名称。
  - function_input（dict）：细化函数的输入。
  - function_output（str）：细化函数的输出。
  - new_plan（Plan）：细化后的新计划。

**parse_to_message_list函数**：
- 将细化链解析为消息列表。
- 参数：
  - flag_changed：一个指示计划是否发生变化的标志。
- 返回值：消息列表。

**注意**：在使用这个类的代码中，需要注意以下几点：
- 在初始化PlanAgent对象时，会创建一个PlanRefineChain对象并将其添加到refine_chains列表中。
- 在plan_refine_mode函数中，会根据用户的建议对计划进行细化，并将细化过程添加到refine_chains列表中。

**输出示例**：
```
PlanRefineChain对象的plans属性：[Plan对象1, Plan对象2, ...]
PlanRefineChain对象的functions属性：[{"name": "函数1", "input": {...}, "output": "输出1"}, {"name": "函数2", "input": {...}, "output": "输出2"}, ...]
```
## FunctionDef register
**register函数**：该函数用于注册计划细化。

该方法将函数名称、输入和输出以及新计划添加到细化链中。

参数：
- function_name (str)：细化函数的名称。
- function_input (dict)：细化函数的输入。
- function_output (str)：细化函数的输出。
- new_plan (Plan)：细化后的新计划。

该函数将函数名称、输入和输出添加到functions列表中，并将新计划添加到plans列表中。

XAgentCoreComponents.global_recorder.regist_plan_modify函数用于注册计划修改，其中包括细化函数的名称、输入、输出以及细化后的计划。

**注意**：使用该代码时需要注意以下几点：
- 需要提供正确的函数名称、输入和输出。
- 需要确保new_plan是Plan类型的对象。
- 需要确保XAgentCoreComponents.global_recorder对象已正确初始化。
## FunctionDef parse_to_message_list
**parse_to_message_list函数**：该函数的功能是将细化链解析为消息列表。

该方法生成一个消息列表，描述细化链中的每个细化步骤。

参数：
- flag_changed：表示计划是否发生了变化的标志。

返回值：
- List[Message]：消息列表。

该函数首先断言self.plans的长度等于self.functions的长度加1。

如果CONFIG.enable_summary为True，则将self.plans[0]转换为JSON格式的字符串，并通过summarize_plan函数生成初始消息init_message。否则，直接将self.plans[0]转换为JSON格式的字符串，并设置缩进和非ASCII字符。

接下来，将init_message封装为Message对象，并添加到output_list中。

然后，通过enumerate函数遍历self.functions和self.plans[1:]，分别获取每个函数和对应的输出计划。根据这些信息生成operation_message，描述用户在第k+1步所做的操作和操作结果，并将其添加到output_list中。

如果self.plans的长度大于1，则根据flag_changed的值判断计划是否发生了变化。如果发生了变化，根据CONFIG.enable_summary的值生成新的消息new_message，并将其添加到output_list中。如果未发生变化，则添加一条消息指示计划未发生变化。

最后，返回output_list作为函数的输出。

**注意**：该函数依赖于其他函数summarize_plan和Message。

**输出示例**：假设函数执行成功，output_list可能如下所示：
```
[
    Message("user", "The initial plan and the execution status is:\n'''\n{init_message}\n'''\n\n"),
    Message("user", "For the 1'th step, You made the following operation:\nfunction_name: {function_name}\n'''\n{function_input}\n'''\nThen get the operation result:\n{function_output}\n"),
    Message("user", "The total plan changed to follows:\n'''\n{new_message}\n'''\n\n")
]
```
***
# ClassDef PlanAgent
**PlanAgent函数**: 这个类的功能是生成和细化计划。

这个类是负责生成和细化计划的，它有以下属性：

- config: 计划代理的配置。
- query (BaseQuery): 用于生成计划的基本查询。
- avaliable_tools_description_list (List[dict]): 可用工具描述的列表。
- plan (Plan): 计划。
- refine_chains (List[PlanRefineChain]): 细化链的列表。

这个类有以下方法：

- `__init__(self, config, query: BaseQuery, avaliable_tools_description_list: List[dict])`: 初始化PlanAgent对象。
- `initial_plan_generation(self, agent_dispatcher)`: 生成初始计划。
- `plan_iterate_based_on_memory_system(self)`: 基于内存系统迭代细化计划。
- `latest_plan(self)`: 获取最新的计划。
- `plan_refine_mode(self, now_dealing_task: Plan, toolserver_interface, agent_dispatcher)`: 进入计划细化模式。
- `deal_subtask_split(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode)`: 处理子任务拆分。
- `deal_subtask_delete(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode)`: 处理子任务删除。
- `deal_subtask_modify(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode)`: 处理子任务修改。
- `deal_subtask_add(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode)`: 处理子任务添加。

**Note**: 
- 这个类代表了一个计划代理，负责生成和细化计划。
- `__init__`方法用于初始化PlanAgent对象，接受配置、查询和可用工具描述列表作为参数。
- `initial_plan_generation`方法用于生成初始计划，通过调用计划生成代理来实现。
- `plan_iterate_based_on_memory_system`方法用于基于内存系统迭代细化计划，目前未实现。
- `latest_plan`方法用于获取最新的计划。
- `plan_refine_mode`方法用于进入计划细化模式，根据用户的建议进行计划细化。
- `deal_subtask_split`方法用于处理子任务拆分，将一个子任务拆分为多个子任务。
- `deal_subtask_delete`方法用于处理子任务删除，删除指定的子任务。
- `deal_subtask_modify`方法用于处理子任务修改，修改指定子任务的数据。
- `deal_subtask_add`方法用于处理子任务添加，在指定子任务后添加新的子任务。

**Output Example**:
```python
plan_agent = PlanAgent(config, query, avaliable_tools_description_list)
plan_agent.initial_plan_generation(agent_dispatcher)
latest_plan = plan_agent.latest_plan()
plan_agent.plan_refine_mode(now_dealing_task, toolserver_interface, agent_dispatcher)
```
## FunctionDef __init__
**__init__函数**：这个函数的作用是初始化一个PlanAgent对象。

详细代码分析和描述：
- 参数config是计划代理的配置。
- 参数query是用于生成计划的基本查询。
- 参数avaliable_tools_description_list是可用工具的描述列表。

这个函数的主要功能是将传入的参数赋值给对象的属性。具体来说：
- 将config赋值给self.config。
- 将query赋值给self.query。
- 将avaliable_tools_description_list赋值给self.avaliable_tools_description_list。

接下来，函数创建了一个Plan对象，并将其赋值给self.plan属性。在创建Plan对象时，传入了一个TaskSaveItem对象作为参数。TaskSaveItem对象包含了一些任务的信息，包括任务的名称、目标、里程碑等。

最后，函数创建了一个空的列表self.refine_chains，用于存储计划的细化链。

**注意**：使用这段代码时需要注意以下几点：
- 需要传入正确的参数，包括config、query和avaliable_tools_description_list。
- 创建Plan对象时，可以根据需要设置TaskSaveItem对象的属性。
## FunctionDef initial_plan_generation
**initial_plan_generation函数**：该函数的功能是生成初始计划。

该函数接受一个名为agent_dispatcher的参数，用于调度代理。

函数内部首先打印一条日志，表示开始生成初始计划。

然后，函数调用function_manager.get_function_schema('subtask_split_operation')函数获取名为'subtask_split_operation'的函数的参数。

接下来，函数调用agent_dispatcher的dispatch方法，传入RequiredAbilities.plan_generation和目标任务的描述作为参数，生成一个代理对象agent。

函数使用agent的parse方法，传入placeholders参数和arguments参数，解析生成新的消息new_message。

函数将new_message中的subtasks解析为字典，并遍历其中的每个子任务。

对于每个子任务，函数调用plan_function_output_parser方法解析子任务的输出，并使用Plan.make_relation方法将子任务与当前计划建立关联。

**注意**：代码中的TODO注释表示该部分代码还不够健壮，因为dispatcher生成的提示可能不包含指定的占位符。

该函数在以下文件中被调用：
文件路径：XAgent/workflow/task_handler.py
代码片段：
```
self.plan_agent.initial_plan_generation(
    agent_dispatcher=self.agent_dispatcher)
```
该函数被调用时，传入了agent_dispatcher作为参数。

函数调用完成后，会打印最新计划的JSON表示，并将计划的相关信息插入到interaction中。

最后，函数调用plan_iterate_based_on_memory_system方法进行计划的迭代。

在函数外部的outer_loop方法中，调用initial_plan_generation函数是解决查询的主要任务之一。

该函数的作用是生成初始计划，通过调用plan generation agent来实现。函数内部通过调用agent_dispatcher的dispatch方法生成一个代理对象agent，并使用agent的parse方法解析生成新的消息new_message。最后，函数将子任务与当前计划建立关联。

**注意**：在使用该函数时，需要注意代码中的TODO注释，以及agent生成的提示信息是否包含指定的占位符。
## FunctionDef plan_iterate_based_on_memory_system
**plan_iterate_based_on_memory_system函数**：该函数的功能是基于内存系统迭代地细化计划。

该函数通过内存系统迭代地细化计划。

代码分析和描述：
- 首先，函数使用logger.typewriter_log方法打印一条带有蓝色前景色的日志信息。
- 然后，函数打印一条"Not Implemented, skip"的信息，表示该函数还未实现。

注意事项：
- 该函数目前还未实现，会直接跳过执行。

该函数在以下文件中被调用：
文件路径：XAgent/workflow/task_handler.py
代码片段：
```
self.plan_agent.plan_iterate_based_on_memory_system()
```
该函数在task_handler.py文件的outer_loop函数中被调用，用于迭代地细化计划。

[代码片段结束]
[XAgent/workflow/task_handler.py文件结束]
## FunctionDef latest_plan
**latest_plan函数**：此函数的功能是获取最新的计划。

该函数返回最新的计划。

该函数被以下文件调用：
文件路径：XAgent/workflow/task_handler.py
代码片段如下：
    def outer_loop(self):
        """
        执行外部循环中的主要任务序列。

        Raises:
            AssertionError: 如果在处理计划时遇到了意外的状态，则引发此异常。

        Returns:
            None
        """
        self.logger.typewriter_log(
            f"-=-=-=-=-=-=-= BEGIN QUERY SOVLING -=-=-=-=-=-=-=",
            Fore.YELLOW,
            "",
        )
        self.query.log_self()

        self.plan_agent.initial_plan_generation(
            agent_dispatcher=self.agent_dispatcher)

        print(summarize_plan(self.plan_agent.latest_plan.to_json()))

        print_data = self.plan_agent.latest_plan.to_json()
        self.interaction.insert_data(data={
            "task_id": print_data.get("task_id", ""),
            "name": print_data.get("name", ""),
            "goal": print_data.get("goal", ""),
            "handler": print_data.get("handler", ""),
            "tool_budget": print_data.get("tool_budget", ""),
            "subtasks": [{**sub, "inner": []} for sub in print_data.get("subtask", [])]
        }, status=StatusEnum.START, current=print_data.get("task_id", ""))

        self.plan_agent.plan_iterate_based_on_memory_system()

        def rewrite_input_func(old, new):
            if new is None or not isinstance(new, dict):
                return old, False
            else:
                goal = new.get("goal", "")
                if goal != "":
                    old = goal
                return old, True

        self.now_dealing_task = self.plan_agent.latest_plan.children[0]
        # workspace_hash_id = ""
        while self.now_dealing_task:
            task_id = self.now_dealing_task.get_subtask_id(to_str=True)
            self.recorder.change_now_task(task_id)
            if self.interaction.interrupt:
                goal = self.now_dealing_task.data.goal
                receive_data = self.interaction.receive(
                    {"args": {"goal": goal}})
                new_intput, flag = rewrite_input_func(
                    self.now_dealing_task, receive_data)

                if flag:
                    self.logger.typewriter_log(
                        "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                        Fore.GREEN,
                        "",
                    )
                    self.logger.typewriter_log(
                        "goal: ",
                        Fore.YELLOW,
                        f"{new_intput}",
                    )
                    self.now_dealing_task.data.goal = new_intput
                    self.logger.typewriter_log(
                        "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                        Fore.GREEN,
                        "",
                    )

            search_method = self.inner_loop(self.now_dealing_task)

            self.now_dealing_task.process_node = search_method.get_finish_node()

            self.posterior_process(self.now_dealing_task)

            self.working_memory_agent.register_task(self.now_dealing_task)

            self.xagent_core.print_task_save_items(self.now_dealing_task.data)

            refinement_result = {
                "name": self.now_dealing_task.data.name,
                "goal": self.now_dealing_task.data.goal,
                "prior_plan_criticism": self.now_dealing_task.data.prior_plan_criticism,
                "posterior_plan_reflection": self.now_dealing_task.data.posterior_plan_reflection,
                "milestones": self.now_dealing_task.data.milestones,
                # "expected_tools": self.now_dealing_task.data.expected_tools,
                "tool_reflection": self.now_dealing_task.data.tool_reflection,
                "action_list_summary": self.now_dealing_task.data.action_list_summary,
                "task_id": task_id,
            }

            self.interaction.insert_data(
                data=refinement_result, status=StatusEnum.REFINEMENT, current=task_id)
            if search_method.need_for_plan_refine:
                self.plan_agent.plan_refine_mode(
                    self.now_dealing_task, self.toolserver_interface, self.agent_dispatcher)
            else:
                self.logger.typewriter_log(
                    "subtask submitted as no need to refine the plan, continue",
                    Fore.BLUE,
                )

            self.now_dealing_task = Plan.pop_next_subtask(
                self.now_dealing_task)

            if self.now_dealing_task is None:
                self.interaction.insert_data(
                    data=[], status=StatusEnum.FINISHED, current="")
            else:
                current_task_id = self.now_dealing_task.get_subtask_id(
                    to_str=True)
                remaining_subtask = Plan.get_remaining_subtask(
                    self.now_dealing_task)
                subtask_list = []
                for todo_plan in remaining_subtask:
                    raw_data = json.loads(todo_plan.data.raw)
                    raw_data["task_id"] = todo_plan.get_subtask_id(to_str=True)
                    raw_data["inner"] = []
                    raw_data["node_id"] = uuid.uuid4().hex
                    subtask_list.append(raw_data)

                self.interaction.insert_data(
                    data=subtask_list, status=StatusEnum.SUBTASK, current=current_task_id)

        self.logger.typewriter_log("ALL Tasks Done", Fore.GREEN)
        return

[代码片段结束]
[End of XAgent/workflow/task_handler.py]

请注意：
- 生成的内容中不应包含Markdown标题和分割线语法。
- 主要使用中文编写。如果需要，可以在分析和描述中使用一些英文单词，以增强文档的可读性，因为您不需要将函数名或变量名翻译为目标语言。

**latest_plan函数**：此函数的功能是获取最新的计划。

该函数返回最新的计划。

该函数被XAgent/workflow/task_handler.py文件中的outer_loop函数调用。outer_loop函数是执行外部循环中的主要任务序列的函数。在outer_loop函数中，首先进行了初始计划生成的操作，然后打印了最新计划的摘要信息，并将该计划的相关信息插入到交互系统中。接下来，根据内存系统的迭代计划进行迭代，然后进入一个循环，处理当前正在处理的任务。在处理任务的过程中，根据用户的输入进行相应的处理，然后执行内部循环任务，并进行后续处理。最后，根据需要进行计划的细化或提交子任务，直到所有任务完成。函数执行完毕后，打印所有任务完成的信息。

**注意**：使用该函数时需要注意以下几点：
- 该函数依赖于其他函数和类的支持，确保这些依赖项已正确导入。
- 函数返回的最新计划可能是一个复杂的数据结构，需要根据具体情况进行处理。

**输出示例**：假设最新计划为{"task_id": "123", "name": "任务1", "goal": "完成某项任务"}，则函数返回{"task_id": "123", "name": "任务1", "goal": "完成某项任务"}。
## FunctionDef plan_refine_mode
**plan_refine_mode函数**：该函数的功能是进入计划细化模式，并根据用户的建议对计划进行细化。

该函数接受以下参数：
- now_dealing_task (Plan): 当前正在处理的任务。

函数内部逻辑如下：
1. 将进入计划细化模式的提示信息打印到日志中。
2. 将当前计划添加到计划细化链中。
3. 初始化计划修改步数和最大步数。
4. 根据任务调度器获取计划细化代理。
5. 尝试从当前处理的任务中获取细化节点的信息。
6. 获取工作空间文件的信息。
7. 进入循环，直到达到最大步数或退出计划细化模式。
8. 在每次循环中，获取当前子任务的ID，并设置标志位flag_changed为False。
9. 将当前计划细化链解析为消息列表。
10. 准备函数调用所需的参数。
11. 调用代理的解析方法，获取新的消息和函数调用的输入。
12. 根据函数调用的输入执行相应的操作，并获取输出结果和状态码。
13. 根据输出结果判断是否发生了修改，并将修改信息注册到计划细化链中。
14. 根据状态码判断操作的结果，并打印相应的日志。
15. 如果状态码为PLAN_REFINE_EXIT或MODIFY_SUCCESS，则退出计划细化模式。
16. 增加计划修改步数。
17. 返回函数的执行结果。

**注意**：在使用该函数时需要注意以下几点：
- 函数的参数now_dealing_task必须是Plan类型的对象。
- 函数的执行过程中会根据用户的建议对计划进行细化，需要确保用户的建议是合理有效的。

**输出示例**：模拟函数返回值的可能外观。
```python
{
    "content": "exit PLAN_REFINE_MODE successfully"
}
```
## FunctionDef deal_subtask_split
**deal_subtask_split函数**: 这个函数的功能是处理子任务的拆分。

这个函数用于处理子任务的拆分。

参数:
- function_input (dict): 函数的输入参数。
- now_dealing_task (Plan): 当前正在处理的任务。

返回值:
- str: 函数的输出结果。
- PlanOperationStatusCode: 状态码。

这个函数首先打印出function_input的内容，然后获取当前任务的子任务栈inorder_subtask_stack，并从function_input中获取目标子任务的ID。接下来，遍历子任务栈，判断是否可以编辑当前子任务以及是否找到了目标子任务。如果可以编辑当前子任务并且找到了目标子任务，则进行拆分操作。拆分操作包括创建新的子任务并建立与原子任务的关系。最后，将目标子任务的状态设置为SPLIT，并返回拆分成功的消息。

如果没有找到目标子任务，则返回目标子任务未找到的错误消息。

**注意**: 使用这段代码时需要注意以下几点:
- function_input参数需要包含target_subtask_id和subtasks字段。
- target_subtask_id字段表示目标子任务的ID。
- subtasks字段是一个列表，包含了要拆分出的新子任务的信息。

**输出示例**:
```
{
    "success": "子任务 'target_subtask_id' 已经被拆分"
}
```
## FunctionDef deal_subtask_delete
**deal_subtask_delete函数**：这个函数的功能是处理子任务的删除。

该方法用于处理子任务的删除。

参数：
- function_input（dict）：函数输入。
- now_dealing_task（Plan）：当前正在处理的任务。

返回值：
- str：函数输出。
- PlanOperationStatusCode：状态码。

代码分析和描述：
该函数首先打印出function_input的内容，然后获取目标子任务的ID，并将所有子任务的ID存储在all_subtask_ids列表中。

接下来，函数会遍历inorder_subtask_stack列表，找到与目标子任务ID相匹配的子任务。如果找到了目标子任务，函数会进行以下操作：
- 检查是否可以编辑该子任务，如果不可以编辑，则返回错误信息。
- 检查子任务的状态是否为"TODO"，如果不是，则返回错误信息。
- 尝试删除该子任务，并返回删除成功的信息。

如果遍历完整个inorder_subtask_stack列表后仍未找到目标子任务，则返回目标子任务未找到的错误信息。

注意：使用该代码时需要注意以下几点：
- function_input参数需要包含"target_subtask_id"字段，表示要删除的子任务ID。
- 函数的返回值是一个包含函数输出和状态码的元组。

输出示例：
```
{
  "success": "Subtask 'target_subtask_id' has been deleted"
}
```
## FunctionDef deal_subtask_modify
**deal_subtask_modify函数**：该函数的功能是处理子任务的修改。

该方法用于处理子任务的修改。

参数：
- function_input (dict)：函数输入。
- now_dealing_task (Plan)：当前正在处理的任务。

返回值：
- str：函数输出。
- PlanOperationStatusCode：状态码。

代码分析和描述：
该函数用于处理子任务的修改。首先，将函数输入以json格式打印出来。然后，获取按照顺序遍历的子任务栈。接下来，获取目标子任务的ID，并将所有子任务的ID存储在一个列表中。

然后，设置一个变量can_edit为False。遍历子任务栈，如果当前子任务的ID与目标子任务的ID相同，则进行以下操作：
- 如果can_edit为False，则返回错误信息，说明只能修改TODO状态的子任务计划，例如任务ID为'now_dealing_task.get_subtask_id(to_str=True)'，而你正在修改的是'subtask.get_subtask_id(to_str=True)'。返回的状态码为MODIFY_FORMER_PLAN。
- 否则，断言当前子任务的状态为TODO，并将其数据从函数输入中加载。

最后，返回修改成功的信息和状态码MODIFY_SUCCESS。

如果当前子任务的ID与当前正在处理的任务的ID相同，则将can_edit设置为True。

如果遍历完整个子任务栈后，仍未找到目标子任务的ID，则返回错误信息，说明目标子任务的ID' target_subtask_id '未找到，应该在' all_subtask_ids '中。返回的状态码为TARGET_SUBTASK_NOT_FOUND。

注意：关于代码使用的注意事项
- 函数的输入参数function_input应为一个字典类型。
- 函数的返回值为一个字符串和一个状态码。

输出示例：
```
{
  "success": "Subtask 'target_subtask_id' has been modified"
}
```
## FunctionDef deal_subtask_add
**deal_subtask_add函数**：此函数的功能是处理子任务的添加。

该方法用于处理子任务的添加。

参数：
- function_input（dict）：函数输入。
- now_dealing_task（Plan）：当前正在处理的任务。

返回值：
- str：函数输出。
- PlanOperationStatusCode：状态码。

代码分析和描述：
- 首先，该函数打印出function_input的内容。
- 然后，获取当前任务的中序子任务栈。
- 获取目标子任务的ID，并将其去除首尾的空格。
- 获取所有子任务的ID列表。
- 检查former_subtask_id是否有效。遍历子任务栈，如果找到与former_subtask_id相等的子任务，则将其赋值给former_subtask。如果找不到，则返回错误信息和状态码TARGET_SUBTASK_NOT_FOUND。
- 获取former_subtask和now_dealing_task的ID列表。
- 检查former_subtask的深度是否小于等于1。如果是，则返回错误信息和状态码TARGET_SUBTASK_NOT_FOUND，表示不允许在根级别添加子任务。
- 检查former_subtask的宽度是否超过了最大宽度。如果超过了最大宽度，则返回错误信息和状态码OTHER_ERROR。
- 检查former_subtask_id_list和now_dealing_task_id_list的长度，并逐个比较对应位置的元素。如果former_subtask_id_list中的元素小于now_dealing_task_id_list中的元素，则返回错误信息和状态码MODIFY_FORMER_PLAN。
- 如果通过了上述检查，将function_input中的subtasks转换为Plan对象的列表new_subplans。
- 获取subtask的父节点，如果父节点为空，则返回错误信息和状态码MODIFY_FORMER_PLAN。
- 获取subtask在父节点的children列表中的索引。
- 将new_subplans插入到subtask的父节点的children列表中的index+1的位置。
- 返回成功信息和状态码MODIFY_SUCCESS。

注意：使用代码中的PlanOperationStatusCode枚举类表示状态码。

输出示例：
```
{
  "success": "A new subtask has been added after 'former_subtask_id'"
}
```
***
