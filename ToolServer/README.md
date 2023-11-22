# 🧰 ToolServer

ToolServer is the server provide XAgent with powerful and safe tools to solve tasks. It is a docker container that provides a safe environment for XAgent to run.

ToolServer is composed of three parts:
- **ToolServerManager** is responsible for creating and managing ToolServerNode instances.
- **ToolServerMonitor** is responsible for monitoring the status of ToolServerNode instances. Automatic detect instances status and removing the instances that are not working properly.
- **ToolServerNode** is responsible for providing tools to solve tasks. It is a docker container that provides a safe environment for XAgent to run.

Currently, ToolServer provides the following tools:
- **📝 File Editor** provide a text editing tool that can write, read, and modify files.
- **📘 Python Notebook** provide a interactive python notebook that can run python code to validate ideas, draw figures, etc.
- **🌏 Web Browser** provide a web browser that can search and visit webpages.
- **🖥️ Shell** provide a bash shell tool that can execute any shell commands, even install programs and host services.
- **🧩 Rapid API** provide a tool to retrieve apis from Rapid API and calling them, which provides a wide range of apis for XAgent to use. See [ToolBench](https://github.com/OpenBMB/ToolBench) to get more information about the Rapid API collections.
You can also easily add new tools to ToolServer to enhance agent's abilities.

## ⚡️ Configurations
Configurations for ToolServer are stored in `assets/config/`. You can change them and restart ToolServer to apply the changes.
Notes:
- Change `node.privileged` to `false` in `manager.yml` if you don't want to used docker in ToolServerNode. This will disable the ability to run docker commands in ToolServerNode.
- Change `idling_close_minutes` in `monitor.yml` to change the time that ToolServerMonitor will wait before closing idle ToolServerNode instances.
- Add your api keys in `node.yml` to enable bing search (or use backup search duckduckgo) and rapid api.
- Change api timeout for Toolserver in `docker-compose.yml` by altering values after `-t` in `services.ToolServerManager.command` if you encounter timeout error of ToolServer.

## 🛠️ Build and Setup ToolServer
You can pull the docker images from docker hub and start ToolServer automatically with following command:
```bash
docker compose up
```
Alternatively, you can build the images by yourself and start ToolServer with following command:
```bash
docker compose build
docker compose up
```
Note that you should install `docker` and `docker-compose` first.

## 🧩 API Documentation
### /get_cookies
This path will return a cookie that contains the node_id of the ToolServerNode instance.
All the following requests should use this cookie to identify the ToolServerNode instance.

### /get_available_tools
This path will return all registered tools in ToolServerNode, together with their parameters.
```JSON
{
    "available_envs":[
        {
            "name":"env1",
            "description":"description1",
            "tools":["tool1","tool2"] //at most 50 tools, the rest will not be returned
        },
    ],
    "available_tools":[
        "tool1",
        "tool2", //hidden tools will not be returned
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
Giving a question, return related tools. Rapid API will also be returned.
Arguments:
```JSON
{
    "question":"question",
    "top_k":10
}
```
Return:
```JSON
{
    "retrieved_tools":[
        "tool1",
        "tool2"
    ],
    "tools_json":[
        {
            //tool1 json
        },
        {
            //tool2 json
        }
    ]
}
```

### /get_json_schema_for_tools
Return the json schema for the given tools.
Arguments:
```JSON
{
    "tools":["tool1","tool2"]
}
```
Return:
```JSON
{
    "tools_json":[
        {
            //tool1 json
        },
        {
            //tool2 json
        }
    ],
    "missing_tools":[

    ]
}
```

### /get_json_schema_for_envs
Return the json schema for the given envs.
Arguments:
```JSON
{
    "envs":["env1","env2"]
}
```
Return:
```JSON
{
    "envs_json":[
        {
            "name":"env1",
            "description":"description1",
            "tools":["tool1","tool2"]
        }
    ],
    "missing_envs":[

    ]
}
```

### /execute_tool
Execute the given tool with the given parameters.
Arguments:
```JSON
{
    "tool":"tool1",
    "parameters":{
        "param1":"value1",
        "param2":"value2"
    }
}
```
Return is dependent on the tool.
The return http code 450 standfor need further calling to finish tool execution.
When return http code 450, the return value will be like:
```JSON
{
    "detail":{
        "type":"retry",
        "next_calling":"ShellEnv_read_stdout",
        "arguments":{}
    }
}
```

### /close_session
Close the ToolServerNode instance.

### /release_session
Close and delete ToolServerNode instance.