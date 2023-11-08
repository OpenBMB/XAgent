"""
"""

import abc
import json


class SharedInteractionBase(metaclass=abc.ABCMeta):
    """
    An abstract base class that defines shared interactions.
    This class is used as a base class for creating different types of shared interactions.
    
    Attributes:
        interaction_id: A string representing the interaction id.
        user_name: A string value representing the username of the user.
        create_time: A string value representing the time of creation.
        update_time: A string value representing the time the interaction was last updated.
        description: A string value representing the description of the interaction.
        agent: A string value representing the agent. Default is an empty string.
        mode: A string value representing the mode. Default is an empty string.
        is_deleted: A boolean value indicating if the interaction is deleted or not. Default is False.
        star: An integer value showing the star rating of the interaction. Default is 0.
        record_dir: A string value representing the directory of the recorded interaction. Default is an empty string.
    """

    def __init__(self, interaction_id: str, user_name: str, create_time: str, update_time: str, description: str,
                 agent: str = "", mode: str = "", is_deleted: bool = False, star: int = 0, record_dir: str = ""):
        self.interaction_id = interaction_id
        self.user_name = user_name
        self.create_time = create_time
        self.update_time = update_time
        self.description = description
        self.agent = agent
        self.mode = mode
        self.is_deleted = is_deleted
        self.star = star
        self.record_dir = record_dir

    def to_dict(self, include=None, exclude=None):
        """
        Converts the shared interaction object to a dictionary.
        
        Args:
            include: A list of keys to include in the returned dictionary. Default is None.
            exclude: A list of keys to exclude from the returned dictionary. Default is None.
        
        Returns:
            A dictionary containing the interaction data.
        """
        
        data = {
            "interaction_id": self.interaction_id,
            "user_name": self.user_name,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "description": self.description,
            "agent": self.agent,
            "mode": self.mode,
            "is_deleted": self.is_deleted,
            "star": self.star,
            "record_dir": self.record_dir,
        }
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}
        return data
    
    def to_json(self):
        """
        Converts the shared interaction object to a JSON string.
        
        Returns:
            A JSON formatted string representation of the shared interaction.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_db(cls, interaction):
        """
        Builds a new SharedInteractionBase instance from the input interaction.
        
        Args:
            interaction: An interaction instance fetched from the database.
        
        Returns:
            A new instance of SharedInteractionBase built from input interaction.
        """
        
        return cls(
            interaction.interaction_id,
            interaction.user_name,
            interaction.create_time,
            interaction.update_time,
            interaction.description,
            interaction.agent,
            interaction.mode,
            interaction.is_deleted,
            interaction.star,
            interaction.record_dir,
        )