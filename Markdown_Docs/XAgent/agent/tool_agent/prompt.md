# FunctionDef get_examples_for_dispatcher
**get_examples_for_dispatcher函数**：该函数用于为调度器生成提示的示例。

该函数的作用是为调度器生成提示的示例，包括用户查询或任务的输入、系统提示和用户提示。

代码分析和描述：
该函数定义了三个变量，分别是example_input、example_system_prompt和example_user_prompt，它们分别表示用户查询或任务的输入、系统提示和用户提示。这些变量的值是预先定义好的字符串。

注意事项：
无

输出示例：
example_input = """{\n  "name": "Finding Feasible Examples",\n  "goal": "Find 10 examples that can reach the target number 24 in the 24-points game.",\n  "handler": "subtask 1",\n  "tool_budget": 50,\n  "prior_plan_criticsim": "It may be difficult to come up with examples that are all feasible.",\n  "milestones": [\n    "Identifying appropriate combination of numbers",\n    "Applying mathematical operations",\n    "Verifying the result equals to target number",\n    "Recording feasible examples"\n  ],\n  "expected_tools": [\n    {\n      "tool_name": "analyze_code",\n      "reason": "To ensure all feasible examples meet the rules of the 24-points game"\n    }\n  ],\n  "exceute_status": "TODO"\n}"""
example_system_prompt = SYSTEM_PROMPT
example_user_prompt = USER_PROMPT

该函数返回了三个变量的值，分别是example_input、example_system_prompt和example_user_prompt。这些值可以作为调度器生成提示的示例使用。
***
