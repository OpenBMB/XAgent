import abc
import json
import uuid

from XAgentServer.models.subtask import Subtask

class XAgentOutputData(metaclass=abc.ABCMeta):
    def __init__(self, task_id: str,
                 name: str,
                 goal: str,
                 handler: str,
                 tool_budget: int,
                 tool_recommendation: str,
                 subtasks: None,
                 node_id: str = None):
        if subtasks is None:
            subtasks = []
        self.name = name
        self.goal = goal
        self.handler = handler
        self.tool_budget = tool_budget
        self.task_id = task_id
        self.subtasks = subtasks
        self.tool_recommendation = tool_recommendation
        if node_id is None:
            self.node_id = uuid.uuid4().hex
        else:
            self.node_id = node_id

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "node_id": self.node_id,
            "name": self.name,
            "goal": self.goal,
            "handler": self.handler,
            "tool_budget": self.tool_budget,
            "subtasks": [
                subtask.to_dict() for subtask in self.subtasks
            ],
            "tool_recommendation": self.tool_recommendation
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)

    def update(self, update_data: dict):
        for k, v in update_data.items():
            setattr(self, k, v)
        return self
