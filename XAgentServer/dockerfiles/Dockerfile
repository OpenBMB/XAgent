

FROM python:3.10


EXPOSE 8090


RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple


WORKDIR /app


COPY ./XAgentServer/requirements.txt requirements.txt


RUN pip install --no-cache-dir -r requirements.txt


COPY . .

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT [ "python", "start_server.py" ]