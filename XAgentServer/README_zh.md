# XAgent-Server 前后端 Demo

XAgent-Server 前后端 Demo，后端通信部分主要由fastapi的`websocket`实现，辅以必要的restful接口；前端服务进行本地部署。

## 编译镜像

XAgent-Server的代码在`XAgentServer/`路径下，每次修改代码后，需要重新编译镜像，执行如下命令：

```bash
cd XAgentServer
docker-compose build
```

## 启动 XAgent-Server

首先需要进入demo服务文件夹`XAgentServer/`下，之后启动 XAgent-Server，执行如下命令：

```bash
# XAgentServer/
cd XAgentServer
docker-compose up
```
这将启动一个XAgent-Server实例，监听本机`8090`端口，配置信息在`XAgentServer/docker-compose.yml`文件中。

完成镜像编译和启动后还需启动nginx服务，在另一个命令行执行如下命令：

```
docker exec XAgent-Server systemctl start nginx
```

出现如下输出，就是镜像编译与启动成功了：

![XAgent-Server成功示例](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272123424.png)


## 使用 XAgent-Server
完成上述操作后，浏览器访问 http://localhost:5173 即可进入前端界面，示例如下 (可以默认用户名: admin, token: xagent-admin 进行登录)：

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

