# Introduction of XAgentGen

XAgentGen implement the guided generation of customized model so as to support the xagent.

# 1. Setup for XAgentGen

running:
```shell
pip install -r requirements_xgen.txt
```
**note:** download the specified version of `pydantic` and `outlines`, you may fix the conflicts manually.

# 2. Start the inference service

runnning example:(specified the model directory and port)
```shell
python app.py --model-path /user/model/path --port 8000
```
**note:** like the command above, the model service will be on `127.0.0.1:8000`,and the `api_base` in config should be `http://127.0.0.1:8000/chat/completions`

# 3. Start the xagent

runnning the command at root dir:
```shell
python run.py --task "find all the prime numbers <=100" --model "xagentllm" --config-file "assets/agentllama.yml"
```



