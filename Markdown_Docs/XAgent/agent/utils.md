# FunctionDef get_command
**get_command函数**：该函数的作用是解析响应并返回命令名称和参数。

该函数会抛出`json.decoder.JSONDecodeError`异常，如果响应不是有效的JSON格式。如果发生其他任何错误，也会捕获并返回一个带有异常消息的"Error:"信息。

参数：
- response_json (Dict)：以字典格式表示的AI的响应。

返回值：
- tuple：命令名称和参数，或者一些错误指示。
  - 如果响应的JSON字典中不包含'command'键，或者'command'的值不是字典，或者'command'字典中不包含'name'键，则返回一个元组，其中第一个元素是'Error:'，第二个元素是解释问题的字符串。
  - 如果发生错误，则返回一个元组，其中第一个元素是'Error:'，第二个元素是异常的字符串表示。

抛出异常：
- json.decoder.JSONDecodeError：如果响应不是有效的JSON格式。
- Exception：如果发生其他任何错误。

该函数首先检查响应中是否包含'command'键，如果不包含，则返回一个错误信息。然后，它检查响应是否是字典格式，如果不是，则返回一个错误信息。接下来，它获取'command'对象，并检查它是否是字典格式，如果不是，则返回一个错误信息。然后，它检查'command'对象中是否包含'name'键，如果不包含，则返回一个错误信息。最后，它获取命令名称和参数，并返回它们。

如果发生`json.decoder.JSONDecodeError`异常，表示响应不是有效的JSON格式，函数会返回一个错误信息。如果发生其他任何异常，函数会返回一个带有异常消息的错误信息。

**注意**：使用该代码时需要注意以下几点：
- 确保响应是有效的JSON格式。
- 确保响应的字典中包含'command'键，并且'command'的值是一个字典。
- 确保'command'字典中包含'name'键。

**输出示例**：
```
command_name = "search"
arguments = {"query": "apple", "limit": 10}
```
***
