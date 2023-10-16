# XAgent-Server Frontend and Backend Demo

This is a demo of the XAgent-Server frontend and backend. The backend communication is mainly implemented using fastapi's `websocket`, supplemented with essential restful APIs. The frontend service is deployed locally.

## Build the Image

The code for XAgent-Server is located in the `XAgentServer/` directory. Every time the code is modified, the image needs to be rebuilt using the following command:

```bash
bash XAgentServer/dockerfiles/build.sh
```

## Launching XAgent-Server

First, navigate to the demo service folder `XAgentServer/`. Then, to launch the XAgent-Server, execute the following command:

```bash
# XAgentServer/
cd XAgentServer
docker compose up
```
This will start an instance of XAgent-Server listening to port `16204` on the local machine. The configuration details can be found in the `XAgentServer/docker-compose.yml` file.

When you see the following output, it means the image has been successfully compiled and launched:

![XAgent-Server成功示例](https://gitee.com/sailaoda/pic2/raw/master/2023/202309272123424.png)

## Starting the Frontend Service

Navigate to the frontend folder:

```bash
cd XAgentWeb
```

Install Dependencies(Recommend Node.js >= 20.0)

```bash
npm install
```

Run the service:

```bash
npm run dev 
```



## Using XAgent-Server

After completing the above steps, you can access the frontend interface by visiting http://localhost:8000 in a web browser. An example of the interface is shown below:

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

