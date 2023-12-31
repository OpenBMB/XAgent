# ClassDef Node
**Node类功能**：Node类是XAgent数据结构中表示通用节点的抽象类。

该类使用abc模块将其标记为抽象基类。其他类应该继承自该类以实现特定类型的节点。

**Node类属性**：
- 无

**Node类方法**：
- \_\_init\_\_(self)：初始化一个新的节点。作为抽象类，Node没有任何具体的实现细节。

**ToolNode类功能**：ToolNode类是XAgent数据结构中表示工具节点的类。

工具节点具有“father”属性，表示其父节点；“children”属性，表示其子节点列表；“data”属性，包含有关节点状态、命令、工具输出和思考属性的元数据；还包括消息历史和工作空间哈希ID。

**ToolNode类属性**：
- father: ToolNode类型，表示父节点。
- children: ToolNode类型的列表，表示子节点列表。
- expand_num: 表示展开次数的整数。
- data: 包含有关节点状态、命令、工具输出和思考属性的字典。
- history: MessageHistory类型，表示消息历史。
- workspace_hash_id: 表示工作空间哈希ID的字符串。

**ToolNode类方法**：
- \_\_init\_\_(self)：初始化一个新的工具节点。为实例设置father、children、expand_num、data、history和workspace_hash_id属性。
- process(self)：生成从当前节点到根节点的数据列表。返回一个包含从当前节点到根节点的数据列表。
- to_json(self)：将实例的data属性转换为JSON兼容格式。返回一个以JSON兼容格式表示的实例的data属性。
- get_depth(self)：计算当前节点在树中的深度。返回节点的深度，如果节点是根节点则返回0。
- get_subtree_size(self)：计算以当前节点为根节点的子树的大小。返回以当前节点为根节点的子树的大小。

**SummarizationNode类功能**：SummarizationNode类用于表示摘要树中的节点。

继承自XAgent.data_structure.node中定义的Node类。

**SummarizationNode类属性**：
- father: SummarizationNode类型，表示父节点。
- children: SummarizationNode类型的列表，表示子节点列表。
- message: Message类型，与该节点关联的消息。
- summarization_from_root_to_here: 从根节点到该节点的摘要。

**SummarizationNode类方法**：
- \_\_init\_\_(self)：初始化一个新的SummarizationNode。设置father、children、message和summarization_from_root_to_here属性。
- add_father_child_relation(cls, father, child)：添加父节点和子节点之间的关系。将子节点添加到父节点的子节点列表中。

**注意**：在使用这些代码时，请注意以下几点：
- Node类是一个抽象类，不能直接实例化。
- ToolNode类表示工具节点，包含了工具节点的属性和方法。
- SummarizationNode类表示摘要树中的节点，包含了摘要节点的属性和方法。
***
# ClassDef ToolNode
**ToolNode类的功能**：ToolNode类是XAgent数据结构中表示工具节点的类。

ToolNode类表示XAgent数据结构中的工具节点。工具节点具有“father”属性，表示其父节点；“children”属性，表示其子节点；“data”属性，包含有关节点状态、命令、工具输出和思考属性的元数据；还包含消息历史和工作空间哈希ID。

ToolNode类具有以下方法：

- `__init__(self)`: 初始化一个新的工具节点。为实例设置father、children、expand_num、data、history和workspace_hash_id属性。
- `process(self)`: 生成从当前节点到根节点的数据列表。返回一个从当前节点到根节点的数据列表。
- `to_json(self)`: 将实例的data属性转换为JSON兼容格式。返回实例的data属性以JSON兼容格式表示的字典。
- `get_depth(self)`: 计算树中当前节点的深度。返回节点的深度。如果节点是根节点，则返回0。
- `get_subtree_size(self)`: 计算以当前节点为根的子树的大小。返回以当前节点为根的子树的大小。

**注意**：ToolNode类是XAgent数据结构中表示工具节点的类。它具有父节点、子节点、数据、历史记录和工作空间哈希ID等属性。它还提供了一些方法来处理节点的数据和计算节点的深度和子树大小。

**示例输出**：
```python
# 创建一个ToolNode实例
node = ToolNode()

# 设置节点的数据属性
node.data = {
    "content": "This is the content",
    "thoughts": {
        "properties": {
            "thought": "This is a thought",
            "reasoning": "This is a reasoning",
            "plan": "This is a plan",
            "criticism": "This is a criticism"
        }
    },
    "command": {
        "properties": {
            "name": "command_name",
            "args": "command_args"
        }
    },
    "tool_output": "This is the tool output",
    "tool_status_code": "TOOL_CALL_SUCCESS"
}

# 获取节点的深度
depth = node.get_depth()
print(depth)  # 输出: 0

# 获取以当前节点为根的子树的大小
subtree_size = node.get_subtree_size()
print(subtree_size)  # 输出: 1

# 将节点的数据属性转换为JSON兼容格式
json_data = node.to_json()
print(json_data)
# 输出: 
# {
#     "content": "This is the content",
#     "thoughts": {
#         "properties": {
#             "thought": "This is a thought",
#             "reasoning": "This is a reasoning",
#             "plan": "This is a plan",
#             "criticism": "This is a criticism"
#         }
#     },
#     "command": {
#         "properties": {
#             "name": "command_name",
#             "args": "command_args"
#         }
#     },
#     "tool_output": "This is the tool output",
#     "tool_status_code": "TOOL_CALL_SUCCESS"
# }
```
## FunctionDef __init__
**__init__函数**：这个函数的作用是初始化一个新的工具节点。

在这个函数中，我们为实例设置了father、children、expand_num、data、history和workspace_hash_id属性。

- father属性表示当前节点的父节点，它的类型是ToolNode。
- children属性表示当前节点的子节点列表，它的类型是ToolNode的列表。
- expand_num属性表示当前节点的展开次数，它的类型是整数。
- data属性是一个字典，包含了节点的内容、思考、命令、工具输出和工具状态码等信息。
  - content字段表示节点的内容，它的类型是字符串。
  - thoughts字段是一个嵌套字典，包含了节点的思考相关属性。
    - thought字段表示节点的思考内容，它的类型是字符串。
    - reasoning字段表示节点的推理内容，它的类型是字符串。
    - plan字段表示节点的计划内容，它的类型是字符串。
    - criticism字段表示节点的批评内容，它的类型是字符串。
  - command字段是一个嵌套字典，包含了节点的命令相关属性。
    - name字段表示节点的命令名称，它的类型是字符串。
    - args字段表示节点的命令参数，它的类型是字符串。
  - tool_output字段表示工具的输出结果，它的类型是字符串。
  - tool_status_code字段表示工具的状态码，它的类型是ToolCallStatusCode枚举值。
- history属性表示节点的消息历史记录，它的类型是MessageHistory的实例。
- workspace_hash_id属性表示节点的工作空间哈希ID，它的类型是字符串。

**注意**：在使用这段代码时需要注意以下几点：
- 需要确保父节点和子节点的类型都是ToolNode。
- expand_num属性的值应该是一个非负整数。
- data属性中的content、thoughts、command、tool_output和tool_status_code字段的值应该符合相应的数据类型要求。
- history属性应该是MessageHistory的实例。
- workspace_hash_id属性应该是一个字符串。
## FunctionDef process
**process函数**：该函数的功能是从当前节点到根节点生成一个数据列表。

该函数通过遍历当前节点的父节点，将每个节点的数据依次添加到列表中，最终返回生成的数据列表。

**注意**：该函数只能在ToolNode对象中调用。

**输出示例**：假设当前节点的数据为[1, 2, 3]，父节点的数据为[4, 5, 6]，根节点的数据为[7, 8, 9]，则调用process函数后返回的数据列表为[7, 8, 9, 4, 5, 6, 1, 2, 3]。
## FunctionDef to_json
**to_json函数**：该函数的功能是将实例的data属性转换为JSON兼容格式。

该函数首先使用深拷贝(deepcopy)创建一个data的副本，然后将副本中的tool_status_code属性的值转换为其对应的枚举名称。最后，将转换后的data返回。

**注意**：使用该函数时需要注意以下几点：
- 该函数只能用于实例对象。
- 转换后的data中的tool_status_code属性值将会被修改为其对应的枚举名称。

**输出示例**：假设实例的data属性为{"tool_status_code": ToolStatusCode.SUCCESS, "data": {"name": "XAgent"}}，经过to_json函数处理后，返回的data属性为{"tool_status_code": "SUCCESS", "data": {"name": "XAgent"}}。
## FunctionDef get_depth
**get_depth函数**：该函数用于计算当前节点在树中的深度。

该函数的作用是计算当前节点在树中的深度。如果节点是根节点，则返回0；否则，递归调用父节点的get_depth函数，并将结果加1作为当前节点的深度。

**注意**：在使用该函数时需要注意以下几点：
- 该函数只能在树的节点对象上调用。
- 确保节点对象的父节点属性正确设置，否则可能导致错误的深度计算结果。

**输出示例**：假设当前节点是树的根节点，则调用get_depth函数的返回值为0。
## FunctionDef get_subtree_size
**get_subtree_size函数**：该函数的功能是计算以当前节点为根的子树的大小。

该函数通过递归的方式计算以当前节点为根的子树的大小。首先判断当前节点是否有子节点，如果没有子节点，则说明当前节点为叶子节点，子树的大小为1。如果有子节点，则遍历每个子节点，并递归调用子节点的get_subtree_size函数，将子节点的大小累加到当前节点的大小中。最后返回当前节点的大小作为子树的大小。

在项目中，该函数被以下文件调用：
文件路径：XAgent/data_structure/node.py
对应代码如下：
```python
def get_subtree_size(self):
    """
    Calculate the size of the subtree rooted at current node.

    Returns:
        size (int): The size of the subtree rooted at current node.
    """
    
    if self.children == []:
        return 1
    now_size = 1
    for child in self.children:
        now_size += child.get_subtree_size()
    return now_size
```
[此处为代码片段结束]
[此处为XAgent/data_structure/node.py结束]
文件路径：XAgent/data_structure/tree.py
对应代码如下：
```python
def get_subtree_size(self):
    """
    Gets the number of nodes (or size) of the subtree from the current root node.

    Returns:
        int: The number of nodes in the subtree
    """
    return self.root.get_subtree_size()
```
[此处为代码片段结束]
[此处为XAgent/data_structure/tree.py结束]

**注意**：在使用该代码时需要注意以下几点：
- 该函数是一个递归函数，需要确保节点之间的关系正确，否则可能导致无限递归。
- 该函数的返回值是以当前节点为根的子树的大小，即子节点的数量。

**输出示例**：模拟代码返回值的可能外观。
```python
size = node.get_subtree_size()
print(size)  # 输出：5
```

通过调用get_subtree_size函数，可以获取以当前节点为根的子树的大小。例如，如果当前节点有5个子节点，则子树的大小为5。
***
