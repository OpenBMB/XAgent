import abc
import json
import uuid


class Node(metaclass=abc.ABCMeta):

    def __init__(self, thoughts: str,
                 reasoning: str,
                 plan: list,
                 using_tools: str,
                 is_last: bool = False,
                 node_id: str = None):
        if plan is None:
            plan = []
        if node_id is None:
            self.node_id = uuid.uuid4().hex
        else:
            self.node_id = node_id
        self.thoughts = thoughts
        self.reasoning = reasoning
        self.plan = plan
        self.using_tools = using_tools
        self.is_last = is_last

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "thoughts": self.thoughts,
            "reasoning": self.reasoning,
            "plan": self.plan,
            "using_tools": self.using_tools,
            "is_last": self.is_last,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)