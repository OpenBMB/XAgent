# FunctionDef get_examples_for_dispatcher
**get_examples_for_dispatcher函数**：此函数的功能是为调度器生成提示提供示例。

此函数返回三个变量，分别是example_input、example_system_prompt和example_user_prompt。其中，example_input表示用户查询或任务的示例输入，example_system_prompt表示系统提示的示例，example_user_prompt表示用户提示的示例。

在调用该函数的代码中，根据不同的ability_type参数值，从不同的模块中导入get_examples_for_dispatcher函数，并返回其结果。

在XAgent/agent/dispatcher.py文件中，根据ability_type的不同值，分别从plan_generate_agent、plan_refine_agent、tool_agent和reflect_agent模块中导入get_examples_for_dispatcher函数，并返回其结果。

在XAgent/agent/plan_generate_agent/prompt.py文件中，get_examples_for_dispatcher函数的示例输入是"Generate a plan for writing a Python-based calculator."，示例系统提示和示例用户提示都是SYSTEM_PROMPT和USER_PROMPT。

在XAgent/agent/plan_refine_agent/prompt.py文件中，get_examples_for_dispatcher函数的示例输入是"Refine a plan for writing a Python-based calculator."，示例系统提示和示例用户提示都是SYSTEM_PROMPT和USER_PROMPT。

在XAgent/agent/tool_agent/prompt.py文件中，get_examples_for_dispatcher函数的示例输入是一个JSON格式的字符串，表示一个任务的详细信息，示例系统提示和示例用户提示都是SYSTEM_PROMPT和USER_PROMPT。

**注意**：使用此代码时需要注意的事项。

**输出示例**：
示例输入：Reflect on the previous actions and give the posterior knowledge
示例系统提示：SYSTEM_PROMPT
示例用户提示：USER_PROMPT
***
