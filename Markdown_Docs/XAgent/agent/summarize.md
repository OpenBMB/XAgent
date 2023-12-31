# FunctionDef summarize_action
**summarize_action函数**：此函数的功能是生成一系列动作的摘要。

该函数接受两个参数：action_process（要处理的动作列表）和task（任务名称），并返回一个包含动作摘要的字符串。

函数内部首先检查action_process列表的长度，如果小于1，则返回"未找到步骤"。

接下来，函数定义了一个内部函数generate_func_args，用于生成以字符串形式表示的函数参数。该函数接受两个参数：args（参数字典）和black_list（禁止或限制在args字典中使用的单词或键的列表）。函数通过遍历args字典中的键值对，并根据条件生成相应的字符串，最后返回生成的字符串。

然后，函数对action_process列表进行遍历，根据条件对每个动作进行处理。首先判断动作的状态码，如果状态码为TOOL_CALL_SUCCESS，则将动作的命令和参数生成字符串，并将其存储在raw_action列表中的第一个位置。如果命令的名称为"FileSystem"，并且参数字典中包含"filepath"键，并且动作的状态码为TOOL_CALL_SUCCESS，则将raw_action列表中的第二个位置设置为"`Old Content has been wrapped, check latest filesystem calling`"，否则将其设置为动作的工具输出。最后，将raw_action添加到raw_actions字典中。

接下来，函数对raw_actions字典中的键进行排序，并遍历排序后的键，生成每个动作的摘要。如果动作中不包含"summary"键，则将动作的描述信息和工具调用信息拼接成一个字符串，并使用function_manager函数的返回值作为动作的摘要。最后，将摘要添加到动作字典中。

接下来，函数根据一定的规则对动作字典进行处理，包括添加返回值、添加失败原因等。最后，将处理后的动作字典按照键的顺序拼接成一个字符串，并返回该字符串作为函数的输出。

**注意**：在使用该函数时，需要注意以下几点：
- 函数的第一个参数action_process应为一个包含动作信息的列表。
- 函数的第二个参数task应为一个字符串，表示任务名称。

**输出示例**：假设action_process列表包含两个动作，摘要字符串的输出可能如下所示：
```
[0] command1(args1)
[0][summary] summary1
[0][description] description1
[0][status code] TOOL_CALL_SUCCESS
[0][return] return_value1
[1] command2(args2)
[1][summary] summary2
[1][description] description2
[1][status code] TOOL_CALL_SUCCESS
[1][return] return_value2
[suggestion] suggestion1
[suggestion] suggestion2
```
## FunctionDef generate_func_args
**generate_func_args函数**：该函数的功能是生成以字符串形式表示的函数参数。

该函数接受两个参数：args（字典类型）和black_list（列表类型），并返回一个字符串，该字符串概括了函数的参数。

参数说明：
- args（字典类型）：一个包含参数的字典。
- black_list（列表类型）：一个包含禁止或限制在args字典中使用的关键词或键的列表。

返回值：
- str：一个字符串，概括了函数的参数。

函数内部实现逻辑如下：
1. 初始化一个空字符串ret和一个变量args_len，用于记录已处理的参数长度。
2. 遍历args字典中的每个键值对，其中k为键，v为值。
3. 如果k在black_list列表中，则将v替换为"`wrapped`"。
4. 使用clip_text函数将v转换为字符串，并限制其长度不超过SINGLE_ACTION_MAX_LENGTH-args_len，clip_end参数表示是否截断字符串末尾。
5. 如果v的长度小于SINGLE_ACTION_MAX_LENGTH-args_len，则将k和v添加到ret字符串中，如果v是字符串类型，则使用双引号括起来；如果v不是字符串类型，则直接添加。
6. 更新args_len的值。
7. 如果v的长度超过SINGLE_ACTION_MAX_LENGTH-args_len，则将k和截断后的v添加到ret字符串中，如果v是字符串类型，则使用双引号括起来，并在末尾添加省略号；如果v不是字符串类型，则直接添加，并在末尾添加省略号。
8. 更新args_len的值。
9. 返回ret字符串，去除最后一个逗号。

**注意**：在使用该函数时，需要注意以下几点：
- args参数必须是一个字典类型。
- black_list参数可以为空列表，也可以包含禁止或限制使用的关键词或键。
- 函数返回的字符串概括了函数的参数，可以根据需要进行进一步处理或展示。

**输出示例**：以下是该函数的一个可能的返回值的示例：
```
arg1="value1", arg2="value2", arg3="value3"...
```
***
# FunctionDef summarize_plan
**summarize_plan函数**：这个函数的功能是根据提供的计划生成一个总结的计划。

该函数接受一个字典类型的参数plans，其中包含了要提供的计划信息。函数返回一个字符串，其中包含了计划的摘要信息。

函数内部定义了一个嵌套函数recursive_summary，用于递归生成摘要计划。在递归过程中，函数会根据计划的不同字段生成相应的描述信息，并将其添加到summary列表中。

函数还定义了一些局部变量，如summary用于存储计划的摘要信息列表，task_ids用于存储计划的任务ID列表，detailed_info用于存储详细的计划信息，current_task_id用于记录当前任务ID。

在函数的最后，根据计划的长度和摘要信息的长度，生成最终的摘要计划。最后将摘要计划转换为字符串形式并返回。

**注意**：该函数依赖于get_token_nums函数和MAX_PLAN_LENGTH常量。

**输出示例**：
```
[Task ID] 1
[Name] Task 1
[Goal] Complete task 1
[Status] DOING
[Milestones]
- Milestone 1
- Milestone 2
[Prior Plan Criticism] Plan criticism for task 1
[Action Status] Success
[Action Info]
- [Conclusion] Action conclusion for task 1
- [Summary] Action summary for task 1
```
这是一个计划的摘要信息示例，包含了任务ID、名称、目标、状态、里程碑、先前计划批评、动作状态和动作信息等信息。
## FunctionDef recursive_summary
**recursive_summary函数**: 这个函数的功能是生成一个递归过程中的总结计划。

该函数接受一个字典类型的计划作为参数。

函数内部首先定义了一些局部变量，包括summary、task_ids和detailed_info。然后通过递归的方式遍历计划的子任务，生成计划的总结描述。在生成总结描述的过程中，会根据计划的不同属性添加相应的描述信息，如任务ID、名称、目标和执行状态等。如果计划中包含里程碑，会将里程碑信息添加到总结描述中。如果计划中没有动作列表的总结描述，但存在之前计划的批评信息，会将批评信息添加到总结描述中。如果计划中存在提交结果，并且结果中包含参数信息，会将动作状态和结论信息添加到总结描述中。如果提交结果中的建议需要对后续子任务的计划进行改进，并且存在改进原因，会将改进原因添加到总结描述中。最后，将任务ID和总结描述添加到task_ids和summary列表中。

在函数的最后，根据当前任务ID和总结描述的长度，对总结描述进行筛选和补充。如果总结描述的长度超过了最大计划长度限制，会跳过该计划。否则，将该计划的详细信息添加到总结描述中。最终，将所有计划的总结描述拼接成一个字符串，并返回。

**注意**: 使用该函数时需要注意以下几点：
- 该函数需要传入一个字典类型的计划作为参数。
- 计划中的属性需要符合特定的命名规范，如task_id、name、goal、exceute_status等。
- 计划中的子任务需要以"subtask"属性的形式存在，并且是一个列表类型。
- 计划中的提交结果需要符合特定的结构，包含args属性，并且args属性中包含result和suggestions_for_latter_subtasks_plan等属性。
- 计划的总结描述长度不能超过最大计划长度限制。
***
