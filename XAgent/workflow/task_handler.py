import json
import uuid
from typing import Dict, List

from colorama import Fore

# , working_memory_agent, vector_db_interface
from XAgent.global_vars import agent_dispatcher
from XAgent.inner_loop_search_algorithms.ReACT import ReACTChainSearch
from XAgent.logs import logger, print_task_save_items
from XAgent.running_recorder import recorder
from XAgent.tool_call_handle import function_handler, toolserver_interface
from XAgent.agent.summarize import summarize_plan 
from XAgent.utils import (RequiredAbilities, SearchMethodStatusCode,
                          TaskSaveItem, TaskStatusCode)
from XAgent.workflow.base_query import BaseQuery
# from XAgent.prompts.subtask_generation_prompt import get_subtask_split_messages, subtask_generate_function
from XAgent.workflow.plan_exec import Plan, PlanAgent
from XAgent.workflow.reflection import get_posterior_knowledge
from XAgentServer.interaction import XAgentInteraction
from XAgentServer.models.ws import XAgentOutputData

from .working_memory import working_memory_agent


class TaskHandler():
    def __init__(self, config,
                 query: BaseQuery,
                 function_list: List[Dict],
                 tool_functions_description_list: List[dict],
                 interaction: XAgentInteraction):
        self.config = config
        self.function_list = function_list
        self.tool_functions_description_list = tool_functions_description_list

        self.query = query

        self.tool_call_count = 0  

        self.plan_agent = PlanAgent(
            config=config,
            query=self.query,
            avaliable_tools_description_list=self.tool_functions_description_list,
        )
        # self.avaliable_tools_description_list = tool_functions_description_list

        self.interaction = interaction

    def outer_loop(self):
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= BEGIN QUERY SOVLING -=-=-=-=-=-=-=",
            Fore.YELLOW,
            "",
        )
        self.query.log_self()

        self.plan_agent.initial_plan_generation()
        print(summarize_plan(self.plan_agent.latest_plan.to_json()))

        self.plan_agent.plan_iterate_based_on_memory_system()

        self.now_dealing_task = self.plan_agent.latest_plan.children[0]
        # workspace_hash_id = "" 
        while self.now_dealing_task:
            recorder.change_now_task(
                self.now_dealing_task.get_subtask_id(to_str=True))
            search_method = self.inner_loop(self.now_dealing_task)
            # workspace_hash_id = search_method.get_finish_node().workspace_hash_id
            self.now_dealing_task.process_node = search_method.get_finish_node()

            self.posterior_process(self.now_dealing_task)

            working_memory_agent.register_task(self.now_dealing_task)

            if search_method.need_for_plan_refine:
                self.plan_agent.plan_refine_mode(self.now_dealing_task)
            else:
                logger.typewriter_log(
                    f"subtask submited as no need to refine the plan, continue",
                    Fore.BLUE,
                )
            self.now_dealing_task = Plan.pop_next_subtask(
                self.now_dealing_task)

        logger.typewriter_log("ALL Tasks Done", Fore.GREEN)
        return

    async def outer_loop_async(self):

        logger.typewriter_log(
            f"-=-=-=-=-=-=-= BEGIN QUERY SOVLING -=-=-=-=-=-=-=",
            Fore.YELLOW,
            "",
        )
        self.query.log_self()

        self.plan_agent.initial_plan_generation()

        print(summarize_plan(self.plan_agent.latest_plan.to_json()))

        print_data = self.plan_agent.latest_plan.to_json()
        self.interaction.init_cache(
            data=XAgentOutputData(
                tool_recommendation="",
                task_id="",
                name="",
                goal="",
                handler="",
                tool_budget=0,
                subtasks=[])
        )
        await self.interaction.update_cache(update_data={
            "node_id": uuid.uuid4().hex,
            "task_id": print_data.get("task_id", ""),
            "name": print_data.get("name", ""),
            "goal": print_data.get("goal", ""),
            "handler": print_data.get("handler", ""),
            "tool_budget": print_data.get("tool_budget", ""),
            "subtasks": print_data.get("subtask", [])
        }, status="start", current=print_data.get("task_id", ""))


        self.plan_agent.plan_iterate_based_on_memory_system()

        def rewrite_input_func(old, new):
            if not isinstance(new, dict):
                pass
            if new is None:
                return old
            else:
                goal = new.get("args", {}).get("goal", "")
                if goal != "":
                    old.data.goal = goal
                return old

        self.now_dealing_task = self.plan_agent.latest_plan.children[0]
        # workspace_hash_id = "" 
        while self.now_dealing_task:
            task_id = self.now_dealing_task.get_subtask_id(to_str=True)
            recorder.change_now_task(task_id)
            if self.interaction.interrupt:
                goal = self.now_dealing_task.data.goal
                receive_data = await self.interaction.auto_receive({"args": {"goal": goal}})
                self.now_dealing_task = rewrite_input_func(
                    self.now_dealing_task, receive_data)
            search_method = await self.inner_loop_async(self.now_dealing_task)

            self.now_dealing_task.process_node = search_method.get_finish_node()

            self.posterior_process(self.now_dealing_task)

            working_memory_agent.register_task(self.now_dealing_task)

            
            refinement_result = {
                "name": self.now_dealing_task.data.name,
                "goal": self.now_dealing_task.data.goal,
                "prior_plan_criticism": self.now_dealing_task.data.prior_plan_criticism,
                "posterior_plan_reflection": self.now_dealing_task.data.posterior_plan_reflection,
                "milestones": self.now_dealing_task.data.milestones,
                # "expected_tools": self.now_dealing_task.data.expected_tools,
                "tool_reflection": self.now_dealing_task.data.tool_reflection,
                "action_list_summary": self.now_dealing_task.data.action_list_summary,
                "task_id": task_id,
            }

            await self.interaction.update_cache(update_data=refinement_result, status="refinement", current=task_id)

            if search_method.need_for_plan_refine:
                self.plan_agent.plan_refine_mode(
                    self.now_dealing_task)
            else:
                logger.typewriter_log(
                    f"subtask submitted as no need to refine the plan, continue",
                    Fore.BLUE,
                )

            self.now_dealing_task = Plan.pop_next_subtask(
                self.now_dealing_task)

            if self.now_dealing_task is None:
                await self.interaction.update_cache(update_data=[], status="finished")
            else:
                current_task_id = self.now_dealing_task.get_subtask_id(
                    to_str=True)
                remaining_subtask = Plan.get_remaining_subtask(
                    self.now_dealing_task)
                subtask_list = []
                for todo_plan in remaining_subtask:
                    raw_data = json.loads(todo_plan.data.raw)
                    raw_data["task_id"] = todo_plan.get_subtask_id(to_str=True)
                    raw_data["inner"] = []
                    raw_data["node_id"] = uuid.uuid4().hex
                    subtask_list.append(raw_data)

                await self.interaction.update_cache(update_data=subtask_list, status="subtask", current=current_task_id)

        logger.typewriter_log("ALL Tasks Done", Fore.GREEN)
        return

    def inner_loop(self, plan: Plan, ):
        task_ids_str = plan.get_subtask_id(to_str=True)
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= Performing Task {task_ids_str} ({plan.data.name}): Begin -=-=-=-=-=-=-=",
            Fore.GREEN,
            "",
        )
        print_task_save_items(plan.data)

        agent = agent_dispatcher.dispatch(
            RequiredAbilities.tool_tree_search,
            json.dumps(plan.data.to_json(), indent=2, ensure_ascii=False),
            # avaliable_tools_description_list=self.avaliable_tools_description_list
        )

        plan.data.status = TaskStatusCode.DOING

        if self.config.rapidapi_retrieve_tool_count > 0:  
            retrieve_string = json.dumps(
                plan.to_json(), indent=2, ensure_ascii=False)
            rapidapi_tool_names, rapidapi_tool_jsons = toolserver_interface.retrieve_rapidapi_tools(
                retrieve_string, top_k=self.config.rapidapi_retrieve_tool_count)
            if rapidapi_tool_names is not None:
                function_handler.change_subtask_handle_function_enum(
                    function_handler.tool_names + rapidapi_tool_names)
            else:
                print("bug: no rapidapi tool retrieved, need to fix here")
                rapidapi_tool_jsons = []
        else:
            rapidapi_tool_jsons = []

        search_method = ReACTChainSearch()

        search_method.run(config=self.config,
                          agent=agent,
                          task_handler=self,
                          function_list=function_handler.intrinsic_tools(
                              self.config.enable_ask_human_for_help),
                          tool_functions_description_list=function_handler.avaliable_tools_description_list +
                          rapidapi_tool_jsons,
                          )

        if search_method.status == SearchMethodStatusCode.SUCCESS:
            plan.data.status = TaskStatusCode.SUCCESS
            logger.typewriter_log(
                f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Solved -=-=-=-=-=-=-=",
                Fore.GREEN,
                "",
            )
        elif search_method.status == SearchMethodStatusCode.FAIL:
            plan.data.status = TaskStatusCode.FAIL
            logger.typewriter_log(
                f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Failed -=-=-=-=-=-=-=",
                Fore.RED,
                "",
            )
        else:
            assert False, f"{plan.data.name}"
        return search_method

    async def inner_loop_async(self, plan: Plan, ):
        task_ids_str = plan.get_subtask_id(to_str=True)
        logger.typewriter_log(
            f"-=-=-=-=-=-=-= Performing Task {task_ids_str} ({plan.data.name}): Begin -=-=-=-=-=-=-=",
            Fore.GREEN,
            "",
        )
        print_task_save_items(plan.data)

        agent = agent_dispatcher.dispatch(
            RequiredAbilities.tool_tree_search,
            json.dumps(plan.data.to_json(), indent=2, ensure_ascii=False),
            # avaliable_tools_description_list=self.avaliable_tools_description_list
        )

        plan.data.status = TaskStatusCode.DOING

        if self.config.rapidapi_retrieve_tool_count > 0:  
            retrieve_string = summarize_plan(plan.to_json())
            rapidapi_tool_names, rapidapi_tool_jsons = toolserver_interface.retrieve_rapidapi_tools(
                retrieve_string, top_k=self.config.rapidapi_retrieve_tool_count)
            if rapidapi_tool_names is not None:
                function_handler.change_subtask_handle_function_enum(
                    function_handler.tool_names + rapidapi_tool_names)
            else:
                print("bug: no rapidapi tool retrieved, need to fix here")
                rapidapi_tool_jsons = []
        else:
            rapidapi_tool_jsons = []

        search_method = ReACTChainSearch()
        await search_method.run_async(config=self.config,
                                      agent=agent,
                                      task_handler=self,
                                      function_list=function_handler.intrinsic_tools(
                                          self.config.enable_ask_human_for_help),
                                      tool_functions_description_list=function_handler.avaliable_tools_description_list +
                                      rapidapi_tool_jsons,
                                      task_id=task_ids_str)

        if search_method.status == SearchMethodStatusCode.SUCCESS:
            plan.data.status = TaskStatusCode.SUCCESS
            logger.typewriter_log(
                f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Solved -=-=-=-=-=-=-=",
                Fore.GREEN,
                "",
            )
        elif search_method.status == SearchMethodStatusCode.FAIL:
            plan.data.status = TaskStatusCode.FAIL
            logger.typewriter_log(
                f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Failed -=-=-=-=-=-=-=",
                Fore.RED,
                "",
            )
        else:
            assert False, f"{plan.data.name}"
        return search_method

    def posterior_process(self, terminal_plan: Plan):

        logger.typewriter_log(
            f"-=-=-=-=-=-=-= POSTERIOR_PROCESS, working memory, summary, and reflection -=-=-=-=-=-=-=",
            Fore.BLUE,
        )
        posterior_data = get_posterior_knowledge(
            all_plan=self.plan_agent.latest_plan,
            terminal_plan=terminal_plan,
            finish_node=terminal_plan.process_node,
            tool_functions_description_list=self.tool_functions_description_list,
            config=self.config,
        )

        summary = posterior_data["summary"]
        terminal_plan.data.action_list_summary = summary

        if "reflection_of_plan" in posterior_data.keys():
            terminal_plan.data.posterior_plan_reflection = posterior_data["reflection_of_plan"]

        if "reflection_of_tool" in posterior_data.keys():
            terminal_plan.data.tool_reflection = posterior_data["reflection_of_tool"]

        # Insert the plan into vector DB
        # vector_db_interface.insert_sentence(terminal_plan.data.raw)
