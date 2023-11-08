import abc
import json
import uuid


class Node(metaclass=abc.ABCMeta):
    """
    An abstract base class that represents a node.

    Attributes:
        node_id (str): The unique identifier of the node. If None, a new UUID is generated.
        thoughts (str): The inner thoughts of the Node.
        reasoning (str): The logical reasoning of the Node.
        plan (list): The strategic plans of the Node. If None, initialize as an empty list.
        using_tools (str): The tools being used by the Node.
        is_last (bool): Whether the Node is the last one in a series of Nodes.
    """

    def __init__(self, thoughts: str,
                 reasoning: str,
                 plan: list,
                 using_tools: str,
                 is_last: bool = False,
                 node_id: str = None):
        """
        Constructs a new Node instance.

        Args:
            thoughts (str): The inner thoughts of the Node.
            reasoning (str): The logical reasoning of the Node.
            plan (list): The strategic plans of the Node. If None, initialize as an empty list.
            using_tools (str): The tools being used by the Node.
            is_last (bool, optional): Whether the Node is the last one in a series of Nodes. Defaults to False.
            node_id (str, optional): The unique identifier of the Node. If None, a new UUID is generated. Defaults to None.
        """
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
        """
        Converts the Node to a dictionary.

        Returns:
            dict: The dictionary representation of the Node.
        """
        return {
            "node_id": self.node_id,
            "thoughts": self.thoughts,
            "reasoning": self.reasoning,
            "plan": self.plan,
            "using_tools": self.using_tools,
            "is_last": self.is_last,
        }

    def to_json(self):
        """
        Converts the Node to a JSON string.

        Returns:
            str: The JSON string representation of the Node.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        """
        Creates a new Node instance from a JSON string.

        Args:
            json_data (str): A JSON string representing a Node.

        Returns:
            Node: A new Node instance created from the JSON data.
        """
        return cls(**json_data)