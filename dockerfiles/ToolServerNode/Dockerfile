FROM python:3.10

LABEL Role="toolserver.node"

EXPOSE 31942

WORKDIR /app

RUN apt-get update

RUN apt update && apt install -y build-essential make openjdk-17-jdk-headless curl docker.io docker-compose psmisc sudo

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install playwright && playwright install chromium &&  playwright install-deps

COPY ToolServer/ToolServerNode/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
 
RUN rm -rf /tmp/* /var/tmp/*

COPY ToolServer/ToolServerNode .

RUN mkdir -p assets

RUN mkdir -p workspace

ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0","--port","31942" ]
