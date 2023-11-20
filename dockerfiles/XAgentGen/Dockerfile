FROM nvidia/cuda:11.6.2-cudnn8-runtime-ubuntu20.04

LABEL Role="xagentgen.node"

# EXPOSE 37264

WORKDIR /app

COPY XAgentGen/requirements_1.txt .

COPY XAgentGen/requirements_2.txt .

RUN apt update && apt install -y python3.10 python3.10-distutils python3-pip

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir -r requirements_1.txt

RUN pip install --no-cache-dir -r requirements_2.txt 

RUN wget https://github.com/vllm-project/vllm/releases/download/v0.2.2/vllm-0.2.2+cu118-cp310-cp310-manylinux1_x86_64.whl

RUN pip uninstall torch -y

RUN pip install --no-cache-dir torch --upgrade --index-url https://download.pytorch.org/whl/cu118

RUN rm -rf /tmp/* /var/tmp/*








