import json
import json5

from typing import List
from colorama import Fore, Style
from copy import deepcopy

from XAgent.loggers.logs import logger
from XAgent.workflow.base_query import BaseQuery
from XAgent.global_vars import agent_dispatcher
from XAgent.utils import TaskSaveItem, RequiredAbilities, PlanOperationStatusCode, TaskStatusCode
from XAgent.message_history import Message
from XAgent.data_structure.plan import Plan
from XAgent.ai_functions import  function_manager
from XAgent.running_recorder import recorder
from XAgent.tool_call_handle import toolserver_interface
from XAgent.agent.summarize import summarize_plan
from XAgent.config import CONFIG
def plan_function_output_parser(function_output_item: dict) -> Plan:
    subtask_node = TaskSaveItem()
    subtask_node.load_from_json(function_output_item=function_output_item)
    subplan = Plan(subtask_node)
    return subplan


class PlanRefineChain():
    def __init__(self, init_plan):
        self.plans = [deepcopy(init_plan)]
        self.functions = []
    
    def register(self,function_name, function_input,function_output,new_plan: Plan):
        self.functions.append({
            "name": function_name,
            "input": function_input,
            "output": function_output,
        })
        self.plans.append(deepcopy(new_plan))

        recorder.regist_plan_modify(
            refine_function_name = function_name,
            refine_function_input = function_input,
            refine_function_output = function_output,
            plan_after = new_plan.to_json(posterior=True),
        )
    
    def parse_to_message_list(self, flag_changed) -> List[Message]:
        assert len(self.plans) == len(self.functions) + 1
        
        if CONFIG.enable_summary: 
            init_message = summarize_plan(self.plans[0].to_json())
        else:
            init_message = json.dumps(self.plans[0].to_json(),indent=2,ensure_ascii=False)
        init_message =  Message("user", f"""The initial plan and the execution status is:\n'''\n{init_message}\n'''\n\n""")
        output_list = [init_message]
        for k, (function, output_plan) in enumerate(zip(self.functions, self.plans[1:])):
            operation_message = Message("user", f"""For the {k+1}\'th step, You made the following operation:
function_name: {function["name"]}
'''
{json.dumps(function["input"],indent=2,ensure_ascii=False)}
'''

Then get the operation result:
{function["output"]}

""")
            output_list.append(operation_message)
        if len(self.plans) > 1:
            if flag_changed:
                if CONFIG.enable_summary: 
                    new_message = summarize_plan(self.plans[-1].to_json())
                else:
                    new_message = json.dumps(self.plans[-1].to_json(),indent=2,ensure_ascii=False)
                output_list.append(Message("user", f"""The total plan changed to follows:\n'''\n{new_message}\n'''\n\n"""))
            else:
                output_list.append(Message("user", f"The total plan stay unchanged"))
        return output_list

class PlanAgent():
    def __init__(self, config, query: BaseQuery, avaliable_tools_description_list: List[dict]):
        self.config = config
        self.query = query
        self.avaliable_tools_description_list = avaliable_tools_description_list

        self.plan = Plan(
            data = TaskSaveItem(
                name=f"act as {query.role_name}",
                goal=query.task,
                milestones=query.plan,
                # tool_budget=100,
            )
        )

        self.refine_chains: List[PlanRefineChain] = []


    def initial_plan_generation(self):
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= GENERATE INITIAL_PLAN -=-=-=-=-=-=-=",
            Fore.GREEN,
            "",
        )


        split_functions = deepcopy(function_manager.get_function_schema('subtask_split_operation'))
        # split_functions["parameters"]["properties"]["subtasks"]["items"]["properties"]["expected_tools"]["items"]["properties"]["tool_name"]["enum"] = [cont["name"] for cont in self.avaliable_tools_description_list]

        agent = agent_dispatcher.dispatch(
            RequiredAbilities.plan_generation,
            target_task=f"Generate a plan to accomplish the task: {self.query.task}",
            # avaliable_tools_description_list=self.avaliable_tools_description_list
        )

        # TODO: not robust. dispatcher generated prompt may not contain these specified placeholders?
        _, new_message , _ = agent.parse(
            placeholders={
                "system": {
                    # "avaliable_tool_descriptions": json.dumps(self.avaliable_tools_description_list, indent=2, ensure_ascii=False),
                    "avaliable_tool_names": str([cont["name"] for cont in self.avaliable_tools_description_list]),
                },
                "user": {
                    "query": self.plan.data.raw
                }
            },
            functions=[split_functions], 
            function_call={"name":"subtask_split_operation"},
        )
        
        subtasks = json5.loads(new_message["function_call"]["arguments"])

        for subtask_item in subtasks["subtasks"]:
            subplan = plan_function_output_parser(subtask_item)
            Plan.make_relation(self.plan, subplan)

    def plan_iterate_based_on_memory_system(self):
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= ITERATIVELY REFINE PLAN BASED ON MEMORY SYSTEM -=-=-=-=-=-=-=",
            Fore.BLUE,
        )
        print("Not Implemented, skip")
        # TODO

    @property
    def latest_plan(self):
        return self.plan

    def plan_refine_mode(self, now_dealing_task: Plan):
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= ITERATIVELY REFINE PLAN BASED ON TASK AGENT SUGGESTIONS -=-=-=-=-=-=-=",
            Fore.BLUE,
        )

        self.refine_chains.append(PlanRefineChain(self.plan)) 

        modify_steps = 0
        max_step = self.config.max_plan_refine_chain_length

        agent = agent_dispatcher.dispatch(
            RequiredAbilities.plan_refinement, 
            target_task="Refine the given plan.", 
            # avaliable_tools_description_list=self.avaliable_tools_description_list
        )
        try:
            refine_node_message = now_dealing_task.process_node.data["command"]["properties"]["args"]
            refine_node_message = refine_node_message["suggestions_for_latter_subtasks_plan"]["reason"]
        except:
            refine_node_message = ""
        workspace_files = str(toolserver_interface.execute_command_client("FileSystemEnv_print_filesys_struture", {"return_root":True}))
        
        while modify_steps < max_step:

            logger.typewriter_log(
                f"-=-=-=-=-=-=-= Continually refining planning (still in the loop)-=-=-=-=-=-=-=",
                Fore.GREEN,
            )

            subtask_id = now_dealing_task.get_subtask_id(to_str=True)
            flag_changed = False
            
            additional_message_list = self.refine_chains[-1].parse_to_message_list(flag_changed)

            function_call = None
            functions=[deepcopy(function_manager.get_function_schema('subtask_operations'))]
            function_call = {"name":"subtask_operations"}
            # print(message_list)
            try_times = 0


            while True:
                _,new_message , _ = agent.parse(
                    placeholders={
                        "system": {
                            # "avaliable_tool_descriptions": json.dumps(self.avaliable_tools_description_list, indent=2, ensure_ascii=False),
                            "avaliable_tool_names": str([cont["name"] for cont in self.avaliable_tools_description_list]),
                            "max_plan_tree_width": self.config.max_plan_tree_width,
                            "max_plan_tree_depth": self.config.max_plan_tree_depth,
                        },
                        "user": {
                            "subtask_id": subtask_id,
                            "max_step": max_step,
                            "modify_steps": modify_steps,
                            "max_plan_tree_depth": self.config.max_plan_tree_depth,
                            "workspace_files": workspace_files[:1000],
                            "refine_node_message":refine_node_message,
                        }
                    }, 
                    functions=functions, 
                    function_call=function_call,
                    additional_messages=additional_message_list,
                    additional_insert_index=-1,
                )
                # print(new_message)
                if not "function_call" in new_message.keys():
                    print("function_call not found, continue to call the LLM API for a new function_call")
                    try_times += 1
                    continue
                function_name = new_message["function_call"]["name"]
                function_input = json5.loads(new_message["function_call"]["arguments"])
                break

            if function_input['operation'] == 'split':
                # modify function_input here
                function_output, output_status_code = self.deal_subtask_split(function_input, now_dealing_task)
            elif function_input['operation'] == 'add':
                function_output, output_status_code = self.deal_subtask_add(function_input, now_dealing_task)
            elif function_input['operation'] == 'delete':
                function_output, output_status_code = self.deal_subtask_delete(function_input, now_dealing_task)
            elif function_input['operation'] == 'exit':
                output_status_code = PlanOperationStatusCode.PLAN_REFINE_EXIT
                function_output = json.dumps({
                    "content": "exit PLAN_REFINE_MODE successfully",
                })
            else:
                logger.typewriter_log("Error: ", Fore.RED, f"Operation {function_input['operation']} not found. Nothing happens")
                output_status_code = PlanOperationStatusCode.PLAN_OPERATION_NOT_FOUND
                function_output = json.dumps({
                    "error": f"Operation {function_input['operation']} not found. Nothing happens"
                })
            
            if "error" not in function_output:
                flag_changed = True

            self.refine_chains[-1].register(function_name=function_name,
                                            function_input=function_input,
                                            function_output=function_output,
                                            new_plan=self.plan)

            if output_status_code == PlanOperationStatusCode.MODIFY_SUCCESS:
                color = Fore.GREEN
            elif output_status_code == PlanOperationStatusCode.PLAN_REFINE_EXIT:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            logger.typewriter_log("SYSTEM: ", Fore.YELLOW, function_output)
            logger.typewriter_log(
                "PLAN MODIFY STATUS CODE: ", Fore.YELLOW, f"{color}{output_status_code.name}{Style.RESET_ALL}"
            )

            if output_status_code == PlanOperationStatusCode.PLAN_REFINE_EXIT or output_status_code == PlanOperationStatusCode.MODIFY_SUCCESS:
                return

            modify_steps += 1

    def deal_subtask_split(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode):
        print(json.dumps(function_input,indent=2,ensure_ascii=False))

        inorder_subtask_stack = Plan.get_inorder_travel(self.plan)
        target_subtask_id = function_input["target_subtask_id"].strip()
        all_subtask_ids = [cont.get_subtask_id(to_str=True) for cont in inorder_subtask_stack]

        can_edit = False
        for k, subtask in enumerate(inorder_subtask_stack):
            if subtask.get_subtask_id(to_str=True) == now_dealing_task.get_subtask_id(to_str=True):
                
                can_edit = True

            if subtask.get_subtask_id(to_str=True) == target_subtask_id:
                if not can_edit:
                    return json.dumps({"error": f"You can only split the TODO subtask plans together with the now_dealing_subtask, e.g. '>= {now_dealing_task.get_subtask_id(to_str=True)}'. Nothing happended",}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
                
                # if not subtask.data.status == TaskStatusCode.FAIL:
                #     return json.dumps({"error": f"You can only split the FAIL subtask plans together. This is a '{subtask.data.status.name}' Task. Nothing happended"}), PlanOperationStatusCode.OTHER_ERROR

                if subtask.get_depth() >= self.config.max_plan_tree_depth:
                    return json.dumps({"error": f"The plan tree has a max depth of {self.config.max_plan_tree_depth}. '{subtask.data.name}' already has a depth of {subtask.get_depth()}. Nothing happended"}), PlanOperationStatusCode.OTHER_ERROR

                for new_subtask in function_input["subtasks"]:
                    new_subplan = plan_function_output_parser(new_subtask)
                    Plan.make_relation(subtask,new_subplan)
                subtask.data.status = TaskStatusCode.SPLIT
                return json.dumps({"success": f"Subtask '{target_subtask_id}' has been split",}), PlanOperationStatusCode.MODIFY_SUCCESS

        return json.dumps({"error": f"target_subtask_id '{target_subtask_id}' not found. Nothing happended",}), PlanOperationStatusCode.TARGET_SUBTASK_NOT_FOUND


    def deal_subtask_delete(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode):
        print(json.dumps(function_input,indent=2,ensure_ascii=False))

        inorder_subtask_stack:list[Plan] = Plan.get_inorder_travel(self.plan)
        target_subtask_id = function_input["target_subtask_id"].strip()

        all_subtask_ids = [cont.get_subtask_id(to_str=True) for cont in inorder_subtask_stack]

        can_edit = False
        for k, subtask in enumerate(inorder_subtask_stack):
            if subtask.get_subtask_id(to_str=True) == target_subtask_id:
                if not can_edit:
                    return json.dumps({"error": f"You can only delete the TODO subtask plans, e.g., task_id>'{now_dealing_task.get_subtask_id(to_str=True)}', you are deleting {subtask.get_subtask_id(to_str=True)}. Nothing happended"}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
                
                
                if subtask.data.status != TaskStatusCode.TODO :
                    return json.dumps({"error": f"You can only delete the TODO subtask plans, e.g., task_id>'{now_dealing_task.get_subtask_id(to_str=True)}', you are deleting {subtask.get_subtask_id(to_str=True)}. Nothing happended"}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
                
                # try to delete the subtask
                subtask.father.children.remove(subtask)
                subtask.father = None
                
                return json.dumps({"success": f"Subtask '{target_subtask_id}' has been deleted",}), PlanOperationStatusCode.MODIFY_SUCCESS
            if subtask.get_subtask_id(to_str=True) == now_dealing_task.get_subtask_id(to_str=True):
                
                can_edit = True

        return json.dumps({"error": f"target_subtask_id '{target_subtask_id}' not found, should in {all_subtask_ids}. Nothing happended",}), PlanOperationStatusCode.TARGET_SUBTASK_NOT_FOUND


    def deal_subtask_modify(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode):
        print(json.dumps(function_input,indent=2,ensure_ascii=False))

        inorder_subtask_stack = Plan.get_inorder_travel(self.plan)
        target_subtask_id = function_input["target_subtask_id"].strip()

        all_subtask_ids = [cont.get_subtask_id(to_str=True) for cont in inorder_subtask_stack]

        can_edit = False
        for k, subtask in enumerate(inorder_subtask_stack):
            if subtask.get_subtask_id(to_str=True) == target_subtask_id:
                if not can_edit:
                    return json.dumps({"error": f"You can only modify the TODO subtask plans, e.g., task_id>'{now_dealing_task.get_subtask_id(to_str=True)}', you are modifying {subtask.get_subtask_id(to_str=True)}. Nothing happended"}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
                
                assert subtask.data.status == TaskStatusCode.TODO
                subtask.data.load_from_json(function_input["new_data"])

                return json.dumps({"success": f"Subtask '{target_subtask_id}' has been modified",}), PlanOperationStatusCode.MODIFY_SUCCESS
            if subtask.get_subtask_id(to_str=True) == now_dealing_task.get_subtask_id(to_str=True):
                
                can_edit = True

        return json.dumps({"error": f"target_subtask_id '{target_subtask_id}' not found, should in {all_subtask_ids}. Nothing happended",}), PlanOperationStatusCode.TARGET_SUBTASK_NOT_FOUND

    def deal_subtask_add(self, function_input: dict, now_dealing_task: Plan) -> (str, PlanOperationStatusCode):
        print(json.dumps(function_input,indent=2,ensure_ascii=False))

        inorder_subtask_stack:list[Plan] = Plan.get_inorder_travel(self.plan)
        former_subtask_id = function_input["target_subtask_id"].strip()

        all_subtask_ids = [cont.get_subtask_id(to_str=True) for cont in inorder_subtask_stack]

        # check whether the former_subtask_id is valid

        former_subtask = None
        for subtask in inorder_subtask_stack:
            if subtask.get_subtask_id(to_str=True) == former_subtask_id:
                former_subtask = subtask
                break
        if former_subtask is None:
            return json.dumps({"error": f"former_subtask_id '{former_subtask_id}' not found, should in {all_subtask_ids}. Nothing happended",}), PlanOperationStatusCode.TARGET_SUBTASK_NOT_FOUND
        
        former_subtask_id_list = former_subtask.get_subtask_id_list()
        now_dealing_task_id_list = now_dealing_task.get_subtask_id_list()
        
        if int(former_subtask_id_list[-1]) + len(function_input["subtasks"]) > self.config.max_plan_tree_width:
            return json.dumps({"error": f"The plan tree has a max width of {self.config.max_plan_tree_width}. '{former_subtask.data.name}' already has a width of {len(former_subtask.children)}. Nothing happended"}), PlanOperationStatusCode.OTHER_ERROR
            
        for i in range(min(len(former_subtask_id_list), len(now_dealing_task_id_list))):
            if former_subtask_id_list[i]<now_dealing_task_id_list[i]:
                return json.dumps({"error": f"You can only add the subtask plans after than now_dealing task, e.g. 'former_subtask_id >= {now_dealing_task.get_subtask_id(to_str=True)}'. Nothing happended",}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
        # pass check
        new_subplans = [plan_function_output_parser(new_subtask) for new_subtask in function_input["subtasks"]]

        subtask = former_subtask
        if subtask.father is None:
            return json.dumps({"error":f"Currently not support adding a subtask at root level!"}), PlanOperationStatusCode.MODIFY_FORMER_PLAN
        # assert subtask.father != None
        index = subtask.father.children.index(subtask)

        for new_subplan in new_subplans:
            new_subplan.father = subtask.father
        subtask.father.children[index+1:index+1] = new_subplans
        
        return json.dumps({"success": f"A new subtask has been added after '{former_subtask_id}'",}), PlanOperationStatusCode.MODIFY_SUCCESS