import abc
import json
import uuid
from XAgentServer.models.node import Node


class Subtask(metaclass=abc.ABCMeta):
    def __init__(
        self,
        name: str = "",
        goal: str = "",
        handler: str = "",
        tool_budget: int = 0,
        milestones: list = [],
        expected_tools: list = [],
        exceute_status: str = "",
        prior_plan_criticsim: str = "",
        task_id: str = "",
        inner: list = None,
        node_id: str = None,
        refinement: dict = None,
    ):
        if inner is None:
            inner = []
        self.name = name
        self.goal = goal
        self.handler = handler
        self.tool_budget = tool_budget
        self.task_id = task_id
        self.milestones = milestones
        self.expected_tools = expected_tools
        self.exceute_status = exceute_status
        self.prior_plan_criticsim = prior_plan_criticsim
        self.inner = inner
        self.refinement = refinement
        if node_id is None:
            self.node_id = uuid.uuid4().hex
        else:
            self.node_id = node_id

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "task_id": self.task_id,
            "name": self.name,
            "goal": self.goal,
            "handler": self.handler,
            "tool_budget": self.tool_budget,
            "milestones": self.milestones,
            "expected_tools": self.expected_tools,
            "exceute_status": self.exceute_status,
            "prior_plan_criticsim": self.prior_plan_criticsim,
            "refinement": self.refinement,
            "inner": [
                node.to_dict() if isinstance(node, Node) else node
                for node in self.inner
            ],
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)
