# Introduction of XAgentGen

XAgentGen implements the guided generation of the customized model to support the XAgent.

# 1. Setup for XAgentGen

running:
```shell
pip install -r requirements_1.txt
pip install -r requirements_2.txt
```
**note:** download the specified version of `Pydantic` and `Outlines`, you may fix the conflicts manually.

# 2. Start the inference service
Running example:(specified the model directory and port)
```shell
python app.py --model-path /user/model/path --port 8000
```
**note:** like the command above, the model service will be on `127.0.0.1:8000`, and the `api_base` in the config should be `http://127.0.0.1:8000/chat/completions`

# 3. Use the XAgent with the customized model

Runnning the command at root dir:
```shell
python run.py --task "find all the prime numbers <=100" --model "xagentllm" --config-file "assets/agentllama.yml"
```



