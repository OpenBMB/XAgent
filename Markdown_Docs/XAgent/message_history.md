# ClassDef MessageDict
**MessageDict类的功能**: 该类是一个TypedDict类型的字典，用于跟踪消息的属性。

**属性**:
- role (MessageRole): 消息的来源，可以是'system'、'user'、'assistant'或'function'之一。
- content (str): 消息的内容。
- function_call (dict): 可调用的方法。

**MessageDict.raw()函数**: 该函数用于提取消息的原始内容，去除其他元数据。

**返回值**:
- MessageDict: 包含'role'和'content'的字典。

**代码分析和描述**:
该函数首先创建一个名为data的字典，其中包含了self.role和self.content的值。如果self.function_call不为None，则将其添加到data字典中。最后，将data字典作为函数的返回值。

**注意**: 在使用该代码时需要注意以下几点:
- MessageDict类用于跟踪消息的属性，可以通过role属性获取消息的来源，通过content属性获取消息的内容。
- function_call属性是一个可调用的方法，可以通过调用该方法来执行相应的操作。
- 在调用raw函数时，将返回一个字典，其中包含了消息的角色和内容。如果消息还包含了可调用的方法，则字典中还会包含function_call属性。

以上是对MessageDict类及其相关函数的详细解释和分析。

**注意**: 生成的文档中不包含Markdown的标题和分割线语法。
***
# ClassDef Message
**Message Function**: 这个类的功能是表示来自代理、用户或系统函数的消息。

这个类代表了来自代理、用户或系统函数的消息。

**role (MessageRole)**: 消息的来源，可以是 'system'、'user'、'assistant' 或 'function'。

**content (str)**: 消息的实际内容。

**type (MessageType)**: 消息的类型，可以是 'ai_response'（AI对话消息）或 'action_result'（API调用的结果）。

**function_call (dict)**: 表示可编程API调用中的方法调用的字典。

**raw()**: 提取消息的原始内容，去除其他元数据。

**Returns**:
    MessageDict: 包含 'role' 和 'content' 的字典。

**to_json()**: 将消息转换为JSON格式。

**Returns**:
    MessageDict: 消息的JSON表示。

**equal(cls, a: Message, b: Message)**: 通过比较所有属性来检查两个消息是否相等。

**Args**:
    a (Message): 要比较的第一个消息。
    b (Message): 要比较的第二个消息。

**Returns**:
    bool: 如果两个消息在所有属性上都相等，则返回True；否则返回False。

**注意**: 在使用该代码时需要注意的事项。

**Output Example**: 
```python
{
    "role": "user",
    "content": "Hello, how are you?"
}
```
## FunctionDef raw
**raw函数**：该函数用于提取消息的原始内容，去除其他元数据。

该函数返回一个包含'role'和'content'的字典。

**代码分析和描述**：
该函数接收一个Message对象的实例作为参数，然后将消息的角色和内容提取出来，存储在一个字典中。如果消息中存在函数调用(function_call)，则将其也添加到字典中。最后返回该字典。

该函数的作用是提取消息的原始内容，去除其他元数据，只保留角色和内容信息。这在处理消息历史记录时非常有用，可以方便地获取消息的核心信息。

**注意**：在调用该函数时，需要传入一个Message对象的实例作为参数。

**输出示例**：
```
{
    "role": "user",
    "content": "Hello, how are you?"
}
```
## FunctionDef to_json
**to_json函数**：该函数的功能是将消息转换为JSON格式。

该函数将消息对象转换为JSON格式，并返回表示消息的字典。它首先调用self.raw()函数获取消息的原始内容，然后将其转换为JSON格式。

**注意**：使用该代码时需要注意以下几点：
- 该函数需要在MessageHistory类的实例上调用。

**输出示例**：以下是该函数可能返回值的示例：
```
{
    "id": 1,
    "timestamp": "2022-01-01 12:00:00",
    "sender": "user",
    "content": "Hello",
    "metadata": {}
}
```
## FunctionDef equal
**equal函数**：该函数的功能是比较两个消息对象的所有属性，判断它们是否相等。

该函数接受两个参数a和b，分别表示要比较的两个消息对象。

如果两个消息对象的角色、内容、类型和函数调用都相等，则返回True，否则返回False。

该函数主要用于判断两个消息对象是否相等。

**注意**：在使用该函数时，需要确保传入的参数是Message对象。

**输出示例**：假设a和b是两个消息对象，如果a和b的所有属性都相等，则返回True，否则返回False。
***
# ClassDef ModelInfo
**ModelInfo类的功能**: 这个类用于存储模型信息。

这个类有以下属性：

- name (str): 模型名称
- prompt_token_cost (float): 每个提示的token成本
- completion_token_cost (float): 每个生成结果的token成本
- max_tokens (int): 可以生成的最大token数量

这个类被以下文件调用：

文件路径：XAgent/message_history.py
调用部分代码如下：
class ChatModelInfo(ModelInfo):
    """用于存储聊天模型信息的数据类。"""

[这部分代码的结束]
调用部分代码如下：
class TextModelInfo(ModelInfo):
    """用于存储文本生成模型信息的数据类。"""

[这部分代码的结束]
调用部分代码如下：
class EmbeddingModelInfo(ModelInfo):
    """用于存储嵌入模型信息的数据类。

    属性:
        embedding_dimensions (int): 嵌入模型的维度数量。
    """

    embedding_dimensions: int

[这部分代码的结束]
[End of XAgent/message_history.py]

**注意**: 使用这段代码时需要注意以下几点：

- 需要提供模型的名称、每个提示的token成本、每个生成结果的token成本和最大token数量。
- 对于嵌入模型信息类，还需要提供嵌入模型的维度数量。
***
# ClassDef ChatModelInfo
**ChatModelInfo函数**：该类的功能是存储聊天模型信息的数据类。

ChatModelInfo是一个继承自ModelInfo的类，用于存储聊天模型的相关信息。它是一个数据类，用于存储聊天模型的各种属性和数据。

该类没有定义任何属性或方法，因此它是一个空的数据类。它的主要作用是作为一个容器，用于存储聊天模型的信息，以便在需要时进行访问和使用。

**注意**：该类没有定义任何属性或方法，因此在使用时需要注意，需要在其他地方定义和设置聊天模型的相关属性和数据。
***
# ClassDef TextModelInfo
**TextModelInfo函数**：这个类的功能是存储文本生成模型的信息。

TextModelInfo是一个继承自ModelInfo的数据类，用于存储文本生成模型的信息。它没有定义任何自己的属性或方法，只是继承了父类ModelInfo的属性和方法。

ModelInfo是一个抽象基类，用于定义模型信息的通用接口。它包含了一些常用的属性和方法，如模型名称、模型类型、模型路径等。TextModelInfo作为ModelInfo的子类，可以通过继承来共享这些属性和方法。

使用TextModelInfo类时，可以通过实例化对象来存储文本生成模型的信息。可以通过访问对象的属性来获取模型的名称、类型、路径等信息。这些信息可以用于后续的模型操作和处理。

**注意**：在使用TextModelInfo类时，需要确保传入正确的模型信息，并且按照规定的方式使用对象的属性。
***
# ClassDef EmbeddingModelInfo
**EmbeddingModelInfo函数**：这个类的功能是存储嵌入模型信息的数据类。

这个类继承自ModelInfo类，用于存储嵌入模型的相关信息。它有一个属性embedding_dimensions，表示嵌入模型的维度数。

**注意**：在使用这个类时需要注意以下几点：
- 确保在实例化EmbeddingModelInfo对象时，传入正确的embedding_dimensions参数。
- 可以通过访问embedding_dimensions属性来获取嵌入模型的维度数。
***
# ClassDef MessageHistory
**MessageHistory函数**: 这个类的功能是存储消息历史记录的数据类。

这个类包含了添加、检索和修剪存储的消息的方法。

**属性**:
- messages (list[Message]): 按创建顺序排列的消息列表。
- summary (str): 表示对话/历史记录摘要的字符串。
- last_trimmed_index (int): 最后一个被删除的消息在历史记录中的索引。

**方法**:
- `__getitem__(self, i: int) -> Message`: 通过索引访问消息。
- `__iter__(self) -> iterator`: 返回一个迭代器，用于遍历消息列表。
- `__len__(self) -> int`: 返回消息列表中的消息数量。
- `add(self, role: MessageRole, content: str, type: MessageType | None = None, function_call: str | None = None) -> None`: 向消息列表中添加新消息。
- `append(self, message: Message) -> None`: 将新消息追加到消息列表中。
- `trim_messages(self, current_message_chain: list[Message]) -> tuple[Message, list[Message]]`: 修剪消息列表，返回被修剪的消息列表和新的摘要消息。
- `per_cycle(self, messages: list[Message] | None = None) -> tuple[Message, Message, Message]`: 从对话周期中生成用户、AI和结果消息的迭代器。
- `summary_message(self) -> Message`: 从当前摘要构建摘要消息。
- `update_running_summary(self, new_events: list[Message]) -> Message`: 更新摘要消息，将新事件与当前摘要结合起来。

**注意**: 
- `add`方法中的`role`参数应为'system'、'user'、'assistant'或'function'之一。
- `trim_messages`方法中的`current_message_chain`参数应为当前上下文中的消息列表。
- `per_cycle`方法中的`messages`参数可以是自定义的消息列表，如果为None，则使用`self.messages`。
- `update_running_summary`方法中的`new_events`参数应为新事件的消息列表。

**输出示例**:
```python
history = MessageHistory()
history.add(MessageRole.USER, "Hello!")
history.add(MessageRole.ASSISTANT, "Hi there!")
history.add(MessageRole.USER, "How are you?")
print(len(history))  # Output: 3

for message in history:
    print(message.content)
# Output:
# Hello!
# Hi there!
# How are you?

summary_message = history.summary_message()
print(summary_message.content)
# Output: This reminds you of these events from your past: \nI was created
```
## FunctionDef __getitem__
**__getitem__函数**：这个函数的作用是通过索引访问消息。

该函数接受一个参数i，表示消息在消息列表中的索引。

返回值是消息列表中索引为i的消息。

**注意**：使用该代码时需要注意以下几点：
- 确保索引i在有效范围内，即不超过消息列表的长度。
- 确保消息列表不为空。

**输出示例**：假设消息列表中有三个消息，分别为"Hello", "World", "!"，当调用`__getitem__(1)`时，返回值为"World"。
## FunctionDef __iter__
**__iter__函数**：该函数的功能是返回一个迭代器，用于遍历消息列表。

该函数是一个特殊的函数，用于定义一个对象的迭代行为。在这个函数中，通过调用内置函数iter()，将消息列表self.messages转换为一个迭代器，并返回该迭代器。

**注意**：使用该函数时需要注意以下几点：
- 该函数只能在支持迭代的对象上使用，例如列表、元组、字典等。
- 迭代器是一种能够逐个访问元素的对象，可以通过for循环或next()函数来遍历迭代器中的元素。

**输出示例**：假设messages列表中有3个元素['Hello', 'World', '!']，则调用__iter__函数后返回的迭代器可以按照以下方式遍历：
```python
messages = ['Hello', 'World', '!']
iterator = messages.__iter__()
for message in iterator:
    print(message)
```
输出结果：
```
Hello
World
!
```
## FunctionDef __len__
**__len__函数**：这个函数的作用是返回消息列表中的消息数量。

该函数通过调用内置的len函数来计算消息列表中的消息数量，并将结果返回。

**注意**：使用该代码时需要注意以下几点：
- 该函数只能用于消息历史记录对象。
- 返回值为整数类型。

**输出示例**：假设消息列表中有5条消息，则返回值为5。
## FunctionDef add
**add函数**: 这个函数的作用是将新的消息添加到消息列表中。

该函数接受以下参数：
- role (MessageRole): 消息的来源，可以是'system'、'user'、'assistant'或'function'。
- content (str): 消息的实际内容。
- type (MessageType): 消息的类型，可以是'ai_response'表示AI对话消息或'action_result'表示API调用的结果。如果未指定，默认为None。
- function_call (str): 表示可编程API调用中的方法调用的字典。如果未指定，默认为None。

该函数返回None。

该函数首先根据传入的参数创建一个Message对象，然后将该对象添加到消息列表中。

**注意**: 
- role参数必须是'system'、'user'、'assistant'或'function'中的一个。
- type参数必须是MessageType枚举中的一个值。
- function_call参数是可选的，如果不指定则默认为None。

**输出示例**:
```
add('user', 'Hello, how are you?', MessageType.AI_RESPONSE, 'api_call')
```
## FunctionDef append
**append函数**：这个函数的功能是将一个新的消息添加到消息列表中。

该函数接受一个名为message的参数，表示要添加到列表中的消息。

该函数没有返回值。

**代码分析和描述**：
该函数使用了列表的append方法，将传入的message对象添加到messages列表中。

**注意**：该函数的参数message必须是一个Message对象。

**输出示例**：无返回值。
## FunctionDef trim_messages
**trim_messages函数**：该函数的功能是返回一个修剪过的消息列表，即在消息历史记录中但不在当前消息链中的消息。

该函数接受两个参数：
- current_message_chain（list[Message]）：当前上下文中的消息链。

该函数的返回值为一个元组，包含两个元素：
- Message：一个包含修剪后的消息的消息对象，用于更新运行摘要。
- list[Message]：一个包含在full_message_history中索引大于last_trimmed_index且不在current_message_chain中的消息列表。

函数的具体实现如下：
1. 首先，从full_message_history中选择索引大于last_trimmed_index的消息，存储在new_messages列表中。
2. 然后，从new_messages列表中移除已经存在于current_message_chain中的消息，得到new_messages_not_in_chain列表。
3. 如果new_messages_not_in_chain列表为空，则返回当前的运行摘要消息和一个空的消息列表。
4. 否则，调用update_running_summary函数，将new_messages_not_in_chain作为参数，更新运行摘要消息，并将返回值存储在new_summary_message中。
5. 找到new_messages_not_in_chain列表中最后一条消息的索引，并将其赋值给self.last_trimmed_index。
6. 最后，返回new_summary_message和new_messages_not_in_chain作为函数的返回值。

**注意**：使用该代码时需要注意以下几点：
- current_message_chain参数必须是一个包含Message对象的列表。
- full_message_history必须是一个包含Message对象的列表。
- last_trimmed_index必须是一个整数，表示上一次修剪的消息索引。

**输出示例**：以下是函数返回值的一个示例：
```
new_summary_message = Message("New running summary", "This is the updated summary.")
new_messages_not_in_chain = [
    Message("Message 1", "This is message 1."),
    Message("Message 2", "This is message 2.")
]

返回值：(new_summary_message, new_messages_not_in_chain)
```
## FunctionDef per_cycle
**per_cycle函数**：该函数的功能是从对话周期中生成用户、AI和结果消息。

该函数接受一个名为messages的参数，类型为list[Message]或None，默认值为None。该参数表示当前上下文中的消息列表。如果messages为None，则使用self.messages。

该函数通过遍历messages列表，从中筛选出用户消息、AI消息和结果消息，并以元组的形式返回。

具体实现如下：
1. 首先，将messages赋值为messages参数或self.messages。
2. 然后，通过循环遍历messages列表中的每个元素（索引从0到len(messages)-1）。
3. 对于每个元素，将其赋值给ai_message。
4. 如果ai_message的type不等于"ai_response"，则跳过当前循环，继续下一次循环。
5. 如果ai_message的type等于"ai_response"，则执行以下操作：
   - 如果i大于0且messages[i-1]的role为"user"，则将messages[i-1]赋值给user_message，否则将user_message赋值为None。
   - 将messages[i+1]赋值给result_message。
   - 使用断言语句判断result_message的type是否等于"action_result"，如果不等于则抛出AssertionError异常。
   - 如果断言通过，则使用yield语句返回user_message、ai_message和result_message组成的元组。
   - 如果断言失败，则使用logger.debug()记录错误信息。

**注意**：使用该函数时需要注意以下几点：
- 该函数需要传入一个消息列表作为参数，表示当前上下文中的消息。
- 该函数会根据消息的type属性筛选出用户消息、AI消息和结果消息，并以元组的形式返回。
- 如果消息列表中的某个元素不符合预期的type类型，会抛出AssertionError异常，并记录错误信息。
- 使用yield语句返回结果，可以在循环中逐步获取生成的元组。

以上是对per_cycle函数的详细分析和描述。
## FunctionDef summary_message
**summary_message函数**：此函数的功能是从当前摘要构建摘要消息。

该函数接受当前摘要作为输入，并返回一个包含当前摘要的系统消息。

**代码分析和描述**：
该函数接受当前摘要作为输入，并使用字符串插值将其包含在系统消息中返回。系统消息的内容是一个字符串，其中包含当前摘要的文本。

**注意事项**：
- 该函数依赖于Message类和summary属性。
- 调用该函数前，需要确保已经设置了当前摘要。

**输出示例**：
```
Message(
    "system",
    "This reminds you of these events from your past: \n{self.summary}",
)
```
## FunctionDef update_running_summary
**update_running_summary函数**：该函数的功能是将一组表示新事件的字典列表与当前摘要结合起来，重点关注关键信息和可能重要的信息以供记忆。函数将返回一个以第一人称过去时格式化的消息，其中包含更新后的摘要。

**参数**：
- new_events（List[Dict]）：包含要添加到摘要中的最新事件的字典列表。

**返回值**：
- str：包含更新后的操作摘要的消息，以第一人称过去时格式化。

**示例**：
```python
new_events = [{"event": "进入了厨房。"}, {"event": "找到了一张写着数字7的便条。"}]
update_running_summary(new_events)
# 返回："这让我想起了过去发生的这些事件：\n我进入了厨房并找到了一张写着数字7的便条。"
```

**update_running_summary函数详细分析**：
该函数接受一个表示新事件的字典列表new_events，并将其与当前摘要结合起来，生成更新后的摘要。函数的具体步骤如下：

1. 创建一个Config对象cfg，用于获取配置信息。
2. 如果new_events为空列表，则直接返回当前摘要的消息，即调用self.summary_message()函数。
3. 创建new_events的副本，以防止修改原始列表。
4. 遍历new_events列表，将其中的"assistant"替换为"you"，以便生成更好的第一人称过去时结果。同时，删除"content"中的"thoughts"字典，以保持摘要的简洁性。
5. 如果遇到"system"角色的事件，将其角色替换为"your computer"。
6. 删除所有用户消息，即将角色为"user"的事件从new_events列表中删除。
7. 构建一个prompt字符串，用于向模型提供输入。该字符串包含了当前摘要和最新事件的信息。
8. 调用ChatSequence.for_model方法，使用cfg.fast_llm_model模型生成一个ChatSequence对象prompt。
9. 将prompt的原始内容记录到日志中，以便后续分析。
10. 调用create_chat_completion函数，使用生成的prompt生成更新后的摘要。
11. 将更新后的摘要记录到日志中。
12. 返回更新后的摘要的消息，即调用self.summary_message()函数。

**注意**：
- 在处理new_events时，会修改原始列表，因此在函数内部创建了new_events的副本进行操作，以防止对原始列表的修改。
- 函数内部使用了Config对象cfg，用于获取配置信息。
- 函数内部调用了self.summary_message()函数，用于返回当前摘要的消息。

**输出示例**：
这让我想起了过去发生的这些事件：
我进入了厨房并找到了一张写着数字7的便条。
***
