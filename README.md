<div align= "center">
    <h1> <img src="https://www.x-agent.net/assets/main-logo-6-5-2e7e4694.png" height=35 align="texttop">XAgent</h1>
</div>

<div align="center">


[![Twitter](https://img.shields.io/twitter/follow/XAgent?style=social)](https://twitter.com/XAgentTeam) [![Discord](https://img.shields.io/badge/XAgent-Discord-purple?style=flat)](https://discord.gg/zncs5aQkWZ) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/license/apache-2-0/) ![Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)




</div>

<p align="center">
  <a href="#Quickstart">Tutorial</a> •
  <a href="#Demo">Demo</a> •
  <a href="#Blog">Blog</a> •
  <a href="#Citation">Citation</a>


</p>

</div>


# 📖 Introduction
XAgent is an open-source experimental Large Language Model (LLM) driven autonomous agent that can automatically solve various tasks. 
It is designed to be a general-purpose agent that can be applied to a wide range of tasks. Currently, XAgent is still in its early stage, and we are working hard to improve it.

🏆 Our goal is to create a super-intelligent agent that can solve any given task!

## <img src="https://www.x-agent.net/assets/main-logo-6-5-2e7e4694.png" height=25 align="texttop"> XAgent
XAgent is designed with the following features:
- **Autonomy**: XAgent can automatically solve various tasks without human participation.
- **Safety**: XAgent is designed to run safely. All actions are constrained inside a docker container. Run it anyway!
- **Extensibility**: XAgent is designed to be extensible. You can easily add new tools to enhance agent's abilities and even new agents！
- **GUI**: XAgent provides a friendly GUI for users to interact with the agent. You can also use the command line interface to interact with the agent.
- **Cooperation with Human**: XAgent can collaborate with you to tackle tasks. It not only has the capability to follow your guidance in solving complex tasks on the go but also can seek your assistance when it encounters challenges.

XAgent is composed of three parts:
- **🤖 Dispatcher** is responsible for dynamically instantiating and dispatching tasks to different agents. It allows us to add new agents and improve the agents' abilities.
- **🧐 Planner** is responsible for generating and rectifying plans for tasks. It divides a task into subtasks and generates milestones for them, allowing agents to solve tasks step by step.
- **🦾 Actor** is responsible for conducting actions to achieve goals and finish subtasks. The actor utilizes various tools to solve subtasks, and it can also collaborate with human to solve tasks.

## 🧰 ToolServer
ToolServer is the server that provides XAgent with powerful and safe tools to solve tasks. It is a docker container that provides a safe environment for XAgent to run.
Currently, ToolServer provides the following tools:
- **📝 File Editor** provides a text editing tool that can write, read, and modify files.
- **📘 Python Notebook** provides an interactive Python notebook that can run Python code to validate ideas, draw figures, etc.
- **🌏 Web Browser** provides a web browser that can search and visit webpages.
- **🖥️ Shell** provides a bash shell tool that can execute any shell commands, even install programs and host services.
- **🧩 Rapid API** provides a tool to retrieve APIs from Rapid API and call them, which provides a wide range of APIs for XAgent to use. See [ToolBench](https://github.com/OpenBMB/ToolBench) to get more information about the Rapid API collections.
You can also easily add new tools to ToolServer to enhance XAgent's abilities.

<div><a id="Quickstart"></a></div>

# ✨ Quickstart
## 🛠️ Build and Setup ToolServer
ToolServer is where XAgent's action takes place. It is a docker container that provides a safe environment for XAgent to run.
So you should install `docker` and `docker-compose` first. 
After that, you should build the docker image for ToolServer and start the docker container.
```bash
cd ToolServer
bash build_all.sh && docker-compose up
```
Refer [here](ToolServer/README.md) for detailed information about our ToolServer.

## 🎮 Setup and Run XAgent
After setting up ToolServer, you can start to run XAgent.
- Install requirements (Require Python >= 3.10)
```bash
pip install -r requirements.txt
```

- Configure XAgent
You should configure XAgent in `config.yml` before running it. 
At least one OpenAI key is provided in `config.yml`, which is used to access OpenAI API.
We highly recommend using `gpt-4-32k` to run XAgent, `gpt-4` is also OK for most simple tasks.
In any case, at least one `gpt-3.5-turbo-16k` API key should be provided as a backup model.
We do not test or recommend using `gpt-3.5-turbo` to run XAgent due to very limited context length, you should not try to run XAgent on that.

- Run XAgent
```bash
python run.py --task "put your task here" --model "gpt-4"
```
The local workspace for your XAgent is in `local_workspace`, where you can find all the files generated by XAgent throughout the running process. Besides, in `running_records` you can find all the intermediate steps information, e.g. task statuses, LLM's input-output pairs, used tools, etc.

- Run XAgent with GUI
```bash
bash XAgentServer/dockerfiles/build.sh
cd XAgentServer
docker compose up

cd ../XAgentWeb
npm install
npm run serve
```
Build the docker image for XAgent-Server and start the docker container.
You will see the XAgent Server listening on port `8000`.
Refer [here](XAgentServer/README.md) for the detailed information about our GUI Demo.

<div><a id="Demo"></a></div>

# 🎬 Demo
You can check our live demo on [XAgent Official Website](https://www.x-agent.net/).

We also provide a video demo of using XAgent here.

<div align="center">

<video width="320" height="240" controls>
  <source src="assets/readme/demo.mp4" type="video/mp4">
</video>

</div>

Here we also show some cases of solving tasks by XAgent:
## Case 1. Data Analysis: Demonstrating the Effectiveness of Dual-Loop Mechanism
We start with a case of aiding users in intricate data analysis. Here, our user submitted an `iris.zip` file to XAgent, seeking assistance in data analysis. XAgent swiftly broke down the task into four sub-tasks: (1) data inspection and comprehension, (2) verification of the system's Python environment for relevant data analysis libraries, (3) crafting data analysis code for data processing and analysis, and (4) compiling an analytical report based on the Python code's execution results.
Here is a figure drawn by XAgent.
![Data Statics by XAgent](assets/readme/statistics.png)


## Case 2. Recommendation: A New Paradigm of Human-Agent Interaction
Empowered with the unique capability to actively seek human assistance and collaborate in problem-solving, XAgent continues to redefine the boundaries of human-agent cooperation. As depicted in screenshot below, a user sought XAgent's aid in recommending some great restaurants for a friendly gathering, yet failed to provide specific details. Recognizing the insufficiency of the provided information, XAgent employed the AskForHumanHelp tool, prompting human intervention to elicit the user's preferred location, budget constraints, culinary preferences, and any dietary restrictions. Armed with this valuable feedback, XAgent seamlessly generated tailored restaurant recommendations, ensuring a personalized and satisfying experience for the user and their friends.
![Illustration of Ask for Human Help of XAgent](assets/readme/ask_for_human_help.png)

## Case 3. Training Model: A Sophisticated Tool User
XAgent not only tackles mundane tasks but also serves as an invaluable aid in complex tasks such as model training. Here we show a scenario where a user desires to analyze movie reviews and evaluate the public sentiment surrounding particular films. In response, XAgent promptly initiates the process by downloading the IMDB dataset to train a cutting-edge BERT model (see screenshot below), harnessing the power of deep learning. Armed with this trained BERT model, XAgent seamlessly navigates the intricate nuances of movie reviews, offering insightful predictions regarding the public's perception of various films.
![bert_1](assets/readme/bert_1.png)
![bert_2](assets/readme/bert_2.png)
![bert_3](assets/readme/bert_3.png)

## 📊 Evaluation
We conduct human preference evaluation to evaluate XAgent's performance. We prepare over 50 real-world complex tasks for evaluation, which can be categorized into 5 classes: Search and Report, Coding and Developing, Data Analysis, Math, and Life Assistant.
We compare the results of XAgent with [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT), which shows a total win of XAgent over AutoGPT. You can download records for XAgent [here](https://drive.google.com/drive/folders/1_slFNXUBQ1CGiNLMCCYoQXZYNGAAdHok?usp=sharing).

![HumanPrefer](assets/readme/agent_comparison.png)

We report a significant improvement of XAgent over AutoGPT in terms of human preference.

We also evaluate XAgent on the following benchmarks:
![Benchmarks](assets/readme/eval_on_dataset.png)


<div><a id="Blog"></a></div>

# 🖌️ Blog

Coming Soon.

<div><a id="Citation"></a></div>

# Citation
If you find our repo useful, please kindly consider citing:
```angular2
@misc{xagent2023,
      title={XAgent: An Autonomous Agent for Complex Task Solving}, 
      author={XAgent Team},
      year={2023},
}
```
