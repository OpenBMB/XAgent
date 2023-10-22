import json
import json5
from typing import List
from copy import deepcopy

from XAgent.utils import RequiredAbilities
from XAgent.data_structure.node import ToolNode
from XAgent.workflow.plan_exec import Plan
from XAgent.global_vars import agent_dispatcher
from XAgent.agent.summarize import summarize_action,summarize_plan
from XAgent.ai_functions import function_manager

def get_posterior_knowledge(all_plan: Plan, terminal_plan: Plan, finish_node: ToolNode, tool_functions_description_list: List[dict], config):

    agent = agent_dispatcher.dispatch(
        RequiredAbilities.reflection,
        "Reflect on the previous actions and give the posterior knowledge"
    )
    all_plan = all_plan.to_json()
    terminal_plan = terminal_plan.to_json()
    if config.enable_summary:
        terminal_plan = summarize_plan(terminal_plan)
        action_process = summarize_action(finish_node.process, terminal_plan)
        all_plan = summarize_plan(all_plan)
    else:
        action_process = json.dumps(finish_node.process,indent=2,ensure_ascii=False)
        all_plan = json.dumps(all_plan, indent=2, ensure_ascii=False)
        terminal_plan = json.dumps(terminal_plan, indent=2, ensure_ascii=False)
        
    new_message,_ = agent.parse(
        placeholders={
            "system": {
                "all_plan": all_plan,
                "terminal_plan": terminal_plan,
                "tool_functions_description_list": json.dumps(tool_functions_description_list, indent=2, ensure_ascii=False),
                "action_process": action_process
            }
        },
        arguments=function_manager.get_function_schema('generate_posterior_knowledge')['parameters']
    )

    data = json5.loads(new_message["arguments"])
    # print(data)

    return data
    




