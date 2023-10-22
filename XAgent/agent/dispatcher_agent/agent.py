import re
import copy
import json5
from typing import List

from .prompt import SYSTEM_PROMPT

from XAgent.logs import logger
from XAgent.message_history import Message
from XAgent.agent.base_agent import BaseAgent

class DispatcherAgent(BaseAgent):
    def __init__(self, config, prompt_messages: List[Message] = None):
        self.config = config
        self.prompt_messages = (
            self.default_prompt_messages if prompt_messages is None else prompt_messages
        )

    @property
    def default_prompt_messages(self):
        return [Message(role="system", content=SYSTEM_PROMPT)]

    def find_all_placeholders(self, prompt):
        return re.findall(r"{{(.*?)}}", prompt)

    def construct_input_messages(
        self,
        task: str,
        example_input: str,
        example_system_prompt: str,
        example_user_prompt: str,
        retrieved_procedure: str,
    ):
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
        try:
            # additional_prompt = message["content"]
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
        message,tokens = self.generate(
            messages=self.construct_input_messages(
                task,
                example_input,
                example_system_prompt,
                example_user_prompt,
                # self.retrieved_procedure(task),
                ""  # The retrieved procedures are mostly irrelevant for now
            ),
            stop=stop,
            **args,
        )

        # additional_prompt = self.extract_prompts_from_response(message)
        additional_prompt = message['arguments']['additional_prompt']

        prompt_messages = []
        if additional_prompt != "":
            example_user_prompt += "\n\nADDITIONAL NOTES\n" + additional_prompt
        prompt_messages.append(Message(role="system", content=example_system_prompt))
        prompt_messages.append(Message(role="user", content=example_user_prompt))

        return prompt_messages, tokens