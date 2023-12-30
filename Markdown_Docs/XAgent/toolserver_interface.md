# FunctionDef is_wrapped_response
**is_wrapped_response函数**：该函数的功能是检查响应对象是否被包装。

该函数接受一个字典类型的参数obj，表示响应对象。函数返回一个布尔值，如果响应对象被包装，则返回True，否则返回False。

具体而言，该函数会检查obj字典中是否包含键'type'，并且该键对应的值是['simple', 'composite', 'binary']中的一个，并且字典中还包含键'data'。如果满足这些条件，则认为响应对象被包装。

在项目中，该函数被XAgent/toolserver_interface.py文件中的unwrap_tool_response函数调用。unwrap_tool_response函数用于解包工具的响应对象。在unwrap_tool_response函数中，如果传入的obj参数是一个字典类型，并且is_wrapped_response函数返回True，则根据obj字典中'type'的值进行不同的处理。如果'type'是'simple'，则返回obj字典中的'data'值；如果'type'是'binary'，则将'data'值解码为二进制数据，并根据'media_type'和'name'生成文件名，将解码后的数据写入文件，并返回包含'media_type'和'file_name'的字典；如果'type'是'composite'，则递归调用unwrap_tool_response函数对'data'中的每个元素进行解包，并返回解包后的列表。如果is_wrapped_response函数返回False，则直接返回传入的obj参数。

需要注意的是，is_wrapped_response函数还会对obj参数进行类型判断，如果obj是字符串、整数、浮点数、布尔值或列表类型，则直接返回obj。如果obj是None，则返回None。如果obj是其他类型，则会打印警告信息，并返回None。

**注意**：使用该代码时需要注意以下几点：
- 传入的obj参数必须是一个字典类型。
- obj字典中必须包含键'type'和'data'。
- 'type'的值必须是['simple', 'composite', 'binary']中的一个。

**输出示例**：模拟代码返回值的可能外观。
```python
True
```
***
# FunctionDef unwrap_tool_response
**unwrap_tool_response函数**：该函数的功能是解包工具响应对象。

该函数接受两个参数：
- obj：工具响应对象。
- logger：日志记录器。

该函数的返回值是解包后的工具响应对象。

该函数的详细代码分析和描述如下：
- 首先，判断obj的类型是否为字典。如果是字典类型，并且是被包装的响应对象（通过is_wrapped_response函数判断），则根据obj['type']的值进行不同的处理。
  - 如果obj['type']的值为'simple'，则直接返回obj['data']。
  - 如果obj['type']的值为'binary'，则根据obj中的信息生成一个文件名name，并根据obj['media_type']的值判断是否为图片类型。如果是图片类型且文件名不以'.png'结尾，则在文件名后添加'.png'后缀。然后，将obj['data']解码为二进制数据，并将其写入到本地工作空间中的文件中。最后，返回一个包含媒体类型和文件名的字典。
  - 如果obj['type']的值为'composite'，则遍历obj['data']中的每个元素，对每个元素递归调用unwrap_tool_response函数，并将结果存入一个列表中。最后，返回该列表作为结果。
- 如果obj的类型是字符串、整数、浮点数、布尔值或列表，则直接返回obj。
- 如果obj为None，则返回None。
- 如果obj的类型不在上述类型中，则使用日志记录器logger记录一条警告日志，内容为"Unknown type {type(obj)} in unwrap_tool_response"，并返回None作为结果。

**注意**：使用该代码时需要注意以下几点：
- 该函数依赖于is_wrapped_response函数，需要确保该函数的正确性。
- 该函数会根据工具响应对象的类型进行不同的处理，需要根据实际情况进行调用和使用。

**输出示例**：模拟该函数返回值的可能外观。
```python
{
    'media_type': 'image/png',
    'file_name': 'example.png'
}
```
***
# ClassDef ToolServerInterface
**ToolServerInterface函数**: 这个类的功能是与ToolServer进行通信的接口。

该类的主要功能是与ToolServer进行通信，包括上传文件、下载文件、获取工作空间结构、获取可用工具等操作。它还提供了懒惰初始化和关闭ToolServer会话的方法。

该类的构造函数接受一个RunningRecoder对象和一个可选的logger对象作为参数。它将RunningRecoder对象赋值给self.recorder属性，将logger对象赋值给self.logger属性。

lazy_init方法是ToolServer接口的懒惰初始化方法。它接受一个config参数，用于配置ToolServer。如果config中设置了使用自托管的ToolServer，则将self.url设置为config中指定的自托管ToolServer的URL；否则，抛出NotImplementedError异常，提示使用自托管ToolServer。然后，向self.url发送一个POST请求，获取ToolServer的cookie，并将cookie保存在self.cookies属性中。

close方法用于关闭ToolServer会话。它向self.url发送一个POST请求，关闭ToolServer会话。

upload_file方法用于将文件上传到ToolServer。它接受一个file_path参数，表示要上传的文件的路径。首先构造一个URL，然后使用requests库向该URL发送一个POST请求，将文件作为multipart/form-data形式的数据发送。请求中包含文件的路径和文件名。最后，将响应内容以JSON格式返回。

download_file方法用于从ToolServer下载文件。它接受一个file_path参数，表示要下载的文件的路径。首先构造一个URL，然后构造一个payload，包含要下载的文件的路径。使用requests库向该URL发送一个POST请求，将payload作为JSON数据发送。然后将响应内容保存到本地文件中，并返回保存文件的路径。

get_workspace_structure方法用于获取ToolServer的工作空间结构。它构造一个URL，使用requests库向该URL发送一个POST请求，获取工作空间的结构，并将响应内容以JSON格式返回。

download_all_files方法用于下载ToolServer工作空间中的所有文件。它构造一个URL，使用requests库向该URL发送一个POST请求，下载工作空间的所有文件，并将响应内容保存到本地文件中，并返回保存文件的路径。

get_available_tools方法用于获取ToolServer中可用的工具。它构造一个URL，使用requests库向该URL发送一个POST请求，获取可用工具的列表，并将响应内容以JSON格式返回。

retrieve_rapidapi_tools方法用于从ToolServer检索RapidAPI工具。它接受一个query参数和一个可选的top_k参数，用于指定检索的查询和返回的工具数量。首先构造一个URL，然后构造一个payload，包含查询和top_k参数。使用requests库向该URL发送一个POST请求，将payload作为JSON数据发送。然后将响应内容保存到本地文件中，并返回保存文件的路径。

get_json_schema_for_tools方法用于获取指定工具的JSON模式。它接受一个command_names参数，表示要获取JSON模式的工具的名称列表。首先构造一个URL，然后构造一个payload，包含要获取JSON模式的工具的名称列表。使用requests库向该URL发送一个POST请求，将payload作为JSON数据发送。然后将响应内容以JSON格式返回。

execute_command_client方法用于在ToolServer上执行命令。它接受一个command_name参数，表示要执行的命令的名称，以及一个arguments参数，表示要执行的命令的参数。首先构造一个URL，然后构造一个payload，包含要执行的命令的名称和参数。使用requests库向该URL发送一个POST请求，将payload作为JSON数据发送。然后将响应内容以JSON格式返回。

**注意**: 使用该类之前，需要先进行懒惰初始化，并确保ToolServer已连接。在使用upload_file和download_file方法时，需要提供文件的路径。在使用get_available_tools和retrieve_rapidapi_tools方法时，需要提供查询参数。在使用get_json_schema_for_tools和execute_command_client方法时，需要提供工具的名称和参数。

**输出示例**:
```
{
    "tool_name": "tool1",
    "arguments": {
        "arg1": "value1",
        "arg2": "value2"
    }
}
```
## FunctionDef __init__
**__init__函数**：这个函数的作用是初始化一个ToolserverInterface对象。

在这个函数中，有两个参数：recorder和logger。recorder是一个RunningRecoder对象，用于记录运行时的信息。logger是一个日志记录器对象，用于记录日志信息。

在函数体内，将传入的recorder赋值给self.recorder，将传入的logger赋值给self.logger。

**注意**：在使用这个函数时，需要传入一个RunningRecoder对象作为recorder参数，并且可以选择传入一个日志记录器对象作为logger参数。
## FunctionDef lazy_init
**lazy_init函数**：该函数的功能是进行ToolServer接口的延迟初始化。

该函数接受一个config参数，用于配置ToolServer。

如果config中的use_selfhost_toolserver为True，则将selfhost_toolserver_url赋值给url变量；否则，抛出NotImplementedError异常，提示使用selfhost toolserver。

接下来，通过requests库向self.url发送一个POST请求，路径为"{self.url}/get_cookie"，并将返回的cookies赋值给self.cookies。

在函数执行过程中，会通过self.logger.typewriter_log方法打印出"ToolServer connected in"和self.url的值。

**注意**：使用该代码时需要注意以下几点：
- 需要提供正确的ToolServer配置信息，确保config参数正确设置。
- 如果使用非selfhost ToolServer，会抛出NotImplementedError异常，需要使用selfhost ToolServer。
## FunctionDef close
**close函数**: 这个函数的功能是关闭ToolServer会话。

该函数通过发送一个POST请求来关闭ToolServer会话。请求的URL是通过在self.url后面添加'/close_session'得到的。请求中还包含了cookies，这些cookies是在初始化ToolServerInterface对象时传入的。

在项目中，该函数被调用的地方是XAgent/core.py文件中的close函数。在这个函数中，首先调用了toolserver_interface对象的download_all_files函数，然后再调用了toolserver_interface对象的close函数。

**注意**: 使用该代码时需要注意以下几点：
- 确保在调用close函数之前已经调用了download_all_files函数，以确保所有文件都已经下载完成。
- 确保在初始化ToolServerInterface对象时传入了正确的URL和cookies参数。
## FunctionDef upload_file
**upload_file函数**：该函数用于将文件上传到ToolServer。

该函数接受一个参数file_path，表示要上传的文件的路径。

函数内部首先构建了上传文件的URL，然后使用requests库发送POST请求，将文件以二进制形式上传到ToolServer。请求中包含了文件的路径和文件名。上传成功后，函数将返回ToolServer的响应。

**注意**：使用该函数前需要确保ToolServer已经启动，并且传入的file_path参数是有效的文件路径。

**输出示例**：假设ToolServer返回的响应为"Upload successful"，则函数的返回值为"Upload successful"。
## FunctionDef download_file
**download_file函数**：该函数的功能是从ToolServer下载文件。

该函数接受一个参数file_path，表示要下载的文件的路径。

函数内部首先构建了下载文件的URL，然后将file_path作为payload的值传递给ToolServer，使用POST请求发送下载文件的请求。请求中还包括了超时时间和cookies信息。如果请求失败，会抛出异常。

接下来，函数根据下载文件的保存路径构建了保存文件的路径save_path，并创建了保存文件的目录。然后使用二进制写入的方式将下载的文件内容写入到save_path指定的文件中。

最后，函数返回保存文件的路径save_path。

**注意**：使用该函数时需要确保ToolServer的URL、超时时间和cookies信息已正确设置。

**输出示例**：假设下载的文件保存在"/Users/logic/Documents/THUNLP/XAgent/XAgent/recordings/file.txt"路径下，则函数的返回值为"/Users/logic/Documents/THUNLP/XAgent/XAgent/recordings/file.txt"。
## FunctionDef get_workspace_structure
**get_workspace_structure函数**：该函数的功能是从ToolServer获取工作空间的结构。

该函数通过向ToolServer发送POST请求，获取工作空间的结构信息。请求的URL为`{self.url}/get_workspace_structure`，超时时间为10秒，使用了之前保存的cookies进行身份验证。请求成功后，将返回的响应转换为JSON格式，并将其作为函数的返回值。

**注意**：使用该代码时需要注意以下几点：
- 需要确保ToolServer的URL正确配置，并且ToolServer已经启动。
- 需要确保ToolServer的cookies已经保存，并且具有访问工作空间结构的权限。

**输出示例**：模拟该代码返回值的可能外观。
```python
{
    "workspace": {
        "name": "MyWorkspace",
        "folders": [
            {
                "name": "Folder1",
                "files": [
                    {
                        "name": "File1.txt",
                        "size": "10KB"
                    },
                    {
                        "name": "File2.txt",
                        "size": "5KB"
                    }
                ]
            },
            {
                "name": "Folder2",
                "files": [
                    {
                        "name": "File3.txt",
                        "size": "8KB"
                    }
                ]
            }
        ]
    }
}
```
## FunctionDef download_all_files
**download_all_files函数**：该函数的功能是从ToolServer下载工作空间中的所有文件。

该函数首先构造了一个下载工作空间的URL，然后通过发送POST请求到该URL来获取响应。如果请求成功，函数将会将响应内容写入到指定的保存路径中，并返回保存路径。

在函数内部，首先构造了下载工作空间的URL，URL的构造使用了self.url和/download_workspace两个部分。self.url是ToolServer的URL地址，/download_workspace是下载工作空间的接口路径。通过将这两个部分拼接在一起，得到了完整的下载工作空间的URL。

然后，使用requests库发送了一个POST请求到下载工作空间的URL，并传递了cookies参数。函数使用了requests.post方法来发送POST请求，并将响应保存在response变量中。

接下来，函数调用了response.raise_for_status()方法来检查请求是否成功。如果请求失败，将会抛出一个异常。

然后，函数构造了保存路径save_path，使用了os.path.join方法将self.recorder.record_root_dir和'workspace.zip'拼接在一起。self.recorder.record_root_dir是工作空间的保存路径，'workspace.zip'是保存文件的文件名。

接着，函数使用os.makedirs方法创建了保存路径的父目录，如果父目录不存在的话。

最后，函数使用了with open语句打开保存路径的文件，并以二进制写入的方式将响应内容写入到文件中。

函数最后返回保存路径save_path。

**注意**：使用该函数前需要确保ToolServer的URL地址已经设置，并且需要确保已经登录并获取了cookies。

**输出示例**：假设保存路径为'/path/to/workspace.zip'，则函数的返回值为'/path/to/workspace.zip'。
## FunctionDef get_available_tools
**get_available_tools函数**：该函数的功能是从ToolServer获取可用的工具。

该函数首先构造了一个空的payload字典，并根据self.url拼接出请求的url。然后通过调用self.recorder.query_tool_server_cache方法，查询ToolServer的缓存数据，传入url和payload作为参数。如果缓存数据不为空，则将缓存数据中的工具输出和响应状态码分别赋值给response和status_code变量。如果缓存数据为空，则通过requests库发送POST请求，将url、payload、timeout和cookies作为参数传入，获取响应结果。然后检查响应的状态码，如果不是200，则抛出异常。接着将响应结果转换为JSON格式，并将其赋值给response变量。如果响应结果不是字典类型，则再次将其转换为JSON格式。最后，调用self.recorder.regist_tool_server方法，将url、payload、工具输出和响应状态码注册到记录器中。最后返回响应结果。

**注意**：在调用该函数之前，需要确保ToolServer的URL、payload和cookies已经设置好。

**输出示例**：假设响应结果为以下格式：
```
{
    "available_tools": ["tool1", "tool2", "tool3"],
    "tools_json": {
        "tool1": {
            "name": "tool1",
            "description": "This is tool1"
        },
        "tool2": {
            "name": "tool2",
            "description": "This is tool2"
        },
        "tool3": {
            "name": "tool3",
            "description": "This is tool3"
        }
    }
}
```
则函数返回的结果为以上示例的字典形式。
## FunctionDef retrieve_rapidapi_tools
**retrieve_rapidapi_tools函数**：该函数用于从ToolServer检索RapidAPI工具。

该函数接受以下参数：
- query（str）：用于检索工具的查询字符串。
- top_k（int，可选）：要检索的工具数量，默认为10。

该函数返回以JSON格式表示的检索到的工具及其描述。

该函数的具体代码分析和描述如下：
- 首先，根据传入的查询字符串和检索数量，构造了用于检索工具的URL和payload。
- 然后，通过调用self.recorder.query_tool_server_cache函数，从缓存中获取工具的输出结果。
- 如果缓存中存在输出结果，则将结果赋值给response和status_code变量。
- 如果缓存中不存在输出结果，则通过发送POST请求到ToolServer，获取工具的输出结果，并将结果赋值给response变量。
- 接着，将工具的输出结果和状态码注册到self.recorder中。
- 最后，从输出结果中提取检索到的工具和工具的描述，并将每个工具的描述注册到function_manager中。

注意事项：
- 如果在检索工具的过程中出现异常，将会打印错误信息并返回None。

输出示例：
```
retrieved_tools = ["Tool1", "Tool2", "Tool3"]
tools_json = [
    {
        "name": "Tool1",
        "description": "This is Tool1"
    },
    {
        "name": "Tool2",
        "description": "This is Tool2"
    },
    {
        "name": "Tool3",
        "description": "This is Tool3"
    }
]
```
## FunctionDef get_json_schema_for_tools
**get_json_schema_for_tools函数**: 该函数的作用是从ToolServer获取指定工具的JSON模式。

该函数接受一个参数command_names，用于指定工具的名称。

函数内部首先构建了请求的URL，并创建了payload参数，其中包含了工具的名称。

接下来，函数通过调用recorder对象的query_tool_server_cache方法，从缓存中查询是否存在该URL和payload的缓存结果。如果存在缓存结果，则直接返回缓存的工具输出和状态码；否则，函数会发送一个POST请求到指定的URL，并将payload以JSON格式发送。函数还设置了超时时间为10秒，并携带了cookies信息。

在获取到响应后，函数首先获取响应的状态码，并将响应内容解析为JSON格式。如果响应内容不是一个字典类型，则函数尝试将其解析为JSON格式。如果解析失败，则不进行处理。

接下来，函数调用recorder对象的regist_tool_server方法，将URL、payload、工具输出和响应状态码注册到recorder中。

然后，函数调用function_manager对象的register_function方法，将工具输出注册到function_manager中。

最后，函数返回工具输出作为结果。

如果在执行过程中出现异常，函数会打印错误信息，并返回None。

**注意**: 使用该代码时需要注意以下几点：
- 需要确保ToolServer的URL正确配置。
- 需要确保ToolServer的cookies信息正确配置。
- 需要确保ToolServer的响应是一个有效的JSON格式。

**输出示例**：模拟代码返回值的可能外观。

```python
{
    "tool1": {
        "input": {
            "type": "string",
            "description": "Input string"
        },
        "output": {
            "type": "string",
            "description": "Output string"
        }
    },
    "tool2": {
        "input": {
            "type": "number",
            "description": "Input number"
        },
        "output": {
            "type": "number",
            "description": "Output number"
        }
    }
}
```
## FunctionDef execute_command_client
**execute_command_client函数**：此函数的功能是在ToolServer上执行命令。

该函数接受以下参数：
- command_name（str）：命令的名称。
- arguments（dict，可选）：命令的参数。默认为{}。
- input_hash_id：输入的哈希ID。

该函数返回以下结果：
- mixed：命令的结果和工具输出的状态码。

该函数的详细分析和描述如下：
- 首先，根据传入的参数构造URL。
- 然后，将arguments参数转换为JSON格式。
- 接下来，构造payload，包括tool_name和arguments。
- 调用self.recorder.query_tool_server_cache函数查询缓存的输出结果。
- 如果self.config['experiment']['redo_action']为True或者缓存输出为空，则发送POST请求到ToolServer，并获取响应。
- 根据响应的状态码进行不同的处理：
  - 如果状态码为200或450，则将响应的JSON结果进行解析。
  - 否则，将响应的文本结果作为命令的结果。
- 如果缓存输出不为空，则使用缓存的输出结果和响应的状态码作为命令的结果和工具输出的状态码。
- 调用self.recorder.regist_tool_server函数将URL、payload、命令的结果和响应的状态码注册到记录器中。
- 根据响应的状态码设置工具输出的状态码。
- 返回命令的结果和工具输出的状态码。

**注意**：在使用该函数时，需要注意以下几点：
- 需要提供正确的command_name和arguments参数。
- 可能会出现网络请求失败或超时的情况，需要进行错误处理。

**输出示例**：可能的返回值示例为("Command result", ToolCallStatusCode.TOOL_CALL_SUCCESS)。
***
