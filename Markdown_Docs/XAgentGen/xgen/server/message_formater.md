# FunctionDef custom_yaml_dump
**custom_yaml_dump函数**：该函数的功能是将输入的item对象转换为自定义的YAML格式。

该函数的代码逻辑如下：
- 如果item为None，则直接返回item。
- 如果item是字典类型，则遍历字典中的每个键值对，对值进行递归调用custom_yaml_dump函数，并将结果存入新的字典中。
- 如果item是字符串类型且包含换行符，则调用literal函数将字符串转换为YAML格式。
- 其他情况下，直接返回item。

该函数在以下文件中被调用：
文件路径：XAgentGen/xgen/server/message_formater.py
调用代码如下：
def custom_yaml_dump(item):
    if item is None:
        return item
    elif isinstance(item, dict):
        data = {}
        for key, value in item.items():
            data[key] = custom_yaml_dump(value)
        return data
    elif isinstance(item, str) and '\n' in item:
        return literal(item)
    else:
        return item

【代码片段结束】
调用代码如下：
def yaml_dump(item):
    f = StringIO()
    item = custom_yaml_dump(item)
    yaml_obj.dump(item, f)
    f.seek(0)
    string = f.read()
    return string

【代码片段结束】
【XAgentGen/xgen/server/message_formater.py代码片段结束】

**注意**：使用该代码时需要注意以下几点：
- 该函数适用于将Python对象转换为自定义的YAML格式。
- 输入的item对象可以是任意类型，包括字典、字符串等。
- 如果item是字典类型，则会递归调用custom_yaml_dump函数对字典中的值进行转换。
- 如果item是字符串类型且包含换行符，则会调用literal函数将字符串转换为YAML格式。
- 其他情况下，item会被直接返回。

**输出示例**：模拟该函数返回值的可能外观。
```python
{
    'key1': 'value1',
    'key2': {
        'subkey1': 'subvalue1',
        'subkey2': 'subvalue2'
    },
    'key3': None
}
```
***
# FunctionDef yaml_load
**yaml_load函数**：该函数的功能是将字符串解析为YAML格式的数据。

该函数接受一个字符串作为输入参数，然后使用StringIO将字符串转换为文件对象f。接下来，使用yaml_obj.load方法将文件对象f中的数据解析为YAML格式的数据，并将解析结果存储在变量data中。最后，将解析结果data作为函数的返回值。

需要注意的是，该函数依赖于yaml_obj对象的load方法进行解析操作。在调用该函数之前，需要确保yaml_obj对象已经正确初始化，并且yaml模块已经正确导入。

**注意**：在使用该函数时，需要注意以下几点：
- 确保传入的字符串参数符合YAML格式的语法规范，否则可能会导致解析失败。
- 确保yaml_obj对象已经正确初始化，并且yaml模块已经正确导入。

**输出示例**：假设输入字符串为"key: value"，则函数的返回值为{'key': 'value'}。
***
# FunctionDef yaml_dump
**yaml_dump函数**：该函数的功能是将输入的item对象转换为yaml格式的字符串。

该函数首先创建一个StringIO对象f，用于存储转换后的字符串。然后调用custom_yaml_dump函数对item进行自定义的转换处理。接下来，使用yaml_obj.dump方法将转换后的item对象写入到f中。然后，将f的指针移动到文件开头，并读取f中的内容，将其作为字符串返回。

在项目中，该函数在XAgentGen/xgen/server/message_formater.py文件中被调用。具体调用代码如下：

```python
def my_dump(item, dump_method):
    item = json_try(item)
    if dump_method == 'yaml':
        return yaml_dump(item)
    elif dump_method == 'json':
        return json.dumps(item, ensure_ascii=False)
    else:
        raise NotImplementedError
```

**注意**：使用该函数时需要注意以下几点：
- 输入的item对象需要满足转换为yaml格式的要求。
- dump_method参数只能为'yaml'或'json'，否则会抛出NotImplementedError异常。

**输出示例**：以下是该函数可能返回的字符串的示例：
```
name: John
age: 30
city: New York
```
***
# FunctionDef message_format
**message_format函数**：该函数的功能是根据传入的消息格式化字符串。

该函数接受一个名为msg的参数，该参数是一个字典类型的消息。函数首先判断消息的角色，如果角色是"user"，则将消息的内容添加到格式化字符串中，并在开头添加特定的起始标记和实例标记；如果角色是"assistant"，则直接将消息的内容添加到格式化字符串中，并在结尾添加特定的结束标记；否则，抛出NotImplementedError异常。最后，函数返回格式化后的字符串。

该函数在以下文件中被调用：
文件路径：XAgentGen/xgen/server/message_formater.py
对应代码如下：
```python
def format(item, dump_method='yaml'):
    """
    reformat the request item
    item: {"messages": ..., "arguments": ..., "functions": ..., "function_call": ...}
    """
    if "arguments" in item and item['arguments'] is not None and len(item['arguments']) > 0:
        arguments_string = "# Global Arguments\n" + my_dump(item["arguments"], "yaml")
    else:
        arguments_string = ""
    if "functions" in item and item['functions'] is not None and len(item['functions']) > 0:
        functions_string = "# Functions\n" + my_dump(item["functions"], "yaml")
    else:
        functions_string = ""
    if "function_call" in item and item['function_call'] is not None and 'name' in item['function_call']:
        function_call_string = f"You need to use {item['function_call']['name']} function."
    else:
        function_call_string = ""
    system_prefix = (
        "Response with following json schemas:\n" +
        f"{arguments_string}\n{functions_string}\n{function_call_string}"
    )
    system_prefix = system_prefix.strip()

    dialog = item["messages"]
    sys_msg_idx = find_system_msg(dialog)
    if sys_msg_idx == -1:
        dialog.insert(0, {"role": "system", "content": system_prefix})
    else:
        dialog[sys_msg_idx]["content"] += "\n" + system_prefix

    dialog = merge_messages(dialog)
    input_string = "".join([message_format(msg) for msg in dialog])
    return input_string
```
[此部分代码结束]
[XAgentGen/xgen/server/message_formater.py代码结束]

**注意**：使用该代码时需要注意以下几点：
- 传入的msg参数必须是一个字典类型的消息，且必须包含"role"和"content"两个键。
- 消息的角色只能是"user"或"assistant"，否则会抛出NotImplementedError异常。

**输出示例**：模拟该代码返回值的可能外观。
```
# Global Arguments
- argument1: value1
- argument2: value2

# Functions
- function1:
    - argument1: value1
    - argument2: value2

You need to use function1 function.

User: [BOS] 用户消息内容 [E_INST] 
Assistant: 助手消息内容[EOS]
```
以上是对目标对象的详细解释文档，包括函数的功能、代码分析和描述、使用注意事项以及输出示例。
***
# FunctionDef merge_messages
**merge_messages函数**：该函数的功能是将消息列表中的连续相同角色的消息合并为一个消息。

该函数接受一个消息列表作为输入参数，然后遍历消息列表中的每个消息。如果当前消息的角色是系统消息，则将角色设置为用户，并在内容前后添加特殊标记。否则，将角色设置为当前消息的角色，并将内容设置为当前消息的内容。

接下来，函数会检查当前消息的角色是否与上一个消息的角色相同。如果相同，则将当前消息的内容追加到上一个消息的内容后面，以换行符分隔。如果不同，则将当前消息添加到新的消息列表中。

最后，函数返回合并后的新消息列表。

**注意**：在使用该代码时需要注意以下几点：
- 输入参数messages应为一个消息列表，其中每个消息应包含角色和内容。
- 返回值为一个新的消息列表，其中连续相同角色的消息已合并。

**输出示例**：假设输入的消息列表为：
```
[
    {"role": "user", "content": "Hello"},
    {"role": "user", "content": "How are you?"},
    {"role": "system", "content": "I'm fine, thank you."}
]
```
则函数的返回值为：
```
[
    {"role": "user", "content": "Hello\nHow are you?"},
    {"role": "user", "content": "I'm fine, thank you."}
]
```
***
# FunctionDef find_system_msg
**find_system_msg函数**: 这个函数的功能是在给定的消息列表中查找系统消息，并返回系统消息的索引。

该函数接受一个消息列表作为参数，然后遍历列表中的每个消息，判断消息的"role"属性是否为"system"，如果是，则将该消息的索引赋值给变量idx。最后，函数返回变量idx，即系统消息的索引。

该函数在项目中的以下文件中被调用：
文件路径：XAgentGen/xgen/server/message_formater.py
对应代码如下：
```python
def format(item, dump_method='yaml'):
    """
    重新格式化请求项
    item: {"messages": ..., "arguments": ..., "functions": ..., "function_call": ...}
    """
    if "arguments" in item and item['arguments'] is not None and len(item['arguments']) > 0:
        arguments_string = "# 全局参数\n" + my_dump(item["arguments"], "yaml")
    else:
        arguments_string = ""
    if "functions" in item and item['functions'] is not None and len(item['functions']) > 0:
        functions_string = "# 函数\n" + my_dump(item["functions"], "yaml")
    else:
        functions_string = ""
    if "function_call" in item and item['function_call'] is not None and 'name' in item['function_call']:
        function_call_string = f"你需要使用 {item['function_call']['name']} 函数。"
    else:
        function_call_string = ""
    system_prefix = (
        "响应的JSON模式如下：\n" +
        f"{arguments_string}\n{functions_string}\n{function_call_string}"
    )
    system_prefix = system_prefix.strip()

    dialog = item["messages"]
    sys_msg_idx = find_system_msg(dialog)
    if sys_msg_idx == -1:
        dialog.insert(0, {"role": "system", "content": system_prefix})
    else:
        dialog[sys_msg_idx]["content"] += "\n" + system_prefix

    dialog = merge_messages(dialog)
    input_string = "".join([message_format(msg) for msg in dialog])
    return input_string
```
[此部分代码结束]
[XAgentGen/xgen/server/message_formater.py代码结束]

**find_system_msg函数**的功能是在给定的消息列表中查找系统消息，并返回系统消息的索引。

该函数通过遍历消息列表中的每个消息，判断消息的"role"属性是否为"system"来找到系统消息。如果找到了系统消息，则将该消息的索引赋值给变量idx。最后，函数返回变量idx，即系统消息的索引。

**注意**：该函数的返回值为系统消息的索引，如果找不到系统消息，则返回-1。

**输出示例**：假设给定的消息列表为：
```python
messages = [
    {"role": "user", "content": "你好"},
    {"role": "system", "content": "系统消息1"},
    {"role": "user", "content": "请问有什么问题？"},
    {"role": "system", "content": "系统消息2"},
    {"role": "user", "content": "谢谢"}
]
```
调用find_system_msg(messages)的返回值为2，表示系统消息2的索引为2。
***
# FunctionDef my_dump
**my_dump函数**：该函数的功能是根据指定的dump方法将item对象转换为字符串。

该函数接受两个参数：
- item：要转换的对象。
- dump_method：指定的转换方法，可选值为'yaml'或'json'。

函数内部首先对item对象进行了json_try操作，将其转换为JSON格式。然后根据dump_method的取值，分别使用yaml_dump和json.dumps方法将item对象转换为字符串。如果dump_method的取值不是'yaml'或'json'，则抛出NotImplementedError异常。

**注意**：在使用该函数时，需要确保dump_method参数的取值为'yaml'或'json'，否则将会抛出异常。

**输出示例**：假设item对象为{"name": "John", "age": 25}，dump_method为'json'，则函数的返回值为'{"name": "John", "age": 25}'。
***
# FunctionDef json_try
**json_try函数**: 这个函数的功能是尝试将输入的item转换为JSON格式的数据。它会递归地检查item的类型，如果是字符串类型，则尝试将其解析为JSON对象；如果是字典类型，则递归地对字典中的每个值进行转换；如果是列表类型，则递归地对列表中的每个元素进行转换；其他类型则直接返回。最终返回转换后的JSON数据。

该函数在项目中的以下文件中被调用：
文件路径：XAgentGen/xgen/server/message_formater.py
对应代码如下：
```python
def my_dump(item, dump_method):
    item = json_try(item)
    if dump_method == 'yaml':
        return yaml_dump(item)
    elif dump_method == 'json':
        return json.dumps(item, ensure_ascii=False)
    else:
        raise NotImplementedError
```
[代码片段结束]
对应代码如下：
```python
def json_try(item):
    if isinstance(item, str):
        try:
            x = json.loads(item)
            if not isinstance(x, str):
                return json_try(x)
            else:
                return x
        except:
            return item
    elif isinstance(item, dict):
        data = {}
        for key, value in item.items():
            data[key] = json_try(value)
        return data if len(data) > 0 else None
    elif isinstance(item, list):
        data = []
        for x in item:
            data.append(json_try(x))
        return data if len(data) > 0 else None
    else:
        return item
```
[代码片段结束]
对应代码如下：
```python
def json_try(item):
    if isinstance(item, str):
        try:
            x = json.loads(item)
            if not isinstance(x, str):
                return json_try(x)
            else:
                return x
        except:
            return item
    elif isinstance(item, dict):
        data = {}
        for key, value in item.items():
            data[key] = json_try(value)
        return data if len(data) > 0 else None
    elif isinstance(item, list):
        data = []
        for x in item:
            data.append(json_try(x))
        return data if len(data) > 0 else None
    else:
        return item
```
[代码片段结束]
对应代码如下：
```python
def json_try(item):
    if isinstance(item, str):
        try:
            x = json.loads(item)
            if not isinstance(x, str):
                return json_try(x)
            else:
                return x
        except:
            return item
    elif isinstance(item, dict):
        data = {}
        for key, value in item.items():
            data[key] = json_try(value)
        return data if len(data) > 0 else None
    elif isinstance(item, list):
        data = []
        for x in item:
            data.append(json_try(x))
        return data if len(data) > 0 else None
    else:
        return item
```
[代码片段结束]
[End of XAgentGen/xgen/server/message_formater.py]

**注意**: 在使用该代码时需要注意以下几点：
- 输入的item应为合法的JSON字符串、字典或列表。
- 如果item无法解析为JSON对象，则会直接返回原始的item。
- 返回的JSON数据可能是字典、列表或其他基本数据类型。

**输出示例**: 模拟代码返回值的可能外观。
```python
{
    "key1": "value1",
    "key2": {
        "nested_key": "nested_value"
    },
    "key3": [
        "item1",
        "item2"
    ]
}
```
***
# FunctionDef my_load
**my_load函数**：该函数的功能是根据指定的dump方法将字符串加载为相应的数据结构。

该函数接受两个参数：string（要加载的字符串）和dump_method（指定的dump方法）。根据dump_method的值，函数将使用相应的方法将字符串加载为数据结构。如果dump_method为'yaml'，则调用yaml_load函数将字符串加载为YAML格式的数据结构；如果dump_method为'json'，则调用json.loads函数将字符串加载为JSON格式的数据结构。如果dump_method的值不是'yaml'或'json'，则抛出NotImplementedError异常。

**注意**：在使用该函数时需要注意以下几点：
- 确保传入的字符串符合指定的dump方法所需的格式。
- 确保dump_method的值为'yaml'或'json'，否则会抛出异常。

**输出示例**：假设传入的字符串为'{"name": "John", "age": 30}'，dump_method为'json'，则函数将返回以下数据结构：
{
  "name": "John",
  "age": 30
}
***
# FunctionDef format
**format函数**：这个函数的功能是重新格式化请求项。

该函数接受两个参数：item和dump_method。item是一个字典，包含了请求的消息、参数、函数和函数调用等信息。dump_method是一个字符串，表示转储方法的类型，默认为'yaml'。

函数首先判断item中是否存在参数（arguments）、函数（functions）和函数调用（function_call）的信息。如果存在，则将它们转储为字符串，并添加相应的注释。如果不存在，则将对应的字符串置为空。

接下来，函数将系统前缀（system_prefix）设置为包含参数、函数和函数调用信息的字符串。然后，函数将对话（dialog）中的系统消息（system message）与系统前缀进行合并。

之后，函数将对话中的消息进行合并，并将每个消息转换为字符串。最后，将所有转换后的字符串拼接在一起，并返回结果。

**注意**：在使用该函数时需要注意以下几点：
- item参数必须是一个字典，包含了请求的消息、参数、函数和函数调用等信息。
- dump_method参数是一个字符串，表示转储方法的类型，默认为'yaml'。

**输出示例**：假设item参数为{"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "How can I help you?"}], "arguments": {"arg1": "value1", "arg2": "value2"}, "functions": {"func1": "value1", "func2": "value2"}, "function_call": {"name": "my_function"}}，则函数的返回值为以下字符串：
```
Hello
How can I help you?
# Global Arguments
arg1: value1
arg2: value2
# Functions
func1: value1
func2: value2
You need to use my_function function.
```
***
