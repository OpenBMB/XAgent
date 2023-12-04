# 📖 Introduction of XAgentGen

XAgentGen implements the guided generation of the customized model to support the XAgent.
XAgentGen allows models to generate function calls with the given complex [json schema](https://json-schema.org/understanding-json-schema) just like openai's function calling.

Currently, XAgentGen supports the following models:
- [XAgentLlama](https://huggingface.co/collections/XAgentTeam/xagentllm-655ae4091c419bb072940e74): the official model of XAgent, which is based on Code-Llama. **Note: the model is still under training, and the preview version is available now.**


# 🛠️ 1. Setup for XAgentGen
After you download the models, you can host a interference service for the model by following the instructions below.
## Install Cuda Container Toolkit
XAgentGen requires the [Cuda Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker) to run.
You should follow the guide to install the Cuda Container Toolkit before running the XAgentGen.

## Pull or Build the XAgentGen image
You can either pull the pre-built docker image or build the docker image by yourself.
We do recommend you to pull the pre-built docker image, which is more convenient.

### Pull the pre-built docker image
```shell
docker pull xagentteam/xagentgen:latest
```

### Build the docker image by yourself
Make sure you are at the root dir of the project, and run the following command:
```shell
docker build -f dockerfiles/XAgentGen/Dockerfile -t xagentteam/xagentgen . 
```
Note that the building process may take a long time and the default setting requires at least 64GB memory to build.
You can low down the memory requirement by changing the `MAX_JOBS` in the dockerfile.


## Run the docker image
Start the docker image by:
```shell
docker run -it -p 13520:13520 --network tool-server-network -v /host/model/path:/model:rw --gpus all --ipc=host xagentteam/xagentgen:latest python app.py --model-path /model --port 13520
```
**Note:** Change the `/host/model/path` to the path of your model directory. The service should be listening on port `13520`.


# 🎮 2. Use the XAgent with the customized model

You should change the config file to use the customized model. The sample config file is in `assets/xagentllama.yml`.
Run XAgent with customized model by: 
```shell
python run.py --task "find all the prime numbers <=100" --config-file "assets/xagentllama.yml"
```

