# XAgent-Server 前后端 Demo

XAgent-Server 前后端 Demo，后端通信部分主要由fastapi的`websocket`实现，辅以必要的restful接口；前端服务进行本地部署。

## 本项目依赖Mysql
```shell
docker pull mysql

docker run -itd --name xagent-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=xagent mysql
```

## 本项目依赖Redis
```shell
docker pull redis

docker run --name xagent-redis -p 6379:6379 -d redis --requirepass xagent
```

## 本项目依赖Python3.10+
```shell
pip install -r requirements.txt
```

## 项目主体依赖
1. 本项目使用FastAPI 作为WEB框架, 使用Websocket 构建长链接通信服务,使用Redis作为状态管理中间件;
2. 使用Mysql 存储交互过程数据, 使用SQLAlchemy 作为ORM框架
3. XAgent 交互入口位于/XAgentServer/server.py; 核心交互逻辑位于XAgentServer/interaction.py;


## 项目目录[中文 / English]
仅列出核心业务模块
>- XAgent [XAgent 核心业务组件 / XAgent Core Components]
>   - 待补充
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
>- XAgentWeb


## 启动 XAgent-Server

我们已经开启了web ui的docker镜像，在之前 build ToolServer 网络的时候。

这将启动一个XAgent-Server实例，监听本机`8090`端口，配置信息在`XAgentServer/docker-compose.yml`文件中。

完成镜像编译和启动后还需启动nginx服务，在另一个命令行执行如下命令：

```
docker exec XAgent-Server systemctl start nginx
```

出现如下输出，就是镜像编译与启动成功了：

![XAgent-Server成功示例](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272123424.png)


## 使用 XAgent-Server
完成上述操作后，浏览器访问 http://localhost:5173 即可进入前端界面，示例如下 (可以默认用户名: Guest, token: xagent 进行登录)：

![login](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272130865.png)

进入 XAgent-Server 后即可开始使用，如下所示：

![playground](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272132478.png)

## 其他

如果您是在windows环境中运行，在编译镜像时可能会出现`XAgentServer/dockerfiles/build.sh: line 2: cd: $'XAgentServer/dockerfiles\r': No such file or directory`的报错情况，如下所示：

![windows_build_docker](https://gitee.com/sailaoda/pic2/raw/master/2023/202309280213559.png)

您可以先进入路径目录，在进行编译，即可解决，执行命令如下：

```bash
cd XAgentServer/dockerfiles/
bash build.sh
```

