# 🧰 ToolServer

ToolServer为XAgent提供了强大的工具和安全的执行环境，它运行在docker容器中，提供了一个安全隔离的执行环境。

ToolServer由3个部件组成：
- **ToolServerManager** 负责管理ToolServerNode，提供了一系列的API供XAgent调用。
- **ToolServerMonitor** 负责监控ToolServerNode的运行状态，当ToolServerNode出现异常时，ToolServerMonitor将停止删除ToolServerNode。
- **ToolServerNode** 负责提供工具，它运行在docker容器中，提供了一个安全隔离的执行环境。

目前ToolServer支持下列工具：
- **📝 文档编辑器** 提供了一个文档编辑工具，可以用于读写，修改文件。
- **📘 Python Notebook** 提供了一个交互式的python notebook，可以运行python代码，绘制图表。
- **🌏 网页浏览器** 提供了一个网页浏览器用于搜索和访问网页。
- **🖥️ Shell** 提供了一个shell工具用于执行任意shell命令，甚至安装程序和托管服务。
- **🧩 Rapid API** 提供了一个Rapid API工具用于调用Rapid API的API。查看[ToolBench](https://github.com/OpenBMB/ToolBench)以获得更多信息。
你也可以轻松的开发自己的工具并添加到ToolServer中，增强agents的能力。

## ⚡️ 配置ToolServer
ToolServer的配置文件存放在`assets/config/`目录下，你可以修改配置文件并重新启动ToolServer以应用修改。
注意事项：
- 如果你不允许XAgent在`ToolServerNode`中使用docker，请将`manager.yml`中的`node.privileged`设置为`false`。
- 将`monitor.yml`中的`idling_close_minutes`设置为ToolServerMonitor在关闭空闲的ToolServerNode实例前等待的时间（默认30分钟）。
- 在`node.yml`中添加你的api key以启用bing搜索（或使用备用搜索duckduckgo）和rapid api。
- 如果你遇到ToolServer的超时错误，请在`docker-compose.yml`中修改`services.ToolServerManager.command`中`-t`后面的值以修改ToolServer的超时时间。

## 🛠️ 编译和启动ToolServer
你通过下面的命令自动拉取最新的镜像并启动ToolServer：
```bash
docker compose up
```
你也可以通过下面的命令自己编译镜像并启动ToolServer：
```bash
docker compose build
docker compose up
```
请注意，你需要提前安装`docker`和`docker-compose`。

## 🧩 API说明
### /get_cookies
该路径将返回一个cookie，其中包含ToolServerNode实例的node_id。
所有后续的请求都需要使用该cookie来识别ToolServerNode实例。

### /get_available_tools
该路径无需参数传递，返回值为一个json字典列出：
```JSON
{
    "available_envs":[
        {
            "name":"env1",
            "description":"description1",
            "tools":["tool1","tool2"] //最多50条，超过50条的部分不返回
        },
    ],
    "available_tools":[
        "tool1",
        "tool2", //部分tool被隐藏，不会返回
    ],
    "tools_json":[
        {
            "name":"tool1",
            "description":"description1",
            "parameters":{
                "type":"object",
                "properties":{
                    "param1":{
                        "type":"string",
                        "description":"description1"
                    },
                    "param2":{
                        "type":"integer",
                        "description":"description2"
                    }
                },
                "required":["param1","param2"]
            }
        },
    ]
}
```

### /retrieving_tools
给定一个问题，通过doc embedings返回相似度最高top_k个工具。

参数格式：
```JSON
{
    "question":"question1",
    "top_k":10,
}
```
结果格式：
```JSON
{
    "retrieved_tools":[
        "tool1",
        "tool2"
    ],
    "tools_json":[
        {
            "name":"tool1",
            "description":"description1",
            "parameters":{
                "type":"object",
                "properties":{
                    "param1":{
                        "type":"string",
                        "description":"description1"
                    },
                    "param2":{
                        "type":"integer",
                        "description":"description2"
                    }
                },
                "required":["param1","param2"]
            }
        },
    ]
}
```

### /get_json_schema_for_tools
返回指定工具们的json schema。
参数格式：
```JSON
{
    "tool_names":[
        "tool1",
        "tool2"
    ]
}
```
结果格式：
```JSON
{
    "tools_json":[
        {
            "name":"tool1",
            "description":"description1",
            "parameters":{
                "type":"object",
                "properties":{
                    "param1":{
                        "type":"string",
                        "description":"description1"
                    },
                    "param2":{
                        "type":"integer",
                        "description":"description2"
                    }
                },
                "required":["param1","param2"]
            }
        },
    ],
    "missing_tools":[
        "tool3",
        "tool4"
    ]
}
```

### /get_json_schema_for_envs
返回指定环境的json schema。
参数格式：
```JSON
{
    "env_names":[
        "env1",
        "env2"
    ]
}
```
结果格式：
```JSON
{
    "envs_json":[
        {
            "name":"env1",
            "description":"description1",
            "tools":["tool1","tool2"] //全部返回
        },
    ],
    "missing_envs":[
        "env3",
        "env4"
    ]
}
```

### /execute_tool
执行指定工具。
参数格式：
```JSON
{
    "tool_name":"tool1",
    "arguments":{
        "param1":"value1",
        "param2":2
    }
}
```
结果格式由各个工具自己定义。
有一个特殊http状态码450，代表该工具还需后续调用才能完成工作，当返回450错误码时，返回值格式例如下：
```JSON
{
    "detail":{
        "type":"retry",
        "next_calling":"ShellEnv_read_stdout",
        "arguments":{}
    }
}
```



## 释放ToolServerNode
当使用完成后，访问路径`/close_session`，ToolServerManager得到该请求后将停止ToolServerNode docker实例。
也可访问路径`/release_session`，ToolServerManager得到该请求后将删除ToolServerNode docker实例。

