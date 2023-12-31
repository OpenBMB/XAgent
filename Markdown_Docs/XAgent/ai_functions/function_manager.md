# ClassDef FunctionManager
**FunctionManager函数**: 这个类提供了管理函数的方法，包括函数的注册和执行。函数是从本地目录下的子目录'functions'和'pure_functions'中的YAML配置文件中定义和加载的。

**function_cfg_dir (str)属性**: 存储函数配置文件所在的目录路径。

**pure_function_cfg_dir (str)属性**: 存储纯函数配置文件所在的目录路径。

**function_cfgs (dict)属性**: 用于存储所有加载的函数配置。

**__init__方法**: 使用给定的函数配置文件目录路径初始化FunctionManager类。

参数:
- function_cfg_dir (str): 函数配置文件所在的目录路径。
- pure_function_cfg_dir (str): 纯函数配置文件所在的目录路径。

**get_function_schema方法**: 根据函数名称获取函数的模式。

参数:
- function_name (str): 函数的名称。

返回值:
- dict: 如果找到函数，则返回函数的模式。
- None: 如果未找到函数，则返回None。

**register_function方法**: 注册一个新的函数及其模式。

参数:
- function_schema (dict): 要注册的函数的模式。

**execute方法**: 根据函数名称执行一个函数。

参数:
- function_name (str): 要执行的函数的名称。
- return_generation_usage (bool, optional): 如果设置为True，则还返回函数执行的用法。
- function_cfg (dict, optional): 函数的配置。如果未提供，则从加载的函数中检索。
- **kwargs: 要执行的函数的参数。

返回值:
- Tuple[dict,Optional[dict]]: 包含执行结果和可选的函数执行用法的元组。

抛出异常:
- KeyError: 如果未找到函数配置。

**__getitem__方法**: 允许FunctionManager实例像字典一样使用，通过键（实际上是函数名称）调用execute方法。

参数:
- function_name (str): 要执行的函数的名称。
- return_generation_usage (bool, optional): 如果设置为True，则还返回函数执行的用法。
- **kwargs: 要执行的函数的参数。

返回值:
- execute方法的返回值。

**__call__方法**: 允许FunctionManager实例可调用，直接调用execute方法。

参数:
- function_name (str): 要执行的函数的名称。
- return_generation_usage (bool, optional): 如果设置为True，则还返回函数执行的用法。
- **kwargs: 要执行的函数的参数。

返回值:
- execute方法的返回值。

**注意**: 使用该类时需要注意以下几点:
- 需要在实例化FunctionManager类时提供函数配置文件的目录路径。
- 可以通过get_function_schema方法获取函数的模式。
- 可以通过register_function方法注册新的函数。
- 可以通过execute方法执行函数。
- 可以通过__getitem__方法和__call__方法以字典或可调用对象的方式执行函数。

**输出示例**:
```
{
  "name": "add",
  "parameters": [
    {
      "name": "a",
      "type": "int"
    },
    {
      "name": "b",
      "type": "int"
    }
  ],
  "return_type": "int"
}
```
## FunctionDef __init__
**__init__函数**: 这个函数的作用是初始化FunctionManager类，并设置函数配置文件的目录。

详细代码分析和描述:
- function_cfg_dir参数是函数配置文件所在的目录路径，默认为当前文件所在目录下的functions文件夹。
- pure_function_cfg_dir参数是纯函数配置文件所在的目录路径，默认为当前文件所在目录下的pure_functions文件夹。
- function_cfgs是一个字典，用于存储函数配置文件的内容。

函数的执行流程如下：
1. 遍历function_cfg_dir目录下的所有.yaml和.yml文件。
2. 对于每个配置文件，使用yaml.load函数加载配置文件的内容，并将其存储在function_cfg变量中。
3. 将function_cfg中的函数名作为键，将整个function_cfg作为值，存储在function_cfgs字典中。
4. 遍历pure_function_cfg_dir目录下的所有.yaml和.yml文件。
5. 对于每个配置文件，使用yaml.load函数加载配置文件的内容，并将其存储在function_cfg变量中。
6. 遍历function_cfg中的每个函数，将函数名作为键，将整个函数配置作为值，存储在function_cfgs字典中。

**注意**: 使用该代码时需要注意以下几点：
- 需要确保function_cfg_dir和pure_function_cfg_dir参数指定的目录存在，并且目录下包含正确的函数配置文件。
- 函数配置文件的格式必须为.yaml或.yml格式。
- 函数配置文件中的函数名必须唯一，否则会覆盖之前同名的函数配置。

以上是对该代码部分的详细解释和描述。
## FunctionDef get_function_schema
**get_function_schema函数**：该函数用于根据函数名称获取函数的模式。

该函数接受一个字符串类型的参数function_name，表示函数的名称。函数会根据给定的名称在函数配置中查找对应的函数模式。

如果找到了对应的函数模式，则返回该函数的模式字典；如果未找到对应的函数模式，则返回None。

该函数的作用是根据函数名称获取函数的模式，以便后续使用。

**代码分析和描述**：
该函数首先接受一个字符串类型的参数function_name，表示函数的名称。然后，函数调用function_cfgs的get方法，传入function_name作为参数，从函数配置中获取对应的函数模式。如果找到了对应的函数模式，则返回该函数的模式字典；如果未找到对应的函数模式，则返回None。

**注意**：在使用该函数时，需要确保传入的函数名称在函数配置中存在。

**输出示例**：
如果找到了对应的函数模式，则返回该函数的模式字典，例如：
{
    "name": "function_name",
    "parameters": {
        "param1": {
            "type": "string",
            "description": "Parameter 1"
        },
        "param2": {
            "type": "int",
            "description": "Parameter 2"
        }
    }
}

如果未找到对应的函数模式，则返回None。
## FunctionDef register_function
**register_function函数**：该函数用于注册一个新的函数及其模式。

该函数接受一个名为function_schema的字典作为参数，该字典包含要注册的函数的模式信息。

如果function_schema中的'name'字段已经存在于self.function_cfgs中，则函数将直接返回，不进行注册操作。

如果function_schema中的'name'字段不存在于self.function_cfgs中，则将该函数的模式信息添加到self.function_cfgs中。

**注意**：在使用该函数时需要注意以下几点：
- function_schema参数必须是一个字典，且必须包含'name'字段。
- 如果要注册的函数已经存在于self.function_cfgs中，则不会进行重复注册。

**输出示例**：模拟该函数返回值的可能外观。

```python
{
    "name": "function_name",
    "description": "function_description",
    ...
}
```
## FunctionDef execute
**execute函数**：这个函数的功能是执行一个指定名称的函数。

该函数接受以下参数：
- function_name (str)：要执行的函数的名称。
- return_generation_usage (bool, 可选)：如果设置为True，还会返回函数执行的用法。
- function_cfg (dict, 可选)：函数的配置。如果未提供，则从加载的函数中获取。
- **kwargs：要执行的函数的参数。

该函数返回一个元组，包含执行函数的返回值和可选的函数执行用法。

如果找不到函数配置，会引发KeyError异常。

在函数内部，首先会检查是否提供了函数配置。如果未提供且函数名称在函数配置中存在，则从函数配置中获取函数配置。否则，会引发KeyError异常，提示找不到函数配置。

接下来，会记录日志，打印出正在执行的AI函数的名称。

然后，根据函数配置中的completions_kwargs参数，判断使用的是哪种请求类型。如果是'openai'，则调用objgenerator.chatcompletion函数，传入相应的参数，执行函数。如果是'xagent'，则根据函数配置中的参数arguments，调用objgenerator.chatcompletion函数，传入相应的参数，执行函数。

最后，根据return_generation_usage参数的值，决定是否返回函数执行的返回值和使用情况。

**注意**：使用该代码时需要注意以下几点：
- 需要提供正确的函数名称和参数。
- 需要确保函数配置已经加载。
- 如果找不到函数配置，会引发KeyError异常。

**输出示例**：模拟代码返回值的可能外观。
```python
{
    'result': {
        'output': 'Hello, World!',
        'status': 'success'
    },
    'usage': {
        'duration': 2.5,
        'memory': 256
    }
}
```
## FunctionDef __getitem__
**__getitem__函数**：这个函数的作用是允许FunctionManager实例像字典一样使用，通过键（实际上是函数名）调用execute方法。

该函数有以下参数：
- function_name（str）：要执行的函数的名称。
- return_generation_usage（bool，可选）：如果设置为True，则还返回函数执行的用法。
- **kwargs：要执行的函数的参数。

该函数返回execute方法的返回值。

**代码分析和描述**：
__getitem__函数是FunctionManager类的一个方法，用于实现实例像字典一样使用。它接受一个函数名作为参数，并可选择返回函数执行的用法。在执行过程中，它会调用execute方法来执行相应的函数。

该函数的参数包括function_name、return_generation_usage和**kwargs。function_name是要执行的函数的名称，return_generation_usage是一个布尔值，用于指定是否返回函数执行的用法，**kwargs是要执行的函数的参数。

在函数体内部，它调用了execute方法，并将function_name、return_generation_usage和**kwargs作为参数传递给execute方法。然后，它返回execute方法的返回值。

**注意**：使用该代码时需要注意以下几点：
- 该函数需要一个有效的函数名作为参数。
- 可以选择返回函数执行的用法。

**输出示例**：模拟代码返回值的可能外观。
```python
# 示例1：
result = function_manager_instance['function_name']
print(result)
# 输出：
# 函数执行的返回值

# 示例2：
result, usage = function_manager_instance['function_name', True, param1='value1', param2='value2']
print(result)
print(usage)
# 输出：
# 函数执行的返回值
# 函数执行的用法
```
## FunctionDef __call__
**__call__函数**：这个函数的作用是允许FunctionManager实例可调用，直接调用execute方法。

该函数接受以下参数：
- function_name（str）：要执行的函数的名称。
- return_generation_usage（bool，可选）：如果设置为True，则还返回函数执行的用法。
- **kwargs：要执行的函数的参数。

返回值：execute方法的返回值。

**详细分析和描述**：
__call__函数是FunctionManager类的一个特殊方法，它允许我们直接调用FunctionManager实例，而不需要显式地调用execute方法。通过调用__call__函数，我们可以直接执行指定名称的函数，并将参数传递给该函数。

在函数体内部，__call__函数调用了execute方法，并将传入的参数传递给execute方法。execute方法是FunctionManager类的另一个方法，用于执行具体的函数逻辑。通过调用execute方法，我们可以执行指定名称的函数，并获取其返回值。

如果设置了return_generation_usage参数为True，__call__函数还会返回函数执行的用法。这对于了解函数的使用方式非常有帮助。

**注意**：使用该代码时需要注意以下几点：
- 需要确保传入的function_name参数是一个已定义的函数名称。
- 如果需要获取函数执行的用法，需要将return_generation_usage参数设置为True。

**输出示例**：假设我们调用了__call__函数，并传入了参数function_name='my_function'和return_generation_usage=True，那么函数的返回值可能是：
```
{
  'result': '函数执行的结果',
  'usage': '函数的使用方式'
}
```
***
