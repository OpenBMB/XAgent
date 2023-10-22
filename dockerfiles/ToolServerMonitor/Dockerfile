FROM python:3.10

LABEL Role="toolserver.monitor"

EXPOSE 8180

WORKDIR /app

COPY ToolServer/ToolServerMonitor/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ToolServer/ToolServerMonitor .

RUN mkdir -p assets

COPY assets/config/monitor.yml ./assets/config.yml

ENTRYPOINT [ "python", "main.py"]