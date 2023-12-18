# X-Agent 

A large-scale agent-based model by Tsinghua University NLP lab.

## Requirements  环境要求

- Node.js >= 16.0.0
- npm >= 9.0.0

## Install Dependencies  安装依赖

```bash
npm install
```



## Run  运行

```bash
npm run dev 
```

# 关于后台地址的修改
# Guidance on modifying the backend address


+ 可能遇到的错误
    
    Possible errors
    
  1. 
      ```
      WebSocket connection to 'ws://localhost:8090/ws
      ```
  2. 对话卡在Outer Loop中
      
      The conversation is stuck in the Outer Loop

+ 如果您在遇到Websocket连接失败的情况，可以尝试修改后台地址，修改后台地址的方法如下：
  
  If you encounter a Websocket connection failure, you can try to modify the background address. The method of modifying the background address is as follows:


    1. 编辑.env.development或者.env.test文件，将VITE_BACKEND_URL的值修改为后台地址，例如：
    
        Edit the .env.development file and modify the value of VITE_BACKEND_URL to the backend address, for example:
        
        ```
        VITE_BACKEND_URL=http://your-IP:8090
        ```
