# FunctionDef get_examples_for_dispatcher
**get_examples_for_dispatcher函数**：该函数的功能是为调度器生成提示提供示例。

该函数返回三个值，分别是example_input、example_system_prompt和example_user_prompt。其中，example_input是用户查询或任务的示例输入，example_system_prompt是系统提示的示例，example_user_prompt是用户提示的示例。

该函数在以下文件中被调用：
- XAgent/agent/dispatcher.py
- XAgent/agent/plan_refine_agent/prompt.py
- XAgent/agent/reflect_agent/prompt.py
- XAgent/agent/tool_agent/prompt.py

在XAgent/agent/dispatcher.py文件中，get_examples_for_dispatcher函数根据传入的ability_type参数选择不同的模块，并调用相应模块中的get_examples_for_dispatcher函数。

在XAgent/agent/plan_refine_agent/prompt.py文件中，get_examples_for_dispatcher函数返回了一个用于计划细化的示例。

在XAgent/agent/reflect_agent/prompt.py文件中，get_examples_for_dispatcher函数返回了一个用于反思的示例。

在XAgent/agent/tool_agent/prompt.py文件中，get_examples_for_dispatcher函数返回了一个用于工具树搜索的示例。

**注意**：使用该代码时需要注意以下几点：
- 该函数需要在调用之前导入相应的模块。
- 该函数返回的示例可以作为调度器生成提示的输入。

**输出示例**：
```
example_input = "Generate a plan for writing a Python-based calculator."
example_system_prompt = SYSTEM_PROMPT
example_user_prompt = USER_PROMPT
```
***
