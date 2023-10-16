from typing import List
from XAgent.agent.plan_generate_agent import PlanGenerateAgent
from XAgent.utils import RequiredAbilities, LLMStatusCode
from XAgent.agent.utils import _chat_completion_request
from XAgent.message_history import Message

class PlanRefineAgent(PlanGenerateAgent):
    abilities = set([RequiredAbilities.plan_refinement])

    def parse(
        self,
        placeholders: dict = {},
        functions=None,
        function_call=None,
        stop=None,
        additional_messages: List[Message] = [],
        additional_insert_index: int = -1,
        *args,
        **kwargs
    ):
        prompt_messages = self.fill_in_placeholders(placeholders)
        # import pdb; pdb.set_trace()
        output = _chat_completion_request(
            messages=prompt_messages[:additional_insert_index]
            + additional_messages
            + prompt_messages[additional_insert_index:],
            functions=functions,
            function_call=function_call,
            model=self.config.default_completion_kwargs['model'],
            stop=stop,
            *args,
            **kwargs
        )

        message = output["choices"][0]["message"]
        tokens = output["usage"]

        return LLMStatusCode.SUCCESS, message, tokens
