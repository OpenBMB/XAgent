import os
from copy import deepcopy
import abc
from typing import List

from XAgent.message_history import MessageHistory
from XAgent.utils import ToolCallStatusCode, TaskStatusCode


class Node(metaclass = abc.ABCMeta):
    """
    Abstract class representing a generic node in the XAgent's data structure.

    This class uses the abc module to denote it as an abstract base class.
    Other classes should inherit from this class to implement specific types of nodes.
    """
    def __init__(self):
        """
        Initialize a new node.

        As an abstract class, Node does not have any implementation details.
        """
        pass


class ToolNode(Node):
    """
    Class representing a tool node in the XAgent's data structure.
    
    A tool node has a “father” that represents its parent node, "children" that represents its child nodes, 
    and “data” containing metadata about node's status, command, tool's output, and thoughts properties.
    It also carries a message history and a workspace hash id.

    """

    def __init__(self):
        """
        Initialize a new tool node.

        Setup father, children, expand_num, data, history, workspace_hash_id attributes for the instance.
        """

        self.father: ToolNode = None
        self.children: list[ToolNode] = []
        self.expand_num = 0
        self.data = {
            "content": "",
            "thoughts": {
                "properties": {
                    "thought": "",
                    "reasoning": "",
                    "plan": "",
                    "criticism": "",
                },
            },
            "command": {
                "properties": {
                    "name": "",
                    "args": "",
                },
            },
            "tool_output": "",
            "tool_status_code": ToolCallStatusCode.TOOL_CALL_SUCCESS,
        }
        self.history: MessageHistory = MessageHistory()
        self.workspace_hash_id = ""

    @property
    def process(self):
        """
        Generate a list of data from current node up to root node.

        Returns:
            data (List): A list of data from current node up to root node.
        """

        data = []
        now_node = self
        while now_node.father != None:
            data = [now_node.data] + data
            now_node = now_node.father
        return data

    def to_json(self):
        """
        Convert the data attribute of the instance to a JSON-compatible format.

        Returns:
            data (Dict): The data attribute of the instance in a JSON-compatible format.
        """

        data = deepcopy(self.data)
        data["tool_status_code"] = data["tool_status_code"].name
        return data

    def get_depth(self):
        """
        Calculate the depth of current node in the tree.

        Returns:
            depth (int): The depth of the node. Return 0 if the node is a root node.
        """
        
        if self.father == None:
            return 0
        return self.father.get_depth() + 1
    
    def get_subtree_size(self):
        """
        Calculate the size of the subtree rooted at current node.

        Returns:
            size (int): The size of the subtree rooted at current node.
        """
        
        if self.children == []:
            return 1
        now_size = 1
        for child in self.children:
            now_size += child.get_subtree_size()
        return now_size