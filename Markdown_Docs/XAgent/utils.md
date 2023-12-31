# FunctionDef get_token_nums
**get_token_nums函数**: 该函数的功能是计算给定文本中的标记数量。

该函数接受一个字符串类型的参数text，表示需要计算标记数量的文本。

函数返回一个整数，表示文本中的标记数量。

该函数的实现逻辑如下：
- 使用encoding.encode函数将文本转换为标记列表。
- 使用len函数计算标记列表的长度，即为标记数量。

注意事项：
- 该函数依赖于encoding模块中的encode函数，请确保该函数已正确导入。
- 参数text应为有效的字符串类型。

输出示例：
假设text为"Hello, world!"，则函数返回的标记数量为3。
***
# FunctionDef clip_text
**clip_text函数**：clip_text函数的功能是截取给定文本的指定数量的标记。如果原始文本和截取后的文本长度不一致，则在截取后的文本的开头或结尾添加"`wrapped`"。

该函数接受以下参数：
- text (str)：需要截取的文本。
- max_tokens (int, 可选)：最大的标记数量。文本将被截取为不超过该数量的标记。
- clip_end (bool, 可选)：如果为True，则从文本的末尾开始截取。如果为False，则从文本的开头开始截取。

该函数返回截取后的文本和原始文本中的标记总数。

该函数在以下文件中被调用：
- XAgent/agent/summarize.py
- XAgent/inner_loop_search_algorithms/ReACT.py
- XAgent/workflow/plan_exec.py

在XAgent/agent/summarize.py文件中，该函数被generate_func_args函数调用，用于生成函数参数的字符串形式。

在XAgent/inner_loop_search_algorithms/ReACT.py文件中，该函数被generate_chain函数调用，用于截取文件系统环境的输出。

在XAgent/workflow/plan_exec.py文件中，该函数被plan_refine_mode函数调用，用于截取工作空间文件系统的输出。

请注意：
- 该函数的返回值示例是根据代码逻辑进行的模拟，实际返回值可能会有所不同。
***
# ClassDef LLMStatusCode
**LLMStatusCode类的功能**：该类是一个枚举类，用于描述LLM的不同状态码。

该类定义了以下状态码：
- SUCCESS：表示成功，对应的值为0。
- ERROR：表示错误，对应的值为1。

该类没有任何方法，只是用于定义状态码。

**注意**：在使用该类时，可以通过LLMStatusCode.SUCCESS和LLMStatusCode.ERROR来获取对应的状态码值。
***
# ClassDef ToolCallStatusCode
**ToolCallStatusCode函数**：这个类的功能是描述工具调用的不同状态码。

枚举类型ToolCallStatusCode描述了工具调用的不同状态码。

状态码包括：
- TOOL_CALL_FAILED：工具调用失败
- TOOL_CALL_SUCCESS：工具调用成功
- FORMAT_ERROR：格式错误
- HALLUCINATE_NAME：幻觉名称
- OTHER_ERROR：其他错误
- TIMEOUT_ERROR：超时错误
- TIME_LIMIT_EXCEEDED：超出时间限制
- SERVER_ERROR：服务器错误
- SUBMIT_AS_SUCCESS：提交成功
- SUBMIT_AS_FAILED：提交失败

这个类还重写了__str__方法，用于返回类名和状态码名称的字符串表示。

**注意**：使用这段代码时需要注意以下几点：
- 可以通过ToolCallStatusCode.TOOL_CALL_FAILED等方式来访问不同的状态码。
- 可以通过str()方法将状态码转换为字符串表示。

**输出示例**：假设代码的返回值如下所示：
ToolCallStatusCode: TOOL_CALL_FAILED
## FunctionDef __str__
**__str__函数**：这个函数的作用是返回一个字符串，该字符串由该对象的类名和名称组成。

该函数是一个特殊方法，用于将对象转换为字符串形式。在Python中，当我们使用print函数或str()函数打印对象时，实际上是调用了该对象的__str__方法来获取对象的字符串表示。

在这个具体的代码中，__str__函数返回了一个由该对象的类名和名称组成的字符串。首先，使用self.__class__.__name__获取该对象的类名，然后使用加号连接字符串，再加上该对象的名称。

**注意**：该函数返回的字符串表示了该对象的类名和名称，可以用于打印对象或将对象转换为字符串。

**输出示例**：ToolServer: toolserver1
***
# ClassDef PlanOperationStatusCode
**PlanOperationStatusCode类的功能**：该类是一个枚举类，用于描述计划操作的不同状态码。

枚举类是一种特殊的数据类型，它定义了一组具名的值，这些值可以作为常量在程序中使用。在这个类中，我们定义了以下几个状态码：

- MODIFY_SUCCESS（修改成功）：表示计划操作修改成功。
- MODIFY_FORMER_PLAN（修改前序计划）：表示修改的计划是前序计划。
- PLAN_OPERATION_NOT_FOUND（找不到计划操作）：表示找不到对应的计划操作。
- TARGET_SUBTASK_NOT_FOUND（找不到目标子任务）：表示找不到目标子任务。
- PLAN_REFINE_EXIT（计划细化退出）：表示计划细化操作退出。
- OTHER_ERROR（其他错误）：表示其他未知错误。

**注意**：在使用该枚举类时，可以根据具体的情况选择合适的状态码进行使用。
***
# ClassDef SearchMethodStatusCode
**SearchMethodStatusCode函数**: 这个类的功能是描述搜索方法的不同状态码。

这个类是一个枚举类，用于描述搜索方法的不同状态码。它定义了以下几个状态码：
- DOING：表示搜索正在进行中。
- SUCCESS：表示搜索成功。
- FAIL：表示搜索失败。
- HAVE_AT_LEAST_ONE_ANSWER：表示搜索至少有一个答案。

这个类没有任何方法，只定义了不同的状态码常量。

这个类在项目中的使用情况如下：
- 在XAgent/inner_loop_search_algorithms/ReACT.py文件中，它被用于表示搜索方法的状态。在run方法中，根据搜索结果将其状态设置为SUCCESS或FAIL。
- 在XAgent/inner_loop_search_algorithms/base_search.py文件中，它被用于初始化搜索方法实例的状态。
- 在XAgent/workflow/task_handler.py文件中，它被用于表示搜索方法的状态。在inner_loop方法中，根据搜索结果将任务的状态设置为SUCCESS或FAIL。

**注意**: 这个类只是用于表示搜索方法的状态码，没有具体的方法可调用。
***
# ClassDef TaskStatusCode
**TaskStatusCode类的功能**: 该类是一个枚举类，用于描述任务的不同状态码。

该类定义了以下状态码：
- TODO：表示任务待办状态，即任务尚未开始。
- DOING：表示任务进行中状态，即任务正在进行中。
- SUCCESS：表示任务成功完成状态，即任务已成功完成。
- FAIL：表示任务失败状态，即任务未能成功完成。
- SPLIT：表示任务拆分状态，即任务被拆分为多个子任务。

该类的状态码用于表示任务的不同状态，开发人员可以根据任务的状态来进行相应的处理和判断。例如，在任务执行过程中，可以根据任务的状态来确定下一个要处理的子任务。

**注意**: 
- 该类是一个枚举类，用于表示任务的不同状态码。
- 开发人员可以根据任务的状态码来进行相应的处理和判断。
***
# ClassDef RequiredAbilities
**RequiredAbilities类的功能**：该类是一个枚举类，用于描述所需的不同能力。

该类定义了以下几个枚举值：
- tool_tree_search（工具树搜索）：值为0，表示需要进行工具树搜索的能力。
- plan_generation（计划生成）：值为1，表示需要进行计划生成的能力。
- plan_refinement（计划细化）：值为2，表示需要进行计划细化的能力。
- task_evaluator（任务评估）：值为3，表示需要进行任务评估的能力。
- summarization（总结）：值为4，表示需要进行总结的能力。
- reflection（反思）：值为5，表示需要进行反思的能力。

**注意**：在使用该类时需要注意以下几点：
- 该类是一个枚举类，用于描述所需的不同能力。
- 每个枚举值都有一个对应的整数值，可以通过枚举值的名称或整数值来访问。
- 可以根据具体需求选择所需的能力。
***
# ClassDef AgentRole
**AgentRole函数**: 这个类表示对话中ChatGPT代理的角色。

**属性**:
- name (str): 代理的名称。
- prefix (str): 代理角色的描述。

**AgentRole函数**: 这个类的功能是创建一个ChatGPT代理的角色。

**代码分析和描述**:
AgentRole类是一个简单的类，用于表示ChatGPT代理在对话中的角色。它具有两个属性，name和prefix，分别表示代理的名称和角色的描述。

- name属性是一个字符串类型，表示代理的名称。默认值为"Auto-GPT"。
- prefix属性是一个字符串类型，表示代理角色的描述。默认值为"You are an expert of using multiple tools to handle diverse real-world user queries."。

这个类没有任何方法或功能，只是用于表示代理的角色。

**注意**: 在使用AgentRole类时，可以根据需要修改name和prefix属性的值来适应具体的应用场景。
***
# ClassDef TaskSaveItem
**TaskSaveItem函数**：这个类表示保存任务的结构。

**属性**：
- name (str): 任务的名称。
- goal (str): 任务的目标。
- milestones (List[str]): 完成任务所需的步骤。
- prior_plan_criticism (str): 对任务初始计划的任何批评。
- status (TaskStatusCode): 任务的当前状态。
- action_list_summary (str): 对完成任务的所有操作的摘要。
- posterior_plan_reflection (List[str]): 包含最终决定计划的反思的列表。
- tool_reflection (List[Dict[str,str]]): 包含每个工具反思的字典列表。

**load_from_json方法**：从json表示中加载数据。
- 参数：
  - function_output_item: json表示的数据。
- 返回值：无
- 注意：该方法根据json数据的键来加载数据，并将其赋值给相应的属性。

**to_json方法**：将对象转换为json表示。
- 参数：
  - posterior (bool): 是否包含后续计划的信息，默认为False。
- 返回值：json表示的数据。
- 注意：该方法将对象的属性转换为json数据，并返回该数据。

**raw属性**：将对象转换为原始的json字符串。
- 返回值：原始的json字符串。

**print_task_save_items函数**：打印任务保存项的详细信息。
- 参数：
  - item: TaskSaveItem对象。
- 返回值：无
- 注意：该函数将任务保存项的各个属性打印出来，包括任务名称、目标、批评、里程碑、状态等。

**plan_function_output_parser函数**：将函数输出项解析为Plan对象。
- 参数：
  - function_output_item: 表示函数输出项的字典。
- 返回值：解析后的Plan对象。
- 注意：该函数根据函数输出项创建一个Plan对象，并返回该对象。

**PlanAgent类**：计划代理类，用于生成计划。
- 参数：
  - config: 计划代理的配置。
  - query (BaseQuery): 用于生成计划的基本查询。
  - avaliable_tools_description_list (List[dict]): 可用工具的描述列表。
- 注意：该类用于生成计划，包括任务名称、目标、里程碑等，并提供了一些方法用于操作计划。
## FunctionDef load_from_json
**load_from_json函数**: 该函数的功能是从json表示中加载数据。

该函数接受一个名为function_output_item的参数，该参数是一个字典，表示函数的输出项。函数首先检查function_output_item中是否存在"subtask name"字段，如果存在，则将其赋值给self.name属性；否则，打印"field subtask name not exist"。接下来，函数检查function_output_item中是否存在"goal"字段以及"goal"字段中是否存在"goal"字段，如果存在，则将其赋值给self.goal属性；否则，打印"field goal.goal not exist"。然后，函数检查function_output_item中是否存在"goal"字段以及"goal"字段中是否存在"criticism"字段，如果存在，则将其赋值给self.prior_plan_criticism属性；否则，打印"field goal.criticism not exist"。最后，函数检查function_output_item中是否存在"milestones"字段，如果存在，则将其赋值给self.milestones属性。

**注意**: 使用该代码时需要注意以下几点：
- 确保function_output_item参数是一个字典类型。
- 确保function_output_item字典中的字段名和属性名一致，否则无法正确加载数据。
- 如果function_output_item中的某些字段缺失，会打印相应的错误信息。

该函数在以下文件中被调用：
文件路径：XAgent/workflow/plan_exec.py
调用代码如下：
```python
def plan_function_output_parser(function_output_item: dict) -> Plan:
    """将函数输出项解析为Plan对象。

    Args:
        function_output_item (dict): 表示函数输出项的字典。

    Returns:
        Plan: 解析后的Plan对象。
    """
    subtask_node = TaskSaveItem()
    subtask_node.load_from_json(function_output_item=function_output_item)
    subplan = Plan(subtask_node)
    return subplan
```
在该文件中，load_from_json函数被调用来加载function_output_item的数据，并将其作为参数传递给TaskSaveItem对象的load_from_json方法。然后，使用加载后的数据创建一个Plan对象并返回。

另外，在该文件中还有一个deal_subtask_modify方法，该方法也调用了load_from_json函数。在deal_subtask_modify方法中，load_from_json函数被用来加载function_input中的new_data字段的数据。

**注意**: 在调用load_from_json函数之前，需要确保function_output_item参数是一个合法的字典对象。
## FunctionDef to_json
**to_json函数**：该函数的功能是将对象转换为json表示形式。

该函数接受一个参数posterior，用于确定是否返回任务的后续数据。函数首先创建一个名为json_data的字典对象，将对象的属性以键值对的形式存储在其中。其中包括"name"、"goal"、"prior_plan_criticsim"、"milestones"和"exceute_status"等属性。如果posterior为True，则进一步判断是否存在action_list_summary属性，如果存在则将其添加到json_data中。

最后，函数返回json_data作为结果。

**注意**：该函数的参数posterior默认为False，如果需要返回后续数据，则需要将posterior设置为True。

**输出示例**：假设对象的属性值如下所示：
```
name = "XAgent"
goal = "Perform various tasks"
prior_plan_criticsim = True
milestones = ["Task1", "Task2", "Task3"]
status = "DOING"
action_list_summary = "Summary of action list"

则函数的返回值为：
{
    "name": "XAgent",
    "goal": "Perform various tasks",
    "prior_plan_criticsim": True,
    "milestones": ["Task1", "Task2", "Task3"],
    "exceute_status": "DOING",
    "action_list_summary": "Summary of action list"
}
```
## FunctionDef raw
**raw函数**：该函数的功能是将对象转换为原始的JSON字符串。

该函数使用`json.dumps()`方法将对象转换为原始的JSON字符串，并返回该字符串。

**注意**：使用该代码时需要注意以下几点：
- 该函数需要对象具有`to_json()`方法，以将对象转换为JSON格式。
- 该函数返回的是一个字符串，表示对象的原始JSON字符串。

**输出示例**：假设对象的`to_json()`方法返回的JSON格式如下所示：
```json
{
  "name": "John",
  "age": 30,
  "city": "New York"
}
```
那么调用`raw()`函数后的返回值为：
```json
{
  "name": "John",
  "age": 30,
  "city": "New York"
}
```
***
# ClassDef Singleton
**Singleton函数**: 这个类的功能是确保一个类只有一个实例。

这个Singleton类是一个元类，它继承了`abc.ABCMeta`和`type`，用于确保一个类只有一个实例。它通过维护一个字典`_instances`来保存每个类的实例。当调用一个类时，会首先检查该类是否已经存在实例，如果不存在则创建一个新的实例并保存在`_instances`字典中，然后返回该实例。如果已经存在实例，则直接返回该实例。

这个Singleton类的作用是为了确保一个类只有一个实例，这在某些情况下非常有用。例如，在日志记录器中，我们希望只有一个实例来处理日志记录，这样可以确保日志记录的一致性和避免冲突。

**注意**: 在使用这个Singleton类时，需要注意以下几点:
- Singleton类是一个元类，它需要作为其他类的元类来使用。
- 使用Singleton类时，需要将它作为元类传递给其他类的`metaclass`参数。

**输出示例**:
```
class Logger(metaclass=Singleton):
    # Logger类的定义
    ...
```

```
class AbstractSingleton(abc.ABC, metaclass=Singleton):
    # AbstractSingleton类的定义
    ...
```
## FunctionDef __call__
**__call__函数**：这个函数的作用是创建一个单例类的实例。

在这段代码中，__call__函数是一个特殊的方法，它定义了当一个对象被调用时应该执行的操作。在这个函数中，它首先检查类是否已经存在实例，如果不存在，则通过调用父类的__call__方法创建一个新的实例，并将其存储在类的_instances属性中。最后，它返回类的实例。

**注意**：使用这个函数时需要注意以下几点：
- 这个函数应该在一个单例类的元类中定义。
- 这个函数确保一个类只有一个实例，并提供了一个全局访问点来获取该实例。

**输出示例**：假设代码的返回值可能如下所示：
```
<__main__.Singleton object at 0x7f9b8c6a2a90>
```
***
# ClassDef AbstractSingleton
**AbstractSingleton函数**: 这个类的功能是实现一个抽象的单例基类。继承自这个类的类只能有一个实例。

这个类使用了一个元类来实现确保类只有一个实例的机制。

**详细分析和描述**:
抽象单例（AbstractSingleton）是一个抽象基类（ABC），它使用了一个元类（metaclass）Singleton来确保继承自该类的类只有一个实例。元类是用来创建类的类，它可以控制类的创建过程。通过将Singleton设置为元类，我们可以在创建继承自AbstractSingleton的类时，确保只有一个实例存在。

AbstractSingleton继承自abc.ABC，这意味着它是一个抽象基类。抽象基类是一种特殊的类，它不能被实例化，只能被继承。它的主要作用是定义一组接口或规范，供子类实现。

AbstractSingleton还使用了metaclass=Singleton来指定元类为Singleton。Singleton是一个自定义的元类，它控制了继承自AbstractSingleton的类的创建过程。在创建继承自AbstractSingleton的类时，Singleton会检查是否已经存在一个实例，如果存在则返回该实例，如果不存在则创建一个新的实例。这样就确保了继承自AbstractSingleton的类只有一个实例。

**注意**: 使用AbstractSingleton作为基类时，继承的类只能有一个实例。这可以确保在整个程序中只有一个特定的对象存在，避免了重复创建对象的开销和可能引发的问题。
***
