# ClassDef Plan
**Plan类**

Plan类表示一个任务计划。

属性:
- father (Optional[Plan]): 父任务计划。
- children (List[Plan]): 子任务计划列表。
- data (TaskSaveItem): 与任务计划相关的数据项。
- process_node (ToolNode): 负责任务计划处理的节点。

方法:
- `__init__(self, data: TaskSaveItem)`: 初始化一个Plan对象。
- `to_json(self, posterior=True) -> dict`: 将Plan对象转换为JSON格式。
- `get_subtask_id(self, to_str=False) -> Union[list, str]`: 获取子任务ID。
- `get_subtask_id_list(self) -> List[int]`: 获取子任务ID列表。
- `get_root(self) -> Plan`: 获取Plan树的根节点。
- `get_depth(self) -> int`: 获取Plan树的深度。
- `get_inorder_travel(cls, now_plan) -> List[Plan]`: 对Plan树进行中序遍历。
- `pop_next_subtask(cls, now_plan) -> Optional[Plan]`: 获取队列中的下一个子任务。
- `get_remaining_subtask(cls, now_plan) -> List[Plan]`: 从给定点获取所有剩余的子任务。
- `make_relation(cls, father, child)`: 在两个计划之间建立父子关系。

**注意**: Plan类用于表示任务计划，包含了任务计划的各种属性和方法。可以通过to_json方法将Plan对象转换为JSON格式，通过get_subtask_id方法获取子任务ID，通过get_root方法获取Plan树的根节点，通过get_depth方法获取Plan树的深度，通过get_inorder_travel方法对Plan树进行中序遍历等。

**输出示例**:
```
{
  "father": null,
  "children": [],
  "data": {
    "name": "task1",
    "goal": "complete task1",
    ...
  },
  "process_node": null
}
```

**注意**: 以上示例为Plan对象的JSON格式表示。
## FunctionDef __init__
**__init__函数**：这个函数的作用是初始化一个Plan对象。

该函数接受一个TaskSaveItem类型的参数data，用于保存与任务计划相关的数据。

在函数体内部，首先初始化了father属性，它是一个可选的Plan对象，用于保存父节点。然后初始化了children属性，它是一个Plan对象的列表，用于保存子节点。接下来初始化了data属性，它保存了TaskSaveItem类型的数据。最后，初始化了process_node属性，它是一个ToolNode对象，用于保存处理节点。

**注意**：使用该代码时需要注意以下几点：
- 参数data必须是TaskSaveItem类型的对象。
- father属性和children属性可以为空，但需要在后续操作中进行正确的赋值。
- process_node属性可以为空，需要根据具体情况进行赋值。
## FunctionDef to_json
**to_json函数**: 这个函数的功能是将Plan对象转换为JSON格式。

该函数接受一个参数posterior，用于确定是否返回任务的后验数据。

返回一个root_json字典，它是Plan对象的JSON格式表示。

该函数首先调用self.data.to_json(posterior=posterior)将Plan对象的data属性转换为JSON格式，并将结果赋值给root_json。

如果self.process_node存在，将self.process_node.data["command"]["properties"]赋值给root_json的"submit_result"键。

然后，将self.get_subtask_id(to_str=True)的返回值赋值给root_json的"task_id"键。

如果self.children的长度大于0，将遍历self.children列表，将每个子任务的to_json()结果添加到root_json的"subtask"键下。

最后，返回root_json。

**注意**: 
- 参数posterior是一个布尔值，用于确定是否返回任务的后验数据。
- 如果self.process_node存在，将self.process_node.data["command"]["properties"]添加到root_json中的"submit_result"键下。
- 如果self.father不为None，将self.get_subtask_id(to_str=True)的返回值添加到root_json中的"task_id"键下。
- 如果self.children的长度大于0，将遍历self.children列表，并将每个子任务的to_json()结果添加到root_json的"subtask"键下。

**输出示例**:
```
{
  "task_id": "123456",
  "subtask": [
    {
      "task_id": "123456-1",
      "name": "子任务1",
      "goal": "完成子任务1",
      "handler": "处理子任务1",
      "tool_budget": 100,
      "subtask": []
    },
    {
      "task_id": "123456-2",
      "name": "子任务2",
      "goal": "完成子任务2",
      "handler": "处理子任务2",
      "tool_budget": 200,
      "subtask": []
    }
  ]
}
```
## FunctionDef get_subtask_id
**get_subtask_id函数**：该函数用于获取子任务的ID。

该函数接受一个布尔值参数`to_str`，用于确定返回的ID是否为字符串类型。

返回值为一个列表，包含子任务的ID。

注意：如果`to_str`为True，则返回的ID为字符串类型；否则返回的ID为整数类型。

**输出示例**：假设`to_str`为False，子任务的ID列表为[1, 2, 3]，则函数的返回值为[1, 2, 3]。

该函数在以下文件中被调用：

文件路径：XAgent/data_structure/plan.py
调用代码如下：
```python
root_json["task_id"] = self.get_subtask_id(to_str=True)
```

文件路径：XAgent/workflow/plan_exec.py
调用代码如下：
```python
subtask_id = now_dealing_task.get_subtask_id(to_str=True)
```

文件路径：XAgent/workflow/task_handler.py
调用代码如下：
```python
task_id = self.now_dealing_task.get_subtask_id(to_str=True)
```

文件路径：XAgent/workflow/working_memory.py
调用代码如下：
```python
subtask_id = terminal_plan.get_subtask_id(to_str=True)
```

请注意：
- 生成的文档内容不应包含Markdown的标题和分隔符语法。
- 文档主要使用中文撰写，如果需要，可以在分析和描述中使用一些英文单词以增强文档的可读性，因为不需要将函数名或变量名翻译为目标语言。
## FunctionDef get_subtask_id_list
**get_subtask_id_list函数**：此函数的功能是获取子任务ID列表。

该函数用于获取当前任务的子任务ID列表。如果当前任务没有父任务，则返回一个包含1的数组；否则，获取父任务的子任务ID列表，并将当前任务的ID添加到列表末尾。

**注意**：在使用此函数时需要注意以下几点：
- 该函数依赖于父任务的存在，如果当前任务没有父任务，则返回默认的子任务ID列表。
- 在调用该函数之前，需要确保当前任务的父任务已经设置。

**输出示例**：假设当前任务的父任务ID为2，当前任务的ID为3，则函数的返回值为[2, 3]。
## FunctionDef make_relation
**make_relation函数**：此函数的功能是在两个计划之间建立父子关系。

此函数接受两个参数：father（父计划）和child（子计划），并将child添加到father的children列表中，并将father设置为child的father。

在项目中，此函数在以下文件中被调用：
文件路径：XAgent/workflow/plan_exec.py
对应代码如下：
```python
def initial_plan_generation(self, agent_dispatcher):
    """生成初始计划。

    通过调用计划生成代理，此方法生成初始计划。
    """
    logger.typewriter_log(
        f"-=-=-=-=-=-=-= 生成初始计划 -=-=-=-=-=-=-=",
        Fore.GREEN,
        "",
    )

    split_functions = deepcopy(function_manager.get_function_schema('subtask_split_operation'))

    agent = agent_dispatcher.dispatch(
        RequiredAbilities.plan_generation,
        target_task=f"生成完成任务的计划：{self.query.task}",
        # avaliable_tools_description_list=self.avaliable_tools_description_list
    )

    # TODO: not robust. dispatcher generated prompt may not contain these specified placeholders?
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
```
对应代码如下：
```python
def deal_subtask_split(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode):
    """处理子任务拆分。

    此方法处理子任务拆分。

    参数：
        function_input (dict)：函数输入。
        now_dealing_task (Plan)：当前正在处理的任务。

    返回：
        str：函数输出。
        PlanOperationStatusCode：状态码。
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
                return json.dumps({"error": f"您只能与当前正在处理的子任务一起拆分TODO子任务计划，例如'>= {now_dealing_task.get_subtask_id(to_str=True)}'。未发生任何操作。"}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
            
            # if not subtask.data.status == TaskStatusCode.FAIL:
            #     return json.dumps({"error": f"You can only split the FAIL subtask plans together. This is a '{subtask.data.status.name}' Task. Nothing happended"}), PlanOperationStatusCode.OTHER_ERROR

            if subtask.get_depth() >= self.config.max_plan_tree_depth:
                return json.dumps({"error": f"计划树的最大深度为{self.config.max_plan_tree_depth}。'{subtask.data.name}'的深度已达到{subtask.get_depth()}。未发生任何操作。"}), PlanOperationStatusCode.OTHER_ERROR

            for new_subtask in function_input["subtasks"]:
                new_subplan = plan_function_output_parser(new_subtask)
                Plan.make_relation(subtask,new_subplan)
            subtask.data.status = TaskStatusCode.SPLIT
            return json.dumps({"success": f"子任务'{target_subtask_id}'已拆分。"}), PlanOperationStatusCode.MODIFY_SUCCESS

    return json.dumps({"error": f"未找到目标子任务ID '{target_subtask_id}'。未发生任何操作。"}), PlanOperationStatusCode.TARGET_SUBTASK_NOT_FOUND
```
【注意】：关于代码使用的注意事项
## FunctionDef get_root
**get_root函数**：此函数的功能是获取计划树的根节点。

该函数用于获取计划树的根节点。计划树是一个层次结构，由多个计划对象组成，每个计划对象都可以有一个父节点和多个子节点。根节点是计划树的最顶层节点，它没有父节点。

该函数首先判断当前计划对象是否有父节点，如果没有父节点，则说明当前计划对象就是根节点，直接返回当前计划对象。如果有父节点，则递归调用父节点的get_root函数，直到找到根节点为止。

**注意**：在使用该函数时需要注意以下几点：
- 该函数只能在计划对象中调用，不能在其他对象中调用。
- 确保计划对象的父子关系正确设置，否则可能导致获取到错误的根节点。

**输出示例**：假设当前计划对象为根节点，则返回当前计划对象本身。
## FunctionDef get_depth
**get_depth函数**：该函数的功能是返回计划树的深度。

该函数通过递归调用父节点的get_depth函数来计算计划树的深度。如果当前节点没有父节点，则返回1，表示当前节点是根节点。否则，返回父节点的深度加1，表示当前节点的深度。

**注意**：该函数依赖于父节点的get_depth函数，因此在调用该函数之前，需要确保父节点已经正确设置。

**输出示例**：假设计划树的深度为3，则函数的返回值为3。
## FunctionDef get_inorder_travel
**get_inorder_travel函数**：此函数的功能是执行计划树的中序遍历。

此函数接受一个参数now_plan，表示当前树中的计划。

函数会返回树中所有计划的中序遍历结果。

函数首先将当前计划now_plan添加到结果列表result_list中。

然后对于当前计划的每个子计划，递归调用get_inorder_travel函数，并将返回的结果列表添加到result_list中。

最后返回result_list作为函数的输出结果。

**注意**：此函数的使用需要注意以下几点：
- 参数now_plan必须是一个有效的计划对象。
- 函数返回的结果是一个包含所有计划的列表。

**输出示例**：假设树中有三个计划A、B、C，其中A是B的父计划，B是C的父计划。调用get_inorder_travel函数时，传入的参数为A，函数的返回结果为[A, B, C]。
## FunctionDef pop_next_subtask
**pop_next_subtask函数**：这个函数的功能是从队列中获取下一个子任务。

该函数接受一个参数now_plan，表示当前的计划。

函数内部首先获取根计划root_plan，然后通过Plan类的get_inorder_travel方法获取所有计划的按顺序遍历列表all_plans。接着，通过index方法找到当前计划在列表中的位置order_id。然后，从order_id+1位置开始遍历all_plans列表，找到第一个状态为TODO的子任务subtask，并返回该子任务。

如果没有找到符合条件的子任务，则返回None。

**注意**：在使用该代码时需要注意以下几点：
- 该函数需要传入一个当前计划对象now_plan。
- 返回值为下一个子任务对象，如果没有符合条件的子任务则返回None。

**输出示例**：假设队列中有多个子任务，返回下一个子任务对象。

```python
subtask = Plan.pop_next_subtask(now_plan)
print(subtask)
```
输出：
```
<Plan object at 0x7f8a7b7e4af0>
```
## FunctionDef get_remaining_subtask
**get_remaining_subtask函数**：此函数的功能是从给定的点获取所有剩余的子任务。

该函数接受一个参数now_plan，表示当前的计划。

函数内部首先获取当前计划的根节点root_plan，然后通过调用Plan类的get_inorder_travel方法获取所有计划的中序遍历结果all_plans。接着，函数通过调用index方法找到当前计划在中序遍历结果中的索引order_id。最后，函数返回从order_id位置开始的所有计划，即剩余的子任务。

**注意**：此函数需要一个Plan对象作为输入参数。

**输出示例**：假设all_plans为[plan1, plan2, plan3, plan4]，order_id为2，则函数返回[plan3, plan4]。
***
