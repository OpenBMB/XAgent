# Setup for xgen

running:
```shell
pip install -r requirements_xgen.txt
```
**note:** download the specified version of `pydantic` and `outlines`, you may fix the conflicts manually.

# Start the inference service

runnning example:(specified the model directory and port)
```shell
python app.py --model-path /user/model/path --port 8000
```
**note:** like the command above, the model service will be on `127.0.0.1:8000`,and the `api_base` in config should be `http://127.0.0.1:8000/chat/completions`




