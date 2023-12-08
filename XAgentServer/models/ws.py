"""
This module contains the class XAgentOutputData which is responsible for data handling 
in the XAgent Server models.
"""

import abc
import json
import uuid

from XAgentServer.models.subtask import Subtask

class XAgentOutputData(metaclass=abc.ABCMeta):
    """
    A class used to handle the output data for XAgent. 

    Attributes
    ----------
    task_id : str
        Unique identifier for the task.
    name : str
        Name of the task.
    goal : str
        Goal description of the task.
    handler : str
        Handler for the task.
    tool_budget : int
        Budget allotted for the tool.
    tool_recommendation : str
        Recommendation of the tool used in the task.
    subtasks : list[Subtask], optional
        List of subtasks involved in the task.
    node_id : str, optional
        Unique identifier for the node, generated if one is not provided. 

    Methods
    -------
    to_dict():
        Returns a dictionary representation of the class object.
    to_json():
        Returns a JSON formatted string representation of the class object.
    from_json(json_data: dict) -> XAgentOutputData:
        Returns a class object with attributes set by the json data. 
    update(update_data: dict) -> XAgentOutputData:
        Updates the class object with the provided data and returns the updated object. 

    """

    def __init__(self, task_id: str,
                 name: str,
                 goal: str,
                 handler: str,
                 tool_budget: int,
                 tool_recommendation: str,
                 subtasks: None,
                 node_id: str = None):
        """
        Constructs all the necessary attributes for the XAgentOutputData object.

        Parameters:
            task_id (str): Unique identifier for the task.
            name (str): Name of the task.
            goal (str): Goal description of the task.
            handler (str): Handler for the task.
            tool_budget (int): Budget allotted for tool.
            tool_recommendation (str): Recommendation of the tool used.
            subtasks (None | list[Subtask]): List of subtasks involved in the task. Defaults to an empty list.
            node_id (str): Unique identifier for the node. Defaults to uuid set by system.
        """
        
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
        """
        Converts the XAgentOutputData object to a dictionary.

        Returns:
            dict: A dictionary representation of the XAgentOutputData object.
        """
        
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
        """
        Converts the XAgentOutputData object to a json formatted string.

        Returns:
            str: A json formatted string representation of the XAgentOutputData object.
        """
        
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        """
        Creates a new XAgentOutputData object from json data.
        
        Args:
            json_data (dict): A dictionary of attributes of XAgentOutputData object.
            
        Returns:
            XAgentOutputData: A new instance of XAgentOutputData.
        """
        return cls(**json_data)

    def update(self, update_data: dict):
        """
        Updates the XAgentOutputData object with the provided data.
        
        Args:
            update_data (dict): A dictionary of attributes of XAgentOutputData object to update.
            
        Returns:
            XAgentOutputData: The updated instance of XAgentOutputData.
        """
        
        for k, v in update_data.items():
            setattr(self, k, v)
        return self