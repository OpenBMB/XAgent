import abc
import json
import uuid
from XAgentServer.models.node import Node


class Subtask(metaclass=abc.ABCMeta):
    """Abstract base class for all subtask types.

    This class provides the basic properties and methods needed for all subtask types. 
    It should be subclassed for each specific subtask type, so that each subclass
    can provide its own specific functionality.

    Attributes:
        name: A string that represents the name of the subtask.
        goal: A string that represents the goal of the subtask.
        handler: A string that represents the handler of the subtask.
        tool_budget: An integer that represents the budget for the tools.
        task_id: A string that represents the id of the subtask.
        milestones: A list that holds the milestones of the subtask.
        expected_tools: A list that holds the expected tools of the subtask.
        exceute_status: A string that represents the execution status of the subtask.
        prior_plan_criticsim: A string that represents the prior plan criticsim of the subtask.
        inner: A list of inner nodes of the subtask.
        node_id: A string that represents the node id of the subtask. It is generated as a 
                 UUID hex string if not explicitly provided at instantiation time.
        refinement: A dict that holds the refinement information.
    """

    def __init__(self, 
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
        """Convert the subtask to a dictionary.

        Returns:
            A dictionary representation of the subtask instance.
        """
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
                node.to_dict() if isinstance(node, Node) else node for node in self.inner
            ]
        }

    def to_json(self):
        """Convert the subtask to a JSON.

        Returns:
            A JSON string representation of the subtask instance.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        """Create a new subtask instance from a JSON string.

        Args:
            json_data: The JSON string that represents a subtask.

        Returns:
            A new Subtask instance.

        Raises:
            TypeError: If the json_data argument is not a dictionary.
        """
        if not isinstance(json_data, dict):
            raise TypeError('json_data must be a dictionary.')
        return cls(**json_data)