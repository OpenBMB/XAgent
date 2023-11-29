import abc
from typing import List
from colorama import Fore, Style
from XAgent.config import CONFIG

from XAgent.agent.base_agent import BaseAgent
from XAgent.utils import RequiredAbilities, TaskSaveItem, AgentRole
from XAgent.agent.dispatcher_agent import DispatcherAgent
from XAgent.message_history import Message


class AgentDispatcher(metaclass=abc.ABCMeta):
    """
    Base abstract class for Agent Dispatcher.
    """
    def __init__(self, logger=None):
        """
        Initialize AgentDispatcher. Assign agent markets for each requirement in RequiredAbilities.
        Agent markets are initially empty.
        """
        self.agent_markets = {}
        self.logger = logger
        for requirement in RequiredAbilities:
            self.agent_markets[requirement] = []
        self.logger.typewriter_log(
            f"Constructing an AgentDispatcher:",
            Fore.YELLOW,
            self.__class__.__name__,
        )

    @abc.abstractmethod
    def dispatch(self, ability_type: RequiredAbilities, target_task) -> BaseAgent:
        """
        Abstract dispatch method to be implemented by subclasses. Dispatches tasks based
        on ability type.

        Args:
            ability_type (RequiredAbilities): The ability type required for the task.
            target_task: The task which needs to be dispatched.

        Returns:
            BaseAgent: Base agent responsible for the task.
        """
        pass

    def dispatch_role(self, target_task: TaskSaveItem) -> AgentRole:
        """
        Dispatch a role for the target task.

        Args:
            target_task (TaskSaveItem): The task for which a role needs to be dispatched.

        Returns:
            AgentRole: Returns a default AgentRole.
        """
        return AgentRole()

    def regist_agent(self, agent: BaseAgent):
        """
        Register agent to the respective agent markets based on abilities.

        Args:
            agent (BaseAgent): The agent that needs to be registered.
        """
        for requirement in RequiredAbilities:
            if requirement in agent.abilities:
                self.agent_markets[requirement].append(agent)


class AutomaticAgentDispatcher(AgentDispatcher):
    """
    AgentDispatcher that automatically dispatches tasks to agents.
    """

    def __init__(self):
        """
        Initialize AutomaticAgentDispatcher.
        """
        super().__init__()

    def dispatch(self, ability_type: RequiredAbilities, target_task) -> BaseAgent:
        """
        Dispatch task to the agent in the market corresponding to the task ability type.

        Args:
            ability_type (RequiredAbilities): The ability type required for the task.
            target_task: The task which needs to be dispatched.

        Returns:
            BaseAgent: Base agent responsible for the task.
        """
        return self.agent_markets[ability_type][0]()


class XAgentDispatcher(AgentDispatcher):
    """Generate the prompt and the agent for the given task."""

    def __init__(self, config, enable=True, logger=None):
        """
        Initialize XAgentDispatcher.

        Args:
            config: Dispatcher configuration.
            enable (bool, optional): Whether the dispatcher is active. Defaults to True.
        """
        self.logger = logger
        super().__init__(logger)
        self.config = config
        self.dispatcher = DispatcherAgent(config)
        self.enable = enable

    def get_examples(self, ability_type: RequiredAbilities):
        """
        Get examples based on the ability type.

        Args:
            ability_type (RequiredAbilities): The ability type for which examples are needed.

        Returns:
            Returns examples for the dispatcher.
        """
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
        """
        Build agent based on the ability type. If failed, fallback to use default agent.

        Args:
            ability_type (RequiredAbilities): Type of ability required by the agent.
            config: Configuration for the agent.
            prompt_messages (List[Message]): List of prompt messages for the agent.

        Returns:
            BaseAgent: The built agent.
        """
        try:
            agent = self.agent_markets[ability_type][0](
                config, prompt_messages, *args, **kwargs
            )
        except:
            # TODO: remove when all the agents can be created with dispatcher.
            self.logger.info("build agent error, use default agent")
            agent = self.agent_markets[ability_type][0](config, *args, **kwargs)
        return agent

    def dispatch(
        self,
        ability_type: RequiredAbilities,
        target_task: TaskSaveItem,
        *args,
        **kwargs,
    ) -> BaseAgent:
        """
        Dispatch task to the agent in the market corresponding to the task ability type.
        Additionally refines the prompt for the task and builds the agent.

        Args:
            ability_type (RequiredAbilities): The ability type required for the task.
            target_task (TaskSaveItem): The task which needs to be dispatched.

        Returns:
            BaseAgent: Base agent responsible for the task.
        """
        example_input, example_system_prompt, example_user_prompt = self.get_examples(
            ability_type
        )
        if self.enable:
            self.logger.typewriter_log(self.__class__.__name__, Fore.GREEN, f"Refine the prompt of a specific agent for {Fore.GREEN}RequiredAbilities.{ability_type.name}{Style.RESET_ALL}")
            _, prompt_messages, tokens = self.dispatcher.parse(
                target_task, example_input, example_system_prompt, example_user_prompt
            )
            print(prompt_messages)
            if prompt_messages[0].content == "" and prompt_messages[1].content == "":
                self.logger.info("Dispatcher fail to follow the output format, we fallback to use the default prompt.")
                prompt_messages = [
                    Message(role="system", content=example_system_prompt),
                    Message(role="user", content=example_user_prompt),
                ]
            else:
                self.logger.typewriter_log(self.__class__.__name__, Fore.GREEN, f"The prompt has been refined!")
        else:
            prompt_messages = [
                Message(role="system", content=example_system_prompt),
                Message(role="user", content=example_user_prompt),
            ]
        agent = self.build_agent(ability_type, self.config, prompt_messages, *args, **kwargs)
        return agent


# agent_dispatcher = XAgentDispatcher(CONFIG, enable=False)