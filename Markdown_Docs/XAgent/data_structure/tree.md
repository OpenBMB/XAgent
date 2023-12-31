# ClassDef TaskSearchTree
**TaskSearchTree函数**: TaskSearchTree类的功能是表示具有特定任务搜索行为的树数据结构。

TaskSearchTree类具有以下属性：
- root (ToolNode): 树的根节点。
- now_expand_num (int): 在遍历过程中维护节点的当前扩展编号。

TaskSearchTree类具有以下方法：

1. \_\_init\_\_()
   - 描述：使用根节点和默认扩展编号初始化TaskSearchTree对象。
   - 参数：无
   - 返回值：无
   - 异常：无

2. get_depth()
   - 描述：获取从当前根节点到树的深度。
   - 参数：无
   - 返回值：int类型，树的深度
   - 异常：无

3. get_subtree_size()
   - 描述：获取从当前根节点开始的子树的节点数（或大小）。
   - 参数：无
   - 返回值：int类型，子树中的节点数
   - 异常：无

4. make_father_relation(father, child)
   - 描述：在两个给定节点之间建立父子关系。
   - 参数：
     - father (ToolNode): 父节点。
     - child (ToolNode): 子节点。
   - 返回值：无
   - 异常：
     - TypeError: 如果father或child不是ToolNode实例。

**注意**：
- 父节点和子节点都需要是ToolNode的实例。

**示例输出**：
```python
tree = TaskSearchTree()
depth = tree.get_depth()
subtree_size = tree.get_subtree_size()
father = ToolNode()
child = ToolNode()
tree.make_father_relation(father, child)
```
## FunctionDef __init__
**__init__函数**：该函数的功能是初始化TaskSearchTree对象，包括创建一个根节点ToolNode和设置默认的扩展数量。

在代码中，我们可以看到__init__函数没有任何参数，它是TaskSearchTree类的构造函数。在函数内部，首先创建了一个根节点ToolNode，并将其赋值给self.root。然后，将根节点的扩展数量设置为0，表示根节点不会被扩展。接着，将当前的扩展数量设置为1，表示当前已经扩展了一个节点。

这个函数的作用是在创建TaskSearchTree对象时，初始化根节点和扩展数量的相关属性。

**注意**：在使用该代码时需要注意以下几点：
- 该函数没有参数，直接调用即可。
- 初始化的根节点默认不会被扩展，如果需要扩展根节点，可以通过修改expand_num属性来实现。
- 当前的扩展数量表示已经扩展的节点数量，可以根据需要进行修改。
## FunctionDef get_depth
**get_depth函数**：该函数的功能是获取当前根节点的树的深度。

该函数通过调用根节点的get_depth方法来获取树的深度。

**注意**：使用该代码时需要注意以下几点：
- 该函数需要在Tree对象上调用。
- 该函数返回一个整数，表示树的深度。

**输出示例**：假设树的深度为3，则函数返回值为3。
## FunctionDef get_subtree_size
**get_subtree_size函数**：该函数的功能是获取当前根节点的子树中的节点数（或大小）。

该函数通过调用根节点的get_subtree_size方法来获取子树的节点数。

**注意**：使用该代码时需要注意以下几点：
- 该函数只能在已经创建了根节点的情况下调用，否则会抛出异常。
- 子树的节点数不包括根节点本身。

**输出示例**：假设当前根节点的子树中有5个节点，则函数返回值为5。
## FunctionDef make_father_relation
**make_father_relation函数**：该函数的功能是在两个给定的节点之间建立父子关系。

该函数接受两个参数：
- father（ToolNode类型）：关系中的父节点。
- child（ToolNode类型）：关系中的子节点。

如果father或child不是ToolNode的实例，则会引发TypeError异常。

在函数内部，首先通过判断father和child是否为ToolNode的实例，如果不是，则抛出TypeError异常，提示father和child都需要是ToolNode的实例。

然后，将child的expand_num属性设置为当前的expand_num值，并将expand_num值加1，用于标识节点的扩展顺序。

接下来，将child的father属性设置为father节点，并将child添加到father的children列表中。

**注意**：使用该代码需要注意以下几点：
- father和child参数必须是ToolNode的实例。
- 使用该函数时，需要确保father和child节点已经创建，并且已经在树中存在。
***
