import json
import json5

from typing import List
from colorama import Fore, Style
from copy import deepcopy

from XAgent.logs import logger
from XAgent.workflow.base_query import BaseQuery
from XAgent.utils import TaskSaveItem, RequiredAbilities, PlanOperationStatusCode, TaskStatusCode
from XAgent.message_history import Message
from XAgent.data_structure.plan import Plan
from XAgent.ai_functions import  function_manager
from XAgent.core import XAgentCoreComponents
from XAgent.agent.summarize import summarize_plan,clip_text
from XAgent.config import CONFIG

def plan_function_output_parser(function_output_item: dict) -> Plan:
    """Parses the function output item into a Plan object.

    Args:
        function_output_item (dict): The dictionary representing the function output item.

    Returns:
        Plan: The parsed Plan object.
    """
    subtask_node = TaskSaveItem()
    subtask_node.load_from_json(function_output_item=function_output_item)
    subplan = Plan(subtask_node)
    return subplan

class PlanRefineChain():
    """Represents a chain of plan refinements.

    This class keeps track of the refined plans and the associated refine functions.

    Attributes:
        plans (List[Plan]): The list of refined plans.
        functions (List[dict]): The list of refine functions.
    """

    def __init__(self, init_plan):
        """Initializes a PlanRefineChain object.

        Args:
            init_plan: The initial plan.
        """
        self.plans = [deepcopy(init_plan)]
        self.functions = []

    def register(self, function_name, function_input, function_output, new_plan: Plan):
        """Registers a plan refinement.

        This method adds the function name, input, and output, as well as the new plan to the refine chain.

        Args:
            function_name (str): The name of the refine function.
            function_input (dict): The input of the refine function.
            function_output (str): The output of the refine function.
            new_plan (Plan): The new plan after refinement.
        """
        self.functions.append({
            "name": function_name,
            "input": function_input,
            "output": function_output,
        })
        self.plans.append(deepcopy(new_plan))

        XAgentCoreComponents.global_recorder.regist_plan_modify(
            refine_function_name = function_name,
            refine_function_input = function_input,
            refine_function_output = function_output,
            plan_after = new_plan.to_json(posterior=True),
        )

    def parse_to_message_list(self, flag_changed) -> List[Message]:
        """Parses the refine chain to a list of messages.

        This method generates a list of messages describing each refinement step in the refine chain.

        Args:
            flag_changed: A flag indicating whether the plan has changed.

        Returns:
            List[Message]: A list of messages.
        """
        assert len(self.plans) == len(self.functions) + 1

        if CONFIG.enable_summary:
            init_message = summarize_plan(self.plans[0].to_json())
        else:
            init_message = json.dumps(self.plans[0].to_json(), indent=2, ensure_ascii=False)
        init_message =  Message("user", f"""The initial plan and the execution status is:\n'''\n{init_message}\n'''\n\n""")
        output_list = [init_message]
        for k, (function, output_plan) in enumerate(zip(self.functions, self.plans[1:])):
            operation_message = Message("user", f"""For the {k+1}\'th step, You made the following operation:\nfunction_name: {function["name"]}\n'''\n{json.dumps(function["input"],indent=2,ensure_ascii=False)}\n'''\nThen get the operation result:\n{function["output"]}\n""")
            output_list.append(operation_message)
        if len(self.plans) > 1:
            if flag_changed:
                if CONFIG.enable_summary:
                    new_message = summarize_plan(self.plans[-1].to_json())
                else:
                    new_message = json.dumps(self.plans[-1].to_json(), indent=2, ensure_ascii=False)
                output_list.append(Message("user", f"""The total plan changed to follows:\n'''\n{new_message}\n'''\n\n"""))
            else:
                output_list.append(Message("user", f"The total plan stay unchanged"))
        return output_list

class PlanAgent():
    """Represents a plan agent.

    This class is responsible for generating and refining plans.

    Attributes:
        config: The configuration for the plan agent.
        query (BaseQuery): The base query for generating plans.
        avaliable_tools_description_list (List[dict]): The list of available tool descriptions.
        plan (Plan): The plan.
        refine_chains (List[PlanRefineChain]): The list of refine chains.
    """
    def __init__(self, config, query: BaseQuery, avaliable_tools_description_list: List[dict]):
        """Initializes a PlanAgent object.

        Args:
            config: The configuration for the plan agent.
            query (BaseQuery): The base query for generating plans.
            avaliable_tools_description_list (List[dict]): The list of available tool descriptions.
        """
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

    def initial_plan_generation(self, agent_dispatcher):
        """Generates the initial plan.

        This method generates the initial plan by calling the plan generation agent.
        """
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= GENERATE INITIAL_PLAN -=-=-=-=-=-=-=",
            Fore.GREEN,
            "",
        )

        split_functions = deepcopy(function_manager.get_function_schema('subtask_split_operation'))

        agent = agent_dispatcher.dispatch(
            RequiredAbilities.plan_generation,
            target_task=f"Generate a plan to accomplish the task: {self.query.task}",
            # avaliable_tools_description_list=self.avaliable_tools_description_list
        )

        # TODO: not robust. dispatcher generated prompt may not contain these specified placeholders?
        new_message , _ = agent.parse(
            placeholders={
                "system": {
                    # "avaliable_tool_descriptions": json.dumps(self.avaliable_tools_description_list, indent=2, ensure_ascii=False),
                    "avaliable_tool_names": str([cont["name"] for cont in self.avaliable_tools_description_list]),
                },
                "user": {
                    "query": self.plan.data.raw
                }
            },
            arguments=deepcopy(function_manager.get_function_schema('simple_thought')['parameters']),
            functions=[split_functions], 
        )
        
        subtasks = json5.loads(new_message["function_call"]["arguments"])

        for subtask_item in subtasks["subtasks"]:
            subplan = plan_function_output_parser(subtask_item)
            Plan.make_relation(self.plan, subplan)

    def plan_iterate_based_on_memory_system(self):
        """Iteratively refines the plan based on the memory system.

        This method iteratively refines the plan based on the memory system.
        """
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= ITERATIVELY REFINE PLAN BASED ON MEMORY SYSTEM -=-=-=-=-=-=-=",
            Fore.BLUE,
        )
        print("Not Implemented, skip")
        # TODO

    @property
    def latest_plan(self):
        """Gets the latest plan.

        Returns:
            The latest plan.
        """
        return self.plan

    def plan_refine_mode(self, now_dealing_task: Plan, toolserver_interface, agent_dispatcher):
        """Enters the plan refine mode.

        This method enters the plan refine mode and performs plan refinements based on user suggestions.

        Args:
            now_dealing_task (Plan): The task that is currently being dealt with.
        """
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
        workspace_files,length = clip_text(workspace_files,1000,clip_end=True)
                
        while modify_steps < max_step:

            logger.typewriter_log(
                f"-=-=-=-=-=-=-= Continually refining planning (still in the loop)-=-=-=-=-=-=-=",
                Fore.GREEN,
            )

            subtask_id = now_dealing_task.get_subtask_id(to_str=True)
            flag_changed = False
            
            additional_message_list = self.refine_chains[-1].parse_to_message_list(flag_changed)

            functions=[deepcopy(function_manager.get_function_schema('subtask_operations'))]
            
            new_message , _ = agent.parse(
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
                        "workspace_files": workspace_files,
                        "refine_node_message":refine_node_message,
                    }
                }, 
                arguments=deepcopy(function_manager.get_function_schema('simple_thought')['parameters']),
                functions=functions, 
                additional_messages=additional_message_list,
                additional_insert_index=-1,
            )
            function_name = new_message["function_call"]["name"]
            function_input = json5.loads(new_message["function_call"]["arguments"])

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
        """Deals with subtask splitting.

        This method handles subtask splitting.

        Args:
            function_input (dict): The function input.
            now_dealing_task (Plan): The task that is currently being dealt with.

        Returns:
            str: The function output.
            PlanOperationStatusCode: The status code.
        """
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
        """Deals with subtask deletion.

        This method handles subtask deletion.

        Args:
            function_input (dict): The function input.
            now_dealing_task (Plan): The task that is currently being dealt with.

        Returns:
            str: The function output.
            PlanOperationStatusCode: The status code.
        """
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
        """Deals with subtask modification.

        This method handles subtask modification.

        Args:
            function_input (dict): The function input.
            now_dealing_task (Plan): The task that is currently being dealt with.

        Returns:
            str: The function output.
            PlanOperationStatusCode: The status code.
        """
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
        """Deals with subtask addition.

        This method handles subtask addition.

        Args:
            function_input (dict): The function input.
            now_dealing_task (Plan): The task that is currently being dealt with.

        Returns:
            str: The function output.
            PlanOperationStatusCode: The status code.
        """
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
        
        if former_subtask.get_depth() <= 1:
            return json.dumps({"error": f"You are not allowed to add a subtask at root level. Nothing happended",}), PlanOperationStatusCode.TARGET_SUBTASK_NOT_FOUND
        
        if len(former_subtask.father.children) + len(function_input["subtasks"]) > self.config.max_plan_tree_width: # fixs bugs here: the length calculation is incorrect
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