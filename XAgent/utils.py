from enum import Enum, unique
import abc
from colorama import Fore, Style
import json
import requests
from dataclasses import dataclass, field
from typing import List, Dict
import tiktoken
from XAgent.config import CONFIG


encoding = tiktoken.encoding_for_model(CONFIG.default_completion_kwargs["model"])


def get_token_nums(text: str) -> int:
    return len(encoding.encode(text))


def clip_text(text: str, max_tokens: int = None, clip_end=False) -> str | int:
    encoded = encoding.encode(text)
    decoded = encoding.decode(
        encoded[:max_tokens] if clip_end else encoded[-max_tokens:]
    )
    if len(decoded) != len(text):
        decoded = decoded + "`wrapped`" if clip_end else "`wrapped`" + decoded
    return decoded, len(encoded)


@unique
class LLMStatusCode(Enum):
    SUCCESS = 0
    ERROR = 1


@unique
class ToolCallStatusCode(Enum):
    TOOL_CALL_FAILED = -1
    TOOL_CALL_SUCCESS = 0
    FORMAT_ERROR = 1
    HALLUCINATE_NAME = 2
    OTHER_ERROR = 3
    TIMEOUT_ERROR = 4
    TIME_LIMIT_EXCEEDED = 5
    SERVER_ERROR = 6

    SUBMIT_AS_SUCCESS = 7
    SUBMIT_AS_FAILED = 8

    def __str__(self):
        return self.__class__.__name__ + ": " + self.name


@unique
class PlanOperationStatusCode(Enum):
    MODIFY_SUCCESS = 0
    MODIFY_FORMER_PLAN = 1
    PLAN_OPERATION_NOT_FOUND = 2
    TARGET_SUBTASK_NOT_FOUND = 3
    PLAN_REFINE_EXIT = 4
    OTHER_ERROR = 5


@unique
class SearchMethodStatusCode(Enum):
    DOING = 0
    SUCCESS = 1
    FAIL = 2
    HAVE_AT_LEAST_ONE_ANSWER = 3


@unique
class TaskStatusCode(Enum):
    TODO = 0
    DOING = 1
    SUCCESS = 2
    FAIL = 3
    SPLIT = 4


@unique
class RequiredAbilities(Enum):
    tool_tree_search = 0
    plan_generation = 1
    plan_refinement = 2
    task_evaluator = 3
    summarization = 4
    reflection = 5


@dataclass
class AgentRole:
    name: str = "Auto-GPT"
    prefix: str = "You are an expert of using multiple tools to handle diverse real-world user queries."


@dataclass
class TaskSaveItem:
    name: str = ""
    goal: str = ""
    # handler: str = "new_agent"
    # tool_budget: int = 10
    milestones: List[str] = field(default_factory=lambda: [])
    # expected_tools: List[str] = field(default_factory=lambda: [])
    prior_plan_criticism: str = ""

    status: TaskStatusCode = TaskStatusCode.TODO

    action_list_summary: str = ""
    posterior_plan_reflection: List[str] = field(default_factory=lambda: [])
    tool_reflection: List[Dict[str, str]] = field(default_factory=lambda: [])

    def load_from_json(self, function_output_item):
        if "subtask name" in function_output_item.keys():
            self.name = function_output_item["subtask name"]
        else:
            print(f"field subtask name not exist")

        if (
            "goal" in function_output_item.keys()
            and "goal" in function_output_item["goal"].keys()
        ):
            self.goal = function_output_item["goal"]["goal"]
        else:
            print(f"field goal.goal not exist")

        if (
            "goal" in function_output_item.keys()
            and "criticism" in function_output_item["goal"].keys()
        ):
            self.prior_plan_criticism = function_output_item["goal"]["criticism"]
        else:
            print(f"field goal.criticism not exist")

        # if "handler" in function_output_item.keys():
        #     self.handler=function_output_item["handler"]
        # else:
        #     print(f"field handler not exist")

        # if "tool_budget" in function_output_item.keys():
        #     self.tool_budget=function_output_item["tool_budget"]
        # else:
        #     print(f"field tool_budget not exist")

        if "milestones" in function_output_item.keys():
            self.milestones = function_output_item["milestones"]
        # if "expected_tools" in function_output_item.keys():
        #     self.expected_tools = function_output_item["expected_tools"]

    def to_json(self, posterior=False):
        json_data = {
            "name": self.name,
            "goal": self.goal,
            # "handler": self.handler,
            # "tool_budget": self.tool_budget,
            "prior_plan_criticsim": self.prior_plan_criticism,
            "milestones": self.milestones,
            # "expected_tools": self.expected_tools,
            "exceute_status": self.status.name,
        }
        if posterior:
            if self.action_list_summary != "":
                json_data["action_list_summary"] = self.action_list_summary
            # if self.posterior_plan_reflection != []:
            #     json_data["posterior_plan_reflection"] = self.posterior_plan_reflection
            # if self.tool_reflection != []:
            #     json_data["tool_reflection"] = self.tool_reflection
        return json_data

    @property
    def raw(self) -> str:
        return json.dumps(self.to_json(posterior=True), indent=2, ensure_ascii=False)


class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractSingleton(abc.ABC, metaclass=Singleton):
    """
    Abstract singleton class for ensuring only one instance of a class.
    """
