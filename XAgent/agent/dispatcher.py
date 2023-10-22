import abc
from typing import List
from colorama import Fore, Style
from XAgent.config import CONFIG

from XAgent.agent.base_agent import BaseAgent
from XAgent.utils import RequiredAbilities, TaskSaveItem, AgentRole
from XAgent.logs import logger
from XAgent.agent.dispatcher_agent import DispatcherAgent
from XAgent.message_history import Message


class AgentDispatcher(metaclass=abc.ABCMeta):
    def __init__(self):
        self.agent_markets = {}
        for requirement in RequiredAbilities:
            self.agent_markets[requirement] = []
        logger.typewriter_log(
            f"Constructing an AgentDispatcher:",
            Fore.YELLOW,
            self.__class__.__name__,
        )

    @abc.abstractmethod
    def dispatch(self, ability_type: RequiredAbilities, target_task) -> BaseAgent:
        pass

    def dispatch_role(self, target_task: TaskSaveItem) -> AgentRole:
        return AgentRole()

    def regist_agent(self, agent: BaseAgent):
        for requirement in RequiredAbilities:
            if requirement in agent.abilities:
                self.agent_markets[requirement].append(agent)


class AutomaticAgentDispatcher(AgentDispatcher):
    def __init__(
        self,
    ):
        super().__init__()

    def dispatch(self, ability_type: RequiredAbilities, target_task) -> BaseAgent:
        return self.agent_markets[ability_type][0]()


class XAgentDispatcher(AgentDispatcher):
    """Generate the prompt and the agent for the given task."""

    def __init__(self, config, enable=True):
        super().__init__()
        self.config = config
        self.dispatcher = DispatcherAgent(config)
        self.enable = enable

    def get_examples(self, ability_type: RequiredAbilities):
        if ability_type == RequiredAbilities.plan_generation:
            from .plan_generate_agent import get_examples_for_dispatcher
        elif ability_type == RequiredAbilities.plan_refinement:
            from .plan_refine_agent import get_examples_for_dispatcher
        elif ability_type == RequiredAbilities.tool_tree_search:
            from .tool_agent import get_examples_for_dispatcher
        elif ability_type == RequiredAbilities.reflection:
            from .reflect_agent import get_examples_for_dispatcher
        return get_examples_for_dispatcher()

    def build_agent(
        self,
        ability_type: RequiredAbilities,
        config,
        prompt_messages: List[Message],
        *args,
        **kwargs,
    ) -> BaseAgent:
        try:
            agent = self.agent_markets[ability_type][0](
                config, prompt_messages, *args, **kwargs
            )
        except:
            # TODO: remove when all the agents can be created with dispatcher.
            logger.info("build agent error, use default agent")
            agent = self.agent_markets[ability_type][0](config, *args, **kwargs)
        return agent

    def dispatch(
        self,
        ability_type: RequiredAbilities,
        target_task: TaskSaveItem,
        *args,
        **kwargs,
    ) -> BaseAgent:
        example_input, example_system_prompt, example_user_prompt = self.get_examples(
            ability_type
        )
        if self.enable:
            logger.typewriter_log(self.__class__.__name__, Fore.GREEN, f"Refine the prompt of a specific agent for {Fore.GREEN}RequiredAbilities.{ability_type.name}{Style.RESET_ALL}")
            _, prompt_messages, tokens = self.dispatcher.parse(
                target_task, example_input, example_system_prompt, example_user_prompt
            )
            print(prompt_messages)
            if prompt_messages[0].content == "" and prompt_messages[1].content == "":
                logger.info("Dispatcher fail to follow the output format, we fallback to use the default prompt.")
                prompt_messages = [
                    Message(role="system", content=example_system_prompt),
                    Message(role="user", content=example_user_prompt),
                ]
            else:
                logger.typewriter_log(self.__class__.__name__, Fore.GREEN, f"The prompt has been refined!")
        else:
            prompt_messages = [
                Message(role="system", content=example_system_prompt),
                Message(role="user", content=example_user_prompt),
            ]
        agent = self.build_agent(ability_type, self.config, prompt_messages, *args, **kwargs)
        return agent



agent_dispatcher = XAgentDispatcher(CONFIG, enable=False)