# ClassDef SummarizationNode
**SummarizationNode函数**: 这个类的功能是表示摘要树中的节点。

这个类继承自XAgent.data_structure.node中定义的Node类。

**属性**:
- father (SummarizationNode): 父节点。
- children (List[SummarizationNode]): 子节点列表。
- message (Message): 与该节点相关联的消息。
- summarization_from_root_to_here: 从根节点到该节点的摘要。

**方法**:
- `__init__(self)`: 构造函数，初始化节点的属性。
- `add_father_child_relation(cls, father, child)`: 添加父节点和子节点之间的关系。
- `add_father_child_relation(cls, father, child)`: 添加父节点和子节点之间的关系。

**注意**: 
- `add_father_child_relation`方法会检查子节点是否已经存在于父节点的子节点列表中，如果存在则会抛出`AssertionError`异常。
- `SummarizationNode`类的实例可以通过`add_father_child_relation`方法来建立父子节点之间的关系。

该对象在以下文件中被调用：
- XAgent/summarization_system.py中的SummarizationTrieTree类的`query`方法和`insert`方法中使用了SummarizationNode类的实例。
- XAgent/summarization_system.py中的SummarizationTrieTree类的`generate_summary`方法中使用了SummarizationNode类的实例。

**SummarizationTrieTree函数**: 这个类表示摘要Trie树，用于生成摘要。

**属性**:
- root (SummarizationNode): 树的根节点。
- config: 树的配置数据。

**方法**:
- `__init__(self, config)`: 构造函数，初始化树的属性。
- `query(self, message_list: List[Message]) -> SummarizationTreeQueryResult`: 使用给定的消息列表查询树。
- `insert(self, message_list)`: 将消息列表插入到树中。
- `get_summarzation_message_all(cls, father_summarize_node: SummarizationNode, message_list: List[Message]) -> List[Message]`: 获取所有摘要消息。
- `get_summarzation_message_recursive(cls, father_summarize_node: SummarizationNode, new_message: Message)`: 递归获取摘要消息。
- `generate_summary(self, message_list, recursive_mode=True, agent_dispatcher=None)`: 为给定的消息列表生成摘要。

**注意**: 
- `query`方法用于查询树中是否存在给定的消息列表，返回查询结果和查询结束的节点。
- `insert`方法用于将消息列表插入到树中，并返回插入后的节点。
- `get_summarzation_message_all`方法用于获取所有摘要消息。
- `get_summarzation_message_recursive`方法用于递归获取摘要消息。
- `generate_summary`方法用于生成给定消息列表的摘要。

该对象在以下文件中被调用：
- XAgent/summarization_system.py中的SummarizationTrieTree类的`generate_summary`方法中使用了SummarizationNode类的实例。
## FunctionDef add_father_child_relation
**add_father_child_relation函数**：此函数的功能是将父节点和子节点之间建立关系。

该函数用于在父节点和子节点之间建立关系。父节点和子节点都是SummarizationNode类型的对象。在建立关系之前，会先检查子节点是否已经存在于父节点的子节点列表中，如果存在则会抛出AssertionError异常。建立关系后，会将子节点添加到父节点的子节点列表中，并将子节点的父节点属性设置为父节点。

**注意**：如果子节点已经存在于父节点的子节点列表中，则会抛出AssertionError异常。
***
# ClassDef SummarizationTreeQueryResult
**SummarizationTreeQueryResult函数**：这个类的功能是枚举查询摘要树时可能的结果。

这个类定义了以下枚举值：
- have_summary：表示查询的消息列表在摘要树中有摘要。
- not_in_tree：表示查询的消息列表不在摘要树中。
- in_tree_but_no_summary：表示查询的消息列表在摘要树中，但没有摘要。

在项目中，这个类被以下文件调用：
- 文件路径：XAgent/summarization_system.py
- 调用代码：
    def query(self, message_list: List[Message]) -> SummarizationTreeQueryResult:
        """使用给定的消息列表查询树。

        参数:
            message_list (List[Message]): 用于查询树的消息列表。

        返回:
            SummarizationTreeQueryResult: 与查询相关的摘要状态。
            SummarizationNode: 如果消息列表在树中，则返回搜索结束的节点。
        """
        # 查询树的代码

    def generate_summary(self, message_list, recursive_mode=True, agent_dispatcher=None):
        """为给定的消息列表生成摘要。

        参数:
            message_list (List[Message]): 要进行摘要的消息列表。
            recursive_mode (bool): 是否需要递归模式摘要。
            
        返回:
            str: 新生成的摘要内容文本。
        """
        # 生成摘要的代码

**注意**：在使用这个类时需要注意以下几点：
- 可以使用`query`函数查询给定消息列表在摘要树中的状态和节点。
- 可以使用`generate_summary`函数为给定消息列表生成摘要。可以选择是否使用递归模式进行摘要。
***
# ClassDef SummarizationTrieTree
**SummarizationTrieTree函数**: 这个类的函数是用来表示摘要Trie树的。该树用于生成摘要。

该类具有以下属性：
- root (SummarizationNode): 树的根节点。
- config: 树的配置数据。

**__init__函数**:
- 参数: config (配置数据)
- 功能: 初始化SummarizationTrieTree对象。
- 返回值: 无

**query函数**:
- 参数: message_list (消息列表)
- 功能: 使用给定的消息列表查询树。
- 返回值: 
  - SummarizationTreeQueryResult: 与查询相关的摘要状态。
  - SummarizationNode: 如果消息列表在树中，则返回搜索结束的节点。

**insert函数**:
- 参数: message_list (消息列表)
- 功能: 将消息列表插入到Trie树中。
- 返回值: 插入后的最后一个节点。

**get_summarzation_message_all函数**:
- 参数: father_summarize_node (父节点), message_list (消息列表)
- 功能: 获取所有摘要消息。
- 返回值: 摘要消息列表。

**get_summarzation_message_recursive函数**:
- 参数: father_summarize_node (父节点), new_message (新消息)
- 功能: 递归获取摘要消息。
- 返回值: 摘要消息列表。

**generate_summary函数**:
- 参数: message_list (消息列表), recursive_mode (递归模式), agent_dispatcher (代理调度器)
- 功能: 为给定的消息列表生成摘要。
- 返回值: 新的摘要内容文本。

**注意**: 使用代码的注意事项。

**输出示例**:
```
新的摘要内容文本
```
## FunctionDef __init__
**__init__函数**：这个函数的功能是初始化一个SummarizationSystem对象。

在这个函数中，我们可以看到有一个参数config，它是用来传递配置信息的。在函数体内部，我们可以看到有两个属性的初始化操作，分别是self.root和self.config。

self.root是一个SummarizationNode对象，它是整个摘要系统的根节点。通过这个根节点，我们可以访问到整个摘要系统的各个节点和功能。

self.config是一个配置对象，用来存储和管理摘要系统的配置信息。通过这个对象，我们可以对摘要系统进行配置和设置。

**注意**：在使用这个函数时，需要传入一个有效的配置对象作为参数。配置对象中应包含摘要系统的相关配置信息。
## FunctionDef query
**query函数**：该函数用于查询给定消息列表在树中的状态。

该函数接受一个消息列表作为参数，并返回一个包含两个元素的元组。第一个元素表示查询的结果状态，第二个元素表示查询结束时所在的节点。

在函数内部，首先将当前节点设置为根节点，然后通过循环遍历消息列表中的每个消息。对于每个消息，遍历当前节点的子节点，如果找到与当前消息相等的子节点，则将当前节点更新为该子节点，并将循环指针后移一位。

如果找到了与当前消息相等的子节点，则继续下一个消息的查询。如果未找到与当前消息相等的子节点，则返回查询结果为"not_in_tree"，并将当前节点作为查询结束时所在的节点。

最后，根据查询结束时所在的节点的状态，返回相应的查询结果和节点。

**注意**：在使用该函数时，需要将消息列表作为参数传入，并根据返回的查询结果进行相应的处理。

**输出示例**：假设查询结果为"have_summary"，查询结束时所在的节点为节点A。


## FunctionDef insert
**insert函数**：这个函数的功能是将一组消息插入到trie树中。

该函数接受一个消息列表作为参数，将这些消息插入到树中，并返回插入后的最后一个节点。

在插入过程中，函数会遍历消息列表，并在树中查找每个消息对应的节点。如果找到了对应的节点，则将当前节点更新为找到的子节点，并继续遍历下一个消息。如果没有找到对应的节点，则停止遍历。

在遍历完消息列表后，函数会创建新的节点，并将其与当前节点建立父子关系。然后将当前节点更新为新创建的节点，并继续遍历剩余的消息列表。

最后，函数返回插入后的最后一个节点。

**注意**：使用该函数时需要注意以下几点：
- 插入的消息列表应该是按照顺序排列的，即从根节点到叶子节点的路径。
- 插入的消息列表中的每个消息应该是唯一的，不能重复。
- 插入的消息列表中的每个消息应该是有效的，不能为None或空字符串。

该函数在以下文件中被调用：
- 文件路径：XAgent/summarization_system.py
- 调用代码：
    ```
    summarize_node = self.insert(message_list)
    ```
## FunctionDef get_summarzation_message_all
**get_summarzation_message_all函数**: 该函数的功能是将提供的文本中的行动和信息结果创建为简明扼要的运行摘要，重点关注关键和可能重要的信息以供记忆。

该函数接受两个参数：father_summarize_node（SummarizationNode类型）和message_list（List[Message]类型），并返回一个List[Message]类型的结果。

函数内部首先构建了一个系统提示(system_prompt)字符串，该字符串包含了当前摘要和最新行动的关键信息。然后将该系统提示作为一条消息添加到message_list中。

最后，函数返回更新后的message_list。

**注意**: 使用该函数时需要注意以下几点：
- father_summarize_node参数是一个SummarizationNode类型的对象，表示父节点的摘要信息。
- message_list参数是一个List[Message]类型的对象，表示消息列表。
- 返回值是一个List[Message]类型的对象，表示更新后的消息列表。

**输出示例**:
```
[
    Message(sender='system', content='Your task is to create a concise running summary of actions and information results in the provided text, focusing on key and potentially important information to remember.\n\nYou will receive the current summary and the your latest actions. Combine them, adding relevant key information from the latest development in 1st person past tense and keeping the summary concise.\n\nLatest Development:\n"""\n[message.content for message in message_list] or "Nothing new happened."\n"""\n')
]
```
## FunctionDef get_summarzation_message_recursive
**get_summarzation_message_recursive函数**：该函数的功能是生成一个包含系统提示和最新开发的消息列表。

该函数接受两个参数：father_summarize_node（SummarizationNode类型）和new_message（Message类型）。father_summarize_node表示当前的摘要节点，new_message表示最新的消息。

函数首先根据father_summarize_node和new_message生成系统提示，系统提示包括当前的摘要和最新的开发。然后将系统提示封装成Message对象，并将其添加到message_list中。

最后，函数返回message_list作为结果。

**注意**：该函数依赖于SummarizationNode和Message两个类。

**输出示例**：
```
[
    Message(
        sender="system",
        content="Your task is to create a concise running summary of actions and information results in the provided text, focusing on key and potentially important information to remember.\n\nYou will receive the current summary and the your latest actions. Combine them, adding relevant key information from the latest development in 1st person past tense and keeping the summary concise.\n\nSummary So Far:\n\"\"\"\n{father_summarize_node.summarization_from_root_to_here}\n\"\"\"\n\nLatest Development:\n\"\"\"\n{[message.content for message in new_message] or "Nothing new happened."}\n\"\"\"\n"
    )
]
```
## FunctionDef generate_summary
**generate_summary函数**：该函数的功能是为给定的消息列表生成摘要。

该函数接受以下参数：
- message_list（List[Message]）：要进行摘要的消息列表。
- recursive_mode（bool）：指示是否需要递归模式摘要的标志。

该函数返回一个字符串，表示新生成的摘要内容文本。

该函数的详细分析和描述如下：
该函数首先通过调用query函数来查询消息列表的摘要节点。如果查询结果的状态码为SummarizationTreeQueryResult.have_summary，则断言失败。
如果递归模式为True，则再次调用query函数查询消息列表去掉最后一条消息的结果。如果查询结果的状态码为SummarizationTreeQueryResult.have_summary，则断言成功。
然后，通过调用get_summarzation_message_recursive函数或get_summarzation_message_all函数来获取摘要消息列表。
如果递归模式为False，并且查询结果的状态码为SummarizationTreeQueryResult.not_in_tree，则调用insert函数将消息列表插入到摘要树中。
最后，通过调用agent_dispatcher的dispatch函数来获取与摘要相关的agent，并调用agent的parse函数来解析摘要内容。
将解析结果中的新摘要赋值给summarize_node的summarization_from_root_to_here属性，并返回新摘要。

**注意**：关于代码使用的注意事项

**输出示例**：模拟代码返回值的可能外观。
***
