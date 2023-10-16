import os
from copy import deepcopy
import abc
from typing import List

from XAgent.message_history import MessageHistory
from XAgent.utils import ToolCallStatusCode, TaskStatusCode



class Node(metaclass = abc.ABCMeta):
    def __init__(self):
        pass


class ToolNode(Node):
    def __init__(self):

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
        data = []
        now_node = self
        while now_node.father != None:
            data = [now_node.data] + data
            now_node = now_node.father
        return data

    def to_json(self):
        data = deepcopy(self.data)
        data["tool_status_code"] = data["tool_status_code"].name
        return data

    def get_depth(self):
        if self.father == None:
            return 0
        return self.father.get_depth() + 1
    
    def get_subtree_size(self):
        if self.children == []:
            return 1
        now_size = 1
        for child in self.children:
            now_size += child.get_subtree_size()
        return now_size



