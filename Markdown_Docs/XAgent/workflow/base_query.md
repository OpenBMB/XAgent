# ClassDef BaseQuery
**BaseQuery函数**: 这个类的功能是定义了一个查询对象的基类。任何其他在XAgent中使用的查询类都应该继承这个基类。

这个类有以下属性：
- role_name (str): 查询涉及的角色名称。
- task (str): 正在查询的任务。
- plan (list): 查询的计划详情列表。

这个类有以下方法：
- `__init__(self, role_name="", task="", plan=[])`: 构造函数，用于初始化BaseQuery对象的属性。
- `log_self(self)`: 抽象方法，用于记录查询的详细信息。所有继承自BaseQuery的类都应该实现这个方法。
- `to_json(self)`: 将BaseQuery对象序列化为JSON对象。
- `from_json(cls, json_data)`: 从JSON对象构造一个新的BaseQuery对象。

**注意**: 
- BaseQuery是一个抽象基类，不能直接实例化。
- `log_self`方法是一个抽象方法，需要在子类中实现具体的逻辑。

**输出示例**:
```python
query = BaseQuery(role_name="user", task="search", plan=["step1", "step2"])
print(query.to_json())
# 输出: {'task': 'search', 'role_name': 'user', 'plan': ['step1', 'step2']}

json_data = {'task': 'search', 'role_name': 'user', 'plan': ['step1', 'step2']}
query = BaseQuery.from_json(json_data)
print(query.role_name)
# 输出: 'user'
```
## FunctionDef to_json
**to_json函数**：该函数的功能是将BaseQuery对象序列化为JSON对象。

该函数将BaseQuery对象的属性转化为一个字典对象，并返回该字典对象。

**注意**：无

**输出示例**：
```
{
    "task": "task_name",
    "role_name": "role_name",
    "plan": "plan_name"
}
```

该函数在项目中的调用情况如下：

文件路径：XAgent/recorder.py

代码片段：
```python
def regist_query(self, query):
    """记录query的相关信息
    """
    record = self.generate_record(
        current=self.now_subtask_id,
        node_id=0,
        node_type=RecorderTypeEnum.QUERY,
        data=query.to_json(),
    )
    with get_db() as db:
        RunningRecordCRUD.insert_record(db=db, record=record)
```

该函数在regist_query函数中被调用，用于将query对象转化为JSON对象，并将其作为记录的一部分存储到数据库中。
## FunctionDef from_json
**from_json函数**：该函数的作用是根据JSON对象构建一个新的BaseQuery对象。

该函数接受两个参数：
- json_data（dict类型）：用于构建BaseQuery对象的JSON对象。

该函数返回一个BaseQuery对象，该对象是根据`json_data`中的值构建而成的。

该函数在以下文件中被调用：
文件路径：XAgent/recorder.py
对应代码如下：
```python
def get_query(self):
    """从数据库中获取查询"""
    with get_db() as db:
        records = RunningRecordCRUD.get_record_by_type(
            db=db,
            record_id=self.record_id,
            node_id=0,
            node_type=RecorderTypeEnum.QUERY,
        )

    self.query = AutoGPTQuery.from_json(records[0].data)
    return self.query
```
[代码片段结束]
对应代码如下：
```python
def load_from_db(self, record_id):
    """从本地文件夹加载record，用于后面的直接复现
    """

    self.newly_start = False

    with get_db() as db:
        records = RunningRecordCRUD.get_record_by_type(
            db=db,
            record_id=record_id
        )

    for record in records:
        if record.node_type == RecorderTypeEnum.QUERY:
            self.query = AutoGPTQuery.from_json(record.data)
        elif record.node_type == RecorderTypeEnum.CONFIG:
            self.config = XAgentConfig()
            self.config.merge_from_dict(record.data)
        elif record.node_type == RecorderTypeEnum.LLM_INPUT_PAIR:
            self.llm_server_cache.append(record.data)
        elif record.node_type == RecorderTypeEnum.TOOL_SERVER_PAIR:
            self.tool_server_cache.append(record.data)
        elif record.node_type == RecorderTypeEnum.PLAN_REFINE:
            self.plan_refine_cache.append(record.data)
        elif record.node_type == RecorderTypeEnum.TOOL_CALL:
            self.tool_call_cache.append(record.data)
        else:
            raise NotImplementedError
```
[代码片段结束]
[文件结束]
文件路径：XAgent/running_recorder.py
对应代码如下：
```python
def load_from_disk(self, record_dir):
    """
    从磁盘中加载record。

    参数：
        - record_dir（str类型）：record的目录。

    """
    logger.typewriter_log(
        "从磁盘中加载record，覆盖所有现有的配置信息",
        Fore.BLUE,
        record_dir,
    )
    self.regist_father_info(record_dir)
    self.newly_start = False

    for dir_name in os.listdir(record_dir):
        if dir_name == "query.json":
            with open(os.path.join(record_dir, dir_name), "r",encoding="utf-8") as reader:
                self.query_json = json.load(reader)
                self.query = AutoGPTQuery.from_json(self.query_json)
        elif dir_name == "config.yml":
            CONFIG.reload(os.path.join(record_dir, dir_name))
        elif dir_name == "LLM_inout_pair":
            inout_count = len(os.listdir(os.path.join(record_dir, dir_name)))
            self.llm_server_cache = [None]*inout_count
            for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                inout_id = int(file_name.split(".")[0])
                with open(os.path.join(record_dir, dir_name, file_name), "r",encoding="utf-8") as reader:
                    llm_pair = json.load(reader)
                    self.llm_server_cache[inout_id] = llm_pair
            logger.typewriter_log(
                f"记录包含{inout_count}个LLM输入输出",
                Fore.BLUE,
            )
        elif dir_name == "tool_server_pair":
            inout_count = len(os.listdir(os.path.join(record_dir, dir_name)))
            self.tool_server_cache = [None]*inout_count
            for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                inout_id = int(file_name.split(".")[0])
                with open(os.path.join(record_dir, dir_name, file_name), "r",encoding="utf-8") as reader:
                    tool_pair = json.load(reader)
                    self.tool_server_cache[inout_id] = tool_pair
            logger.typewriter_log(
                f"记录包含{len(os.listdir(os.path.join(record_dir, dir_name)))}个工具调用",
                Fore.BLUE,
            )
        elif os.path.isdir(os.path.join(record_dir, dir_name)):
            for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                if file_name.startswith("plan_refine"):
                    with open(os.path.join(record_dir, dir_name, file_name),encoding="utf-8") as reader:
                        plan_refine = json.load(reader)
                        self.plan_refine_cache.append(plan_refine)
                elif file_name.startswith("tool"):
                    with open(os.path.join(record_dir, dir_name, file_name),encoding="utf-8") as reader:
                        tool_call = json.load(reader)
                        self.tool_call_cache.append(tool_call)
                else:
                    raise NotImplementedError
```
[代码片段结束]
[文件结束]

**注意**：使用该代码时需要注意以下几点：
- `json_data`参数必须是一个字典类型的JSON对象。
- `json_data`中的键必须与`BaseQuery`类的属性名相对应，否则会引发错误。

**输出示例**：模拟代码返回值的可能外观。
```python
{
    "key1": "value1",
    "key2": "value2",
    ...
}
```
***
# ClassDef AutoGPTQuery
**AutoGPTQuery函数**：这个类的功能是用于特定的GPT模型操作，它继承自BaseQuery类。

构造函数`__init__(self, **args)`：通过继承BaseQuery类，构造AutoGPTQuery对象的所有必要属性。

参数：
- `**args`：可变长度的参数列表，是一个属性键值对的字典。

log_self函数：使用logger记录AutoGPTQuery的详细信息。

该方法记录"Role"和"Task"，分别使用role_name和task作为参数。
如果计划中有任何细节，它还会记录"Plan"以及计划中的每个细节。

注意：使用代码中的logger记录AutoGPTQuery的详细信息。

**注意**：关于代码使用的注意事项：
- AutoGPTQuery是一个特定类型的查询，用于特定的GPT模型操作。
- 构造函数`__init__`继承自BaseQuery类，用于构造AutoGPTQuery对象的属性。
- log_self函数使用logger记录AutoGPTQuery的详细信息，包括"Role"、"Task"和计划中的细节。
## FunctionDef __init__
**__init__函数**：这个函数的功能是通过从BaseQuery类继承来构建AutoGPTQuery对象的所有必要属性。

这个函数接受一个可变长度的参数列表**args，它是一个包含属性键值对的字典。

在函数内部，通过调用父类的__init__函数来初始化对象的属性。

**注意**：使用这段代码时需要注意以下几点：
- 这个函数是一个构造函数，用于初始化对象的属性。
- 参数**args是一个字典，可以包含任意数量的属性键值对。
- 调用父类的__init__函数来初始化对象的属性。
## FunctionDef log_self
**log_self函数**: 这个函数的功能是使用logger记录AutoGPTQuery的详细信息。

这个函数会使用logger记录"Role"和"Task"，并分别使用role_name和task作为参数。如果计划中有任何细节，它还会记录"Plan"以及计划中的每个细节。

这个函数被以下文件调用：
文件路径：XAgent/workflow/base_query.py
对应的代码如下：
```python
class BaseQuery(metaclass = abc.ABCMeta):
    """
    Base class for Query object. This class should be inherited by any other query class that will be used in the XAgent.

    Attributes:
        role_name (str): Name of the role involved in the query.
        task (str): Task that is being queried.
        plan (list): List of the plan details for the query.
    """

    def __init__(self, role_name="", task="", plan=[]):
        """
        Constructs all the necessary attributes for the BaseQuery object.

        Args:
            role_name (str, optional): Name of the role involved in the query.
            task (str, optional): Task that is being queried.
            plan (list, optional): List of the plan details for the query.
        """
        self.role_name = role_name
        self.task = task
        self.plan = plan

    @abc.abstractmethod
    def log_self(self):
        """
        Abstract method to log Query details. 
        This method should be implemented by all classes that inherit from BaseQuery.
        """
        pass

    def to_json(self):
        """
        Serializes the BaseQuery object into a JSON object.

        Returns:
            dict: A dictionary version of the BaseQuery object.
        """
        return {
            "task": self.task,
            "role_name": self.role_name,
            "plan": self.plan,
        }

    @classmethod
    def from_json(cls, json_data):
        """
        Construct a new BaseQuery object from a JSON object.

        Args:
            json_data (dict): The JSON object that will be used to construct the BaseQuery.

        Returns:
            BaseQuery: A new BaseQuery object constructed from the values in `json_data`.
        """
        return cls(**json_data)
```
[代码段结束]
[结束于 XAgent/workflow/base_query.py]
文件路径：XAgent/workflow/task_handler.py
对应的代码如下：
```python
    def outer_loop(self):
        """
        Executes the main sequence of tasks in the outer loop.

        Raises:
            AssertionError: Raised if a not expected status is encountered while handling the plan.

        Returns:
            None
        """
        self.logger.typewriter_log(
            f"-=-=-=-=-=-=-= BEGIN QUERY SOVLING -=-=-=-=-=-=-=",
            Fore.YELLOW,
            "",
        )
        self.query.log_self()

        self.plan_agent.initial_plan_generation(
            agent_dispatcher=self.agent_dispatcher)

        print(summarize_plan(self.plan_agent.latest_plan.to_json()))

        print_data = self.plan_agent.latest_plan.to_json()
        self.interaction.insert_data(data={
            "task_id": print_data.get("task_id", ""),
            "name": print_data.get("name", ""),
            "goal": print_data.get("goal", ""),
            "handler": print_data.get("handler", ""),
            "tool_budget": print_data.get("tool_budget", ""),
            "subtasks": [{**sub, "inner": []} for sub in print_data.get("subtask", [])]
        }, status=StatusEnum.START, current=print_data.get("task_id", ""))

        self.plan_agent.plan_iterate_based_on_memory_system()

        def rewrite_input_func(old, new):
            if new is None or not isinstance(new, dict):
                return old, False
            else:
                goal = new.get("goal", "")
                if goal != "":
                    old = goal
                return old, True

        self.now_dealing_task = self.plan_agent.latest_plan.children[0]
        # workspace_hash_id = ""
        while self.now_dealing_task:
            task_id = self.now_dealing_task.get_subtask_id(to_str=True)
            self.recorder.change_now_task(task_id)
            if self.interaction.interrupt:
                goal = self.now_dealing_task.data.goal
                receive_data = self.interaction.receive(
                    {"args": {"goal": goal}})
                new_intput, flag = rewrite_input_func(
                    self.now_dealing_task, receive_data)

                if flag:
                    self.logger.typewriter_log(
                        "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                        Fore.GREEN,
                        "",
                    )
                    self.logger
***
