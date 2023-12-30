# ClassDef BaseAgent
**BaseAgent类的功能**：BaseAgent类是一个抽象基类，它为继承它的类提供了必要的属性和方法。它是Abstract Base Class (abc模块)的元类。

**属性**：
- abilities (set)：BaseAgent所需的一组RequiredAbilities，这些是BaseAgent所需的必要技能。

**方法**：
- \_\_init\_\_(self, config, prompt_messages: List[Message] = None)：构造一个具有设置的能力、配置设置和初始提示消息的代理对象。
  - 参数：
    - config (obj)：代理的配置设置。
    - prompt_messages (List)：初始的提示消息列表。
- parse(self, **args) -> (LLMStatusCode, Message, dict)：抽象方法，需要子类实现。用于解析给定的参数。
- fill_in_placeholders(self, placeholders: dict)：用提供的值填充输入中的占位符。
  - 参数：
    - placeholders (dict)：包含占位符和其替换值的字典。
  - 返回值：
    - filled_messages：将占位符替换为相应值后的初始提示消息的副本。
- generate(self, messages:list[dict]|list[Message], arguments:dict=None, functions:list[dict]=None, function_call:dict=None, stop:dict=None, *args,**kwargs)：使用给定的消息、参数、函数和函数调用生成AI模型的响应。
  - 参数：
    - messages (list[dict]|list[Message])：与AI模型交互的消息列表。
    - arguments (dict, optional)：用于AI模型响应的参数字典。
    - functions (list[dict], optional)：表示用于AI模型响应的函数列表。
    - function_call (dict, optional)：表示用于AI模型响应的函数调用的字典。
    - stop (dict, optional)：指示何时停止与AI模型的对话的字典。
    - *args：可变长度参数列表。
    - **kwargs：任意关键字参数。
  - 返回值：
    - message (dict)：AI模型生成的消息。
    - tokens (int)：生成AI模型响应所使用的令牌数。

**注意**：在使用`generate`方法时，需要根据具体情况传递不同的参数，如`messages`、`arguments`、`functions`、`function_call`和`stop`。

**示例输出**：
```python
config = ...
agent = BaseAgent(config)
placeholders = {
    "system": {
        "placeholder1": "value1",
        "placeholder2": "value2"
    },
    "user": {
        "placeholder3": "value3",
        "placeholder4": "value4"
    }
}
filled_messages = agent.fill_in_placeholders(placeholders)
print(filled_messages)
# Output:
# [Message(role='system', content='System message with value1 and value2'),
#  Message(role='user', content='User message with value3 and value4')]

messages = [
    Message(role='system', content='System message'),
    Message(role='user', content='User message')
]
arguments = {
    'arg1': 'value1',
    'arg2': 'value2'
}
functions = [
    {
        'name': 'function1',
        'parameters': {
            'param1': 'value1',
            'param2': 'value2'
        }
    }
]
function_call = {
    'name': 'function1',
    'arguments': {
        'arg1': 'value1',
        'arg2': 'value2'
    }
}
stop = {
    'condition': 'stop_condition'
}
message, tokens = agent.generate(messages, arguments, functions, function_call, stop)
print(message)
print(tokens)
# Output:
# {'content': 'Generated message', 'function_call': {'name': 'function1', 'arguments': {'arg1': 'value1', 'arg2': 'value2'}}}
# 100
```
## FunctionDef __init__
**__init__函数**：这个函数的作用是构建一个具有设置能力、配置设置和初始提示消息集的Agent对象。

详细代码分析和描述：
- 参数config是Agent的配置设置，它是一个对象。
- 参数prompt_messages是Agent的初始提示消息集，它是一个消息列表，默认为None。
- 函数内部使用logger.typewriter_log方法打印一条日志，记录正在构建Agent对象的过程。
- 将参数config赋值给self.config，将参数prompt_messages赋值给self.prompt_messages。
- 将self.usage初始化为空字典。

**注意**：关于代码使用的注意事项
## FunctionDef parse
**parse函数**：该函数的功能是解析给定的参数。这是一个抽象方法，需要由子类实现。用于解析给定的参数。

**代码分析和描述**：
parse函数是一个抽象方法，需要由子类实现。它接受一个名为args的关键字参数，并返回一个元组，包含LLMStatusCode、Message和dict类型的值。该函数没有具体的实现，只是一个占位符，需要在子类中进行实现。

**注意**：parse函数是一个抽象方法，需要在子类中进行实现。在实现时，需要根据具体的需求解析给定的参数，并返回相应的结果。
## FunctionDef fill_in_placeholders
**fill_in_placeholders函数**：该函数用于填充输入中定义的占位符，将其替换为相应的值。

该函数接受一个字典作为参数，其中键为占位符，值为其替换值。

函数返回一个填充了占位符的初始prompt_messages的副本。

该函数的具体实现如下：
```python
def fill_in_placeholders(self, placeholders: dict):
    filled_messages = deepcopy(self.prompt_messages)
    for message in filled_messages:
        role = message.role
        if role in placeholders:
            for key, value in placeholders[role].items():
                message.content = message.content.replace("{{" + str(key) + "}}", str(value))
    return filled_messages
```

**注意**：在使用该函数时需要注意以下几点：
- placeholders参数是一个字典，其中键为占位符，值为其替换值。
- 该函数会返回一个填充了占位符的初始prompt_messages的副本。

**输出示例**：一个可能的返回值示例
```python
[
    Message(role='user', content='Hello, {{name}}!'),
    Message(role='assistant', content='Hi there, {{name}}! How can I assist you?')
]
```

该函数在以下文件中被调用：
1. 文件路径：XAgent/agent/plan_generate_agent/agent.py
   对应代码如下：
   ```python
   def parse(
       self,
       placeholders: dict = {},
       arguments: dict = None,
       functions=None,
       function_call=None,
       stop=None,
       additional_messages: List[Message] = [],
       *args,
       **kwargs
   ):
       prompt_messages = self.fill_in_placeholders(placeholders)
       messages = prompt_messages + additional_messages

       return self.generate(
           messages=messages,
           arguments=arguments,
           functions=functions,
           function_call=function_call,
           stop=stop,
           *args, **kwargs
       )
   ```
2. 文件路径：XAgent/agent/plan_refine_agent/agent.py
   对应代码如下：
   ```python
   def parse(
       self,
       placeholders: dict = {},
       arguments:dict = None,
       functions=None,
       function_call=None,
       stop=None,
       additional_messages: List[Message] = [],
       additional_insert_index: int = -1,
       *args,
       **kwargs
   ):
       prompt_messages = self.fill_in_placeholders(placeholders)
       messages =prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
       
       return self.generate(
           messages=messages,
           arguments=arguments,
           functions=functions,
           function_call=function_call,
           stop=stop,
           *args,**kwargs
       )
   ```
3. 文件路径：XAgent/agent/reflect_agent/agent.py
   对应代码如下：
   ```python
   def parse(
       self,
       placeholders: dict = {},
       arguments:dict = None,
       functions=None,
       function_call=None,
       stop=None,
       additional_messages: List[Message] = [],
       *args,
       **kwargs
   ):
       prompt_messages = self.fill_in_placeholders(placeholders)
       messages = prompt_messages + additional_messages

       return self.generate(
           messages=messages,
           arguments=arguments,
           functions=functions,
           function_call=function_call,
           stop=stop,
           *args,**kwargs
       )
   ```
4. 文件路径：XAgent/agent/tool_agent/agent.py
   对应代码如下：
   ```python
   def parse(
       self,
       placeholders: dict = {},
       arguments:dict=None,
       functions=None,
       function_call=None,
       stop=None,
       additional_messages: List[Message] = [],
       additional_insert_index: int = -1,
       *args,
       **kwargs
   ):
       prompt_messages = self.fill_in_placeholders(placeholders)
       messages = prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
       messages = [message.raw() for message in messages]
       
       if self.config.default_request_type == 'openai':
           arguments = None
           functions = list(filter(lambda x: x['name'] not in ['subtask_submit','subtask_handle'],functions))
           if CONFIG.enable_ask_human_for_help:
               functions += [function_manager.get_function_schema('ask_human_for_help')]
           messages[0]['content'] += '\n--- Avaliable Tools ---\nYou are allowed to use tools in the "subtask_handle.tool_call" function field.\nRemember the "subtask_handle.tool_call.tool_input" field should always in JSON, as following described:\n{}'.format(json.dumps(functions,indent=2))
           
           def change_tool_call_description(message:dict,reverse:bool=False):
               des_pairs = [('Use tools to handle the subtask',
                             'Use "subtask_handle" to make a normal tool call to handle the subtask'),
                            ('5.1  Please remember to generate the function call field after the "criticism" field.\n  5.2  Please check all content is in json format carefully.',
                             '5.1. Please remember to generate the "tool_call" field after the "criticism" field.\n  5.2. Please remember to generate comma if the "tool_call" field is after the "criticism" field.\n  5.3. Please check whether the **"tool_call"** field is in the function call json carefully.'),
                            ('After decide the action, use "subtask_handle" functions to apply action.',
                             'After decide the action, call functions to apply action.')]
               
               for pair in des_pairs:
                   message['content'] = message['content'].replace(pair[0],pair[1]) if reverse else message['content'].replace(pair[1],pair[0])
                   
               return message
           
           messages[0] = change_tool_call_description(messages[0])
           functions = [function_manager.get_function_schema('subtask_submit'),
                        function_manager.get_function_schema('subtask_handle')]

       message,tokens = self.generate(
           messages=messages,
           arguments=arguments,
           functions=functions,
           function_call=function_call,
           stop=stop,
           *args,**kwargs
       )

       function_call_args:dict = message['function_call']['arguments']

       if self.config.default_request_type == 'openai' and 'tool_call' in function_call_args:
           tool_schema = function_manager.get_function_schema(function_call_args['tool_call']["tool_name"])
           assert tool_schema is not None, f"Function {function_call_args['tool_call']['tool_name']} not found! Poential Schema Validation Error!"
           
           tool_call_args = function_call_args['tool_call']['tool_input'] if 'tool_input' in function_call_args['tool_call'] else ''
           
           def validate():
               nonlocal tool_schema,tool_call_args
               if isinstance(tool_call_args,str):
                   tool_call_args = {} if tool_call_args == '' else json5.loads(tool_call_args)
               jsonschema.validate(instance=tool_call_args, schema=tool_schema['parameters'])
           
           try:
               validate()
           except Exception as e:  
               messages[0] = change_tool_call_description(messages[0],reverse=True)
               tool_call_args = objgenerator.dynamic_json_fixes(
                   broken_json=tool_call_args,
                   function_schema=tool_schema,
                   messages=messages,
                   error_message=str(e))["choices"][0]["message"]["function_call"]["arguments"]
               validate()
           
           function_call_args['tool_call']['tool_input'] = tool_call_args
           
           message['function_call'] = function_call_args.pop('tool_call')
           message['function_call']['name'] = message['function_call'].pop('tool_name')
           message['function_call']['arguments'] = message['function_call'].pop('tool_input')
           message['arguments'] = function_call_args
               
       return message,tokens
   ```
## FunctionDef generate
**generate函数**：该函数用于从AI模型生成响应，使用给定的消息、参数、函数和函数调用。

该函数接受以下参数：
- messages (list[dict]|list[Message])：与AI模型交互的消息列表。
- arguments (dict, optional)：包含用于AI模型响应的参数的字典。
- functions (list[dict], optional)：包含用于AI模型响应的函数的字典列表。
- function_call (dict, optional)：表示要用于AI模型响应的函数调用的字典。
- stop (dict, optional)：表示何时停止与AI模型的对话的字典。
- *args：可变长度的参数列表。
- **kwargs：任意关键字参数。

该函数返回一个元组，包含生成的消息和生成AI模型响应所使用的令牌数。

**代码分析和描述**：
- 首先，函数检查messages参数的类型，如果是Message对象的列表，则将其转换为字典列表。
- 接下来，函数根据配置文件中的默认请求类型进行处理。
  - 如果默认请求类型是'openai'，则根据参数的情况生成相应的函数调用。
    - 如果arguments不为None，则根据arguments生成函数调用。
    - 如果functions为None或长度为0，则生成一个默认的函数调用。
    - 如果functions只有一个函数，并且function_call为None，则将该函数作为默认的函数调用。
    - 如果functions只有一个函数，并且arguments不为None，则将arguments中的属性添加到函数调用的参数中。
    - 如果functions有多个函数，则抛出NotImplementedError。
    - 调用objgenerator.chatcompletion函数，生成AI模型的响应。
    - 解析响应中的函数调用参数，并将其添加到生成的消息中。
  - 如果默认请求类型是'xagent'，则直接调用objgenerator.chatcompletion函数，生成AI模型的响应。
  - 如果默认请求类型不在以上两种情况中，则抛出NotImplementedError。
- 最后，函数返回生成的消息和使用的令牌数。

**注意**：在使用该函数时，需要注意以下几点：
- messages参数应为一个包含消息的列表，每个消息应为字典类型。
- arguments参数应为一个字典，包含用于AI模型响应的参数。
- functions参数应为一个字典列表，每个字典表示一个函数。
- function_call参数应为一个字典，表示一个函数调用。
- stop参数应为一个字典，表示何时停止与AI模型的对话。
- 函数的返回值是一个包含生成的消息和使用的令牌数的元组。

**输出示例**：
```python
message = {
    'content': 'This is the generated response.',
    'arguments': {
        'argument1': 'value1',
        'argument2': 'value2'
    },
    'function_call': {
        'name': 'function_name',
        'arguments': {
            'arg1': 'value1',
            'arg2': 'value2'
        }
    }
}
tokens = 100
```
***
