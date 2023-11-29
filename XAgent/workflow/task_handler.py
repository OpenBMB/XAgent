import json
import uuid

from colorama import Fore

from XAgent.inner_loop_search_algorithms.ReACT import ReACTChainSearch
from XAgent.agent.summarize import summarize_plan
from XAgent.utils import (RequiredAbilities, SearchMethodStatusCode,
                          TaskSaveItem, TaskStatusCode)
from XAgent.ai_functions import function_manager
from XAgent.core import XAgentCoreComponents, XAgentParam
from XAgentServer.enums.status import StatusEnum
from .plan_exec import Plan, PlanAgent
from .reflection import get_posterior_knowledge


class TaskHandler():
    """
    Main class for handling tasks within the XAgent system.

    Attributes:
        config: The configuration settings for the task handler.
        function_list: List of available functions for the current task.
        tool_functions_description_list: List of available tool functions description for the current task.
        query: The current task of this agent.
        tool_call_count: Variable for tracking the count of tool calls.
        plan_agent: Instance of PlanAgent class which is used for generating and handling plan for the current task.
        interaction: Instance of XAgentInteraction class for interacting with outer world.
    """

    def __init__(self,
                 xagent_core: XAgentCoreComponents,
                 xagent_param: XAgentParam):
        """
        Initializes TaskHandler with the provided input parameters.

        Args:
            xaagent_core (XAgentCoreComponents): Instance of XAgentCoreComponents class.
            xaagent_param (XAgentParam): Instance of XAgentParam class.
        """
        self.xagent_core = xagent_core
        self.xagent_param = xagent_param
        self.config = xagent_param.config
        self.function_list = self.xagent_core.function_list
        self.tool_functions_description_list = self.xagent_core.tool_functions_description_list
        self.query = self.xagent_param.query
        self.tool_call_count = 0
        self.plan_agent = PlanAgent(
            config=self.config,
            query=self.query,
            avaliable_tools_description_list=self.tool_functions_description_list,
        )
        self.logger = self.xagent_core.logger
        # self.avaliable_tools_description_list = tool_functions_description_list

        self.interaction = self.xagent_core.interaction
        self.recorder = self.xagent_core.recorder
        self.agent_dispatcher = self.xagent_core.agent_dispatcher
        self.function_list = self.xagent_core.function_list
        self.function_handler = self.xagent_core.function_handler
        self.toolserver_interface = self.xagent_core.toolserver_interface
        self.working_memory_agent = self.xagent_core.working_memory_agent
        self.now_dealing_task = None

    def outer_loop(self):
        """
        Executes the main sequence of tasks in the outer loop.

        Raises:
            AssertionError: Raised if a not expected status is encountered while handling the plan.

        Returns:
            None
        """
        self.logger.typewriter_log(
            f"-=-=-=-=-=-=-= BEGIN QUERY SOVLING -=-=-=-=-=-=-=",
            Fore.YELLOW,
            "",
        )
        self.query.log_self()

        self.plan_agent.initial_plan_generation(
            agent_dispatcher=self.agent_dispatcher)

        print(summarize_plan(self.plan_agent.latest_plan.to_json()))

        print_data = self.plan_agent.latest_plan.to_json()
        self.interaction.insert_data(data={
            "task_id": print_data.get("task_id", ""),
            "name": print_data.get("name", ""),
            "goal": print_data.get("goal", ""),
            "handler": print_data.get("handler", ""),
            "tool_budget": print_data.get("tool_budget", ""),
            "subtasks": [{**sub, "inner": []} for sub in print_data.get("subtask", [])]
        }, status=StatusEnum.START, current=print_data.get("task_id", ""))

        self.plan_agent.plan_iterate_based_on_memory_system()

        def rewrite_input_func(old, new):
            if new is None or not isinstance(new, dict):
                return old, False
            else:
                goal = new.get("goal", "")
                if goal != "":
                    old = goal
                return old, True

        self.now_dealing_task = self.plan_agent.latest_plan.children[0]
        # workspace_hash_id = ""
        while self.now_dealing_task:
            task_id = self.now_dealing_task.get_subtask_id(to_str=True)
            self.recorder.change_now_task(task_id)
            if self.interaction.interrupt:
                goal = self.now_dealing_task.data.goal
                receive_data = self.interaction.receive(
                    {"args": {"goal": goal}})
                new_intput, flag = rewrite_input_func(
                    self.now_dealing_task, receive_data)

                if flag:
                    self.logger.typewriter_log(
                        "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                        Fore.GREEN,
                        "",
                    )
                    self.logger.typewriter_log(
                        "goal: ",
                        Fore.YELLOW,
                        f"{new_intput}",
                    )
                    self.now_dealing_task.data.goal = new_intput
                    self.logger.typewriter_log(
                        "-=-=-=-=-=-=-= USER INPUT -=-=-=-=-=-=-=",
                        Fore.GREEN,
                        "",
                    )

            search_method = self.inner_loop(self.now_dealing_task)

            self.now_dealing_task.process_node = search_method.get_finish_node()

            self.posterior_process(self.now_dealing_task)

            self.working_memory_agent.register_task(self.now_dealing_task)

            self.xagent_core.print_task_save_items(self.now_dealing_task.data)

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

            self.interaction.insert_data(
                data=refinement_result, status=StatusEnum.REFINEMENT, current=task_id)
            if search_method.need_for_plan_refine:
                self.plan_agent.plan_refine_mode(
                    self.now_dealing_task, self.toolserver_interface, self.agent_dispatcher)
            else:
                self.logger.typewriter_log(
                    "subtask submitted as no need to refine the plan, continue",
                    Fore.BLUE,
                )

            self.now_dealing_task = Plan.pop_next_subtask(
                self.now_dealing_task)

            if self.now_dealing_task is None:
                self.interaction.insert_data(
                    data=[], status=StatusEnum.FINISHED, current="")
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

                self.interaction.insert_data(
                    data=subtask_list, status=StatusEnum.SUBTASK, current=current_task_id)

        self.logger.typewriter_log("ALL Tasks Done", Fore.GREEN)
        return

    def inner_loop(self, plan: Plan, ):
        """
        Generates search plan and process it for the current task.

        Args:
            plan (Plan): The plan to be processed.

        Raises:
            AssertionError: Raised if a not expected status is encountered while handling the plan.

        Returns:
            ReACTChainSearch: Instance of the search plan.
        """
        task_ids_str = plan.get_subtask_id(to_str=True)
        self.logger.typewriter_log(
            f"-=-=-=-=-=-=-= Performing Task {task_ids_str} ({plan.data.name}): Begin -=-=-=-=-=-=-=",
            Fore.GREEN,
            "",
        )
        self.xagent_core.print_task_save_items(plan.data)

        agent = self.agent_dispatcher.dispatch(
            RequiredAbilities.tool_tree_search,
            json.dumps(plan.data.to_json(), indent=2, ensure_ascii=False),
            # avaliable_tools_description_list=self.avaliable_tools_description_list
        )

        plan.data.status = TaskStatusCode.DOING

        if self.config.rapidapi_retrieve_tool_count > 0:
            retrieve_string = summarize_plan(plan.to_json())
            rapidapi_tool_names, rapidapi_tool_jsons = self.toolserver_interface.retrieve_rapidapi_tools(
                retrieve_string, top_k=self.config.rapidapi_retrieve_tool_count)
            if rapidapi_tool_names is not None:
                self.function_handler.change_subtask_handle_function_enum(
                    self.function_handler.tool_names + rapidapi_tool_names)
                self.function_handler.avaliable_tools_description_list += rapidapi_tool_jsons
            else:
                print("bug: no rapidapi tool retrieved, need to fix here")

        search_method = ReACTChainSearch(
            xagent_core_components=self.xagent_core,)

        arguments = function_manager.get_function_schema('action_reasoning')[
            'parameters']
        search_method.run(config=self.config,
                          agent=agent,
                          arguments=arguments,
                          functions=self.function_handler.intrinsic_tools(
                              self.config.enable_ask_human_for_help),
                          task_id=task_ids_str,
                          now_dealing_task=self.now_dealing_task,
                          plan_agent=self.plan_agent)

        if search_method.status == SearchMethodStatusCode.SUCCESS:
            plan.data.status = TaskStatusCode.SUCCESS
            self.logger.typewriter_log(
                f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Solved -=-=-=-=-=-=-=",
                Fore.GREEN,
                "",
            )
        elif search_method.status == SearchMethodStatusCode.FAIL:
            plan.data.status = TaskStatusCode.FAIL
            self.logger.typewriter_log(
                f"-=-=-=-=-=-=-= Task {task_ids_str} ({plan.data.name}): Failed -=-=-=-=-=-=-=",
                Fore.RED,
                "",
            )
        else:
            assert False, f"{plan.data.name}"
        return search_method

    def posterior_process(self, terminal_plan: Plan):
        """
        Performs the post-processing steps on the terminal plan including extraction of posterior knowledge
        and updating the plan data.

        Args:
            terminal_plan (Plan): The terminal plan after completion of all inner loop tasks.

        Returns:
            None
        """

        self.logger.typewriter_log(
            "-=-=-=-=-=-=-= POSTERIOR_PROCESS, working memory, summary, and reflection -=-=-=-=-=-=-=",
            Fore.BLUE,
        )
        posterior_data = get_posterior_knowledge(
            all_plan=self.plan_agent.latest_plan,
            terminal_plan=terminal_plan,
            finish_node=terminal_plan.process_node,
            tool_functions_description_list=self.tool_functions_description_list,
            config=self.config,
            agent_dispatcher=self.agent_dispatcher,
        )

        summary = posterior_data["summary"]
        terminal_plan.data.action_list_summary = summary

        if "reflection_of_plan" in posterior_data.keys():
            terminal_plan.data.posterior_plan_reflection = posterior_data["reflection_of_plan"]

        if "reflection_of_tool" in posterior_data.keys():
            terminal_plan.data.tool_reflection = posterior_data["reflection_of_tool"]

        # Insert the plan into vector DB
        # vector_db_interface.insert_sentence(terminal_plan.data.raw)
