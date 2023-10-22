# 🧰 ToolServer

ToolServer is the server that provides XAgent with powerful and safe tools to solve tasks. It is a Docker container that provides a safe environment for XAgent to run.

ToolServer is composed of three parts:
- **ToolServerManager** is responsible for creating and managing ToolServerNode instances.
- **ToolServerMonitor** is responsible for monitoring the status of ToolServerNode instances. Automatic detection of instance status and removing instances that are not working properly.
- **ToolServerNode** is responsible for providing tools to solve tasks. It is a Docker container that provides a safe environment for XAgent to run.

Currently, ToolServer provides the following tools:
- **📝 File Editor** provide a text editing tool that can write, read, and modify files.
- **📘 Python Notebook** provides an interactive Python notebook that can run Python code to validate ideas, draw figures, etc.
- **🌏 Web Browser** provides a web browser that can search and visit webpages.
- **🖥️ Shell** provides a bash shell tool that can execute any shell commands, even install programs and host services.
- **🧩 Rapid API** provides a tool to retrieve APIs from Rapid API and calling them, which provides a wide range of APIs for XAgent to use. See [ToolBench](https://github.com/OpenBMB/ToolBench) to get more information about the Rapid API collections.
You can also easily add new tools to ToolServer to enhance agent's abilities.

## ⚡️ Configurations
Configurations for ToolServer are stored in `ToolServer/config/`. You can change them and rebuild images to apply the changes.
Notes:
- Change `node.privileged` to `false` in `manager.yml` if you don't want to use Docker in ToolServerNode. This will disable the ability to run Docker commands in ToolServerNode.
- Change `idling_close_minutes` in `monitor.yml` to change the time that ToolServerMonitor will wait before closing idle ToolServerNode instances.
- Add your API keys in `node.yml` to enable Bing search (or use backup search DuckDuckGo) and rapid API.
- Change the API timeout for Toolserver in `docker-compose.yml` by altering the values after `-t` in `services.ToolServerManager.command` if you encounter a timeout error of ToolServer.

## 🛠️ Build and Setup ToolServer
All Docker image build files are stored in `ToolServer/dockerfiles`.
You can build them manually with the following command:
```bash
cd ToolServer
docker-compose build
```
This will build all the Docker images for ToolServerManager, ToolServerMonitor and ToolServerNode.

After building the Docker images, you can start the Docker container with following command:
```bash
cd ToolServer
docker-compose up
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
            "tools":["tool1","tool2"] //at most 50 tools, the rest will not be returned.
        },
    ],
    "available_tools":[
        "tool1",
        "tool2", //hidden tools will not be returned.
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
Return the JSON schema for the given tools.
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
Return the JSON schema for the given environments/envs.
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
The return http code 450 stands for need further calling to finish tool execution.
When returning the http code 450, the return value will be like:
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
Close and delete the ToolServerNode instance.
