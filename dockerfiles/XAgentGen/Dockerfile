FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

LABEL Role="xagentgen.node"

WORKDIR /app

RUN apt update && apt install -y git ninja-build

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir packaging

RUN MAX_JOBS=8 pip install flash-attn==2.0.4 --no-build-isolation

RUN pip install --no-cache-dir https://github.com/vllm-project/vllm/releases/download/v0.2.2/vllm-0.2.2+cu118-cp310-cp310-manylinux1_x86_64.whl

RUN pip install --no-cache-dir -U xformers --index-url https://download.pytorch.org/whl/cu118

COPY XAgentGen/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir pydantic==1.10.13

RUN rm -rf /tmp/* /var/tmp/*

COPY XAgentGen .