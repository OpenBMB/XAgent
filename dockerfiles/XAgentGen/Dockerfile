FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

LABEL Role="xagentgen.node"

# EXPOSE 37264

WORKDIR /app

COPY XAgentGen/requirements_1.txt .

COPY XAgentGen/requirements_2.txt .

RUN apt update && apt install -y git ninja-build

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install packaging

RUN MAX_JOBS=8 pip install flash-attn==2.0.4 --no-build-isolation

RUN pip install --no-cache-dir -r requirements_1.txt

RUN pip install --no-cache-dir -r requirements_2.txt 


RUN rm -rf /tmp/* /var/tmp/*








