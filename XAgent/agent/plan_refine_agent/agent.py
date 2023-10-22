from typing import List
from XAgent.agent.plan_generate_agent import PlanGenerateAgent
from XAgent.utils import RequiredAbilities
from XAgent.message_history import Message

class PlanRefineAgent(PlanGenerateAgent):
    abilities = set([RequiredAbilities.plan_refinement])

    def parse(
        self,
        placeholders: dict = {},
        arguments:dict = None,
        functions=None,
        function_call=None,
        stop=None,
        additional_messages: List[Message] = [],
        additional_insert_index: int = -1,
        *args,
        **kwargs
    ):
        prompt_messages = self.fill_in_placeholders(placeholders)
        messages =prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
        
        return self.generate(
            messages=messages,
            arguments=arguments,
            functions=functions,
            function_call=function_call,
            stop=stop,
            *args,**kwargs
        ) 
