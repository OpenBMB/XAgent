import re
import copy
import json5
from typing import List

from .prompt import SYSTEM_PROMPT

from XAgent.logs import logger
from XAgent.message_history import Message
from XAgent.agent.base_agent import BaseAgent

class DispatcherAgent(BaseAgent):
    """
    A subclass of BaseAgent whose primary function is to help dispatch tasks to 
    different agent handlers based on the task requirements.

    Attributes:
    ------------
    config : object
        The configuration settings for the agent.
    prompt_messages : List[Message]
        The list of prompt messages for the agent to dispatch.
    """
    def __init__(self, config, prompt_messages: List[Message] = None):
        """
        Initialize a DispatcherAgent instance.

        Args:
        -------
        config : object
            The configuration settings for the agent.
        prompt_messages : list, optional
            The list of prompt messages for the agent to dispatch, defaults to None.
            If not provided, default_prompt_messages is used instead.
        """
        self.config = config
        self.prompt_messages = (
            self.default_prompt_messages if prompt_messages is None else prompt_messages
        )

    @property
    def default_prompt_messages(self):
        """
        Returns the default system prompt messages in the form of a list of Message objects.

        Returns:
        -----------
        list[Message] : 
            A list containing the default prompt message.
        """
        return [Message(role="system", content=SYSTEM_PROMPT)]

    def find_all_placeholders(self, prompt):
        """
        Finds all placeholders within a prompt.

        Args:
        --------
        prompt : str
            The string within which placeholders are to be found.

        Returns:
        --------
        list[str] : 
            A list of all placeholders found within the prompt.
        """
        return re.findall(r"{{(.*?)}}", prompt)

    def construct_input_messages(
        self,
        task: str,
        example_input: str,
        example_system_prompt: str,
        example_user_prompt: str,
        retrieved_procedure: str,
    ):
        """
        Constructs input messages by replacing placeholders in the prompt_messages 
        with provided data.

        Args:
        ---------
        task : str
            The task to be completed.
        example_input : str
            An example input for the task.
        example_system_prompt : str
            The example system prompt for the task.
        example_user_prompt : str
            The example user prompt for the task.
        retrieved_procedure : str
            The retrieved process for the task.

        Returns:
        ---------
        list[Message] :
            A list containing the constructed input messages with placeholders replaced with provided data.
        """
        prompt_messages = copy.deepcopy(self.prompt_messages)
        # TODO: Make it more robust. Here we assume only the first message is system prompt
        #       and we only update the placeholders in the first message.
        prompt_messages[0].content = (
            prompt_messages[0]
            .content.replace("{{example_system_prompt}}", example_system_prompt)
            .replace("{{example_user_prompt}}", example_user_prompt)
            .replace("{{retrieved_procedure}}", retrieved_procedure)
            .replace("{{task}}", task)
        )
        return prompt_messages  # + [Message(role="user", content=task)] 

    def extract_prompts_from_response(self, message):
        """
        Extracts additional prompts from the dispatcher's response message.

        Args:
        --------
        message : str 
           The response message from the dispatcher.

        Returns:
        ---------
        str : 
            The additional prompt extracted from the message; if not found, "" is returned.

        """
        try:
            additional_prompt = re.findall(r"ADDITIONAL USER PROMPT:?\n```(.*)```", message['content'], re.DOTALL)[0].strip()
        except IndexError as e:
            logger.error(
                f"Failed to extract prompts from the dispatcher's response:\n{message['content']}"
            )
            logger.error("Fallback to use the default prompts.")
            additional_prompt = ""
        return additional_prompt

    def retrieved_procedure(self, query: str) -> str:
        # TODO: this function should be implemented thru tool server

        """
        Retrieves a procedure relevant to the given query from an external site.

        Args:
        --------
        query : str
            The query to retrieve the relevant procedure.

        Returns:
        ---------
        str : 
            The relevant procedure retrieved; if retrieval fails, the string 'None' is returned.
        """
        
        url = "https://open-procedures.replit.app/search/"
        try:
            import requests
            import json

            relevant_procedures = requests.get(url, params={'query': query}).json()[
                "procedures"
            ][0]
        except:
            # For someone, this failed for a super secure SSL reason.
            # Since it's not strictly necessary, let's worry about that another day. Should probably log this somehow though.
            relevant_procedures = "None"

        return relevant_procedures

    def parse(
        self,
        task: str,
        example_input: str,
        example_system_prompt: str,
        example_user_prompt: str,
        stop=None,
        **args,
    ) -> List[Message]:
        # TODO: should we consider additional messages when generating prompt?
        # currently the plan generation and refine agent are the same since we
        # don't consider the additional messages when generating prompt.

        """
        Parse the task and related data to generate prompt messages.

        Args:
        ---------
        task : str
            The task to be processed.
        example_input : str
            An example input related to the task.
        example_system_prompt : str
            An example system prompt related to the task.
        example_user_prompt : str
            An example user prompt related to the task.
        stop : str, optional
            The stopping criterion for message generation, defaults to None.

        Returns:
        ---------
        Tuple[List[Message], List[str]] : 
            A tuple containing a list of prompt messages and tokens.
        """
        message,tokens = self.generate(
            messages=self.construct_input_messages(
                task,
                example_input,
                example_system_prompt,
                example_user_prompt,
                ""  
            ),
            stop=stop,
            **args,
        )

        additional_prompt = message['arguments']['additional_prompt']

        prompt_messages = []
        if additional_prompt != "":
            example_user_prompt += "\n\nADDITIONAL NOTES\n" + additional_prompt
        prompt_messages.append(Message(role="system", content=example_system_prompt))
        prompt_messages.append(Message(role="user", content=example_user_prompt))

        return prompt_messages, tokens