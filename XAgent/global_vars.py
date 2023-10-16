# from XAgent.workflow.working_memory import WorkingMemoryAgent
from XAgent.agent.dispatcher import AutomaticAgentDispatcher, XAgentDispatcher
#from XAgent.vector_db import VectorDBInterface
# from XAgent.running_recorder import RunningRecoder
from XAgent.config import CONFIG as config

agent_dispatcher = XAgentDispatcher(config, enable=False)
# working_memory_agent = WorkingMemoryAgent()
# vector_db_interface = VectorDBInterface()
# recorder = RunningRecoder()