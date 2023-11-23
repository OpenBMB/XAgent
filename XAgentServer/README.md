# XAgent-Server Frontend and Backend Demo

This is a demo of the XAgent-Server frontend and backend. The backend communication is mainly implemented using fastapi's `websocket`, supplemented with essential restful APIs. The frontend service is deployed locally.

## This project relies on Mysql
```shell
docker pull mysql

docker run -itd --name xagent-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=xagent mysql
```

## This project relies on Redis
```shell
docker pull redis

docker run --name xagent-redis -p 6379:6379 -d redis --requirepass xagent
```

## This project relies on Python3.10+
```shell
pip install -r requirements.txt
```

## Project subject dependence
1. The project uses FastAPI as the WEB framework, Websocket to build a long connection communication service, and Redis as the state management middleware;
2. Use Mysql to store interactive process data and SQLAlchemy as ORM framework
3. The XAgent interface is located at XAgentServer/server.py; Core interactive logic in the XAgentServer/interaction.py


## project directory[Chinese / English]
Only core business modules are listed
>- XAgentServer [XAgent 交互组件 / XAgent Interactive Components]
>   - application [应用 / Application]
>       - core [应用启动核心配置文件 / Configuration File]
>       - cruds [数据库操作集 / CRUDs]
>       - routers [FastAPI 核心路由文件 / FastAPI Routers]
>       - schemas [FastAPI 请求响应结构体 / FastAPI Request & Response Schemas]
>       - websockets [XAgent 前后端数据交互框架 / XAgent Websocket Framework]
>       - dependence.py [FastAPI 依赖注入 / FastAPI Dependencies]
>       - main.py [FastAPI 启动入口 / FastAPI Entrance]
>       - global_val.py [全局变量 / Global Variables]
>   - dockerfiles [Docker 镜像构建文件 / Docker Image Build Files]
>   - database [数据库 / Database]
>   - enums [枚举类型 / Enums]
>   - exts [依赖的拓展 / Extensions]
>   - logggers [日志 / Logs]
>   - models [业务模块定义 / Modules]
>   - interaction.py [核心交互逻辑 / Core Interactive Module]
>   - server.py [交互入口 / Entrance for XAgent]



## Launching XAgent-Server

First, we ran web ui docker when build ToolServer network.

This will start an instance of XAgent-Server listening to port `8090` on the local machine. The configuration details can be found in the `XAgentServer/docker-compose.yml` file.

After completing the image compilation and startup, you need to start the nginx service. Execute the following command on another command line:

```
docker exec XAgent-Server systemctl start nginx
```

When you see the following output, it means the image has been successfully compiled and launched:

![XAgent-Server成功示例](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272123424.png)


## Using XAgent-Server

After completing the above steps, you can access the frontend interface by visiting http://localhost:5173 in a web browser. Default user: Guest, token: xagent, you can use it to login. An example of the interface is shown below:

![login](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272130865.png)

Once you're inside the XAgent-Server, you can start using it as demonstrated:

![playground](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272132478.png)

## Additional Information

If you are running this in a Windows environment, you might encounter an error while building the image, which looks like this: `XAgentServer/dockerfiles/build.sh: line 2: cd: $'XAgentServer/dockerfiles\r': No such file or directory` as shown below:

![windows_build_docker](https://gitee.com/sailaoda/pic2/raw/master/2023/202309280213559.png)

To resolve this, you can navigate to the directory first, then proceed with the compilation. Use the following commands:

```bash
cd XAgentServer/dockerfiles/
bash build.sh
```

