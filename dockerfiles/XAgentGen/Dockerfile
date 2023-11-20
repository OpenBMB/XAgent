FROM nvidia/cuda:11.6.2-cudnn8-runtime-ubuntu20.04

LABEL Role="xagentgen.node"

# EXPOSE 37264

WORKDIR /app

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY XAgentGen/requirements_1.txt .

COPY XAgentGen/requirements_2.txt .

RUN pip install --no-cache-dir -r requirements_1.txt

RUN pip install --no-cache-dir -r requirements_2.txt 

RUN rm -rf /tmp/* /var/tmp/*








