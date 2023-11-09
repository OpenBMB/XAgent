"""
"""

import abc
import json


class InteractionBase(metaclass=abc.ABCMeta):
    """
    Base class for interaction objects.

    Attributes:
        interaction_id (str): Unique identifier of the interaction.
        user_id (str): Identifier of the user who initiated the interaction.
        create_time (str): Time at which the interaction was created.
        description (str): A brief description of the interaction.
        agent (str, optional): The agent involved in the interaction. Default is an empty string.
        mode (str, optional): Mode of the interaction. Default is an empty string.
        file_list (list, optional): List of files associated with the interaction. Default is an empty list.
        recorder_root_dir (str, optional): Root directory of the recorder. Default is an empty string.
        status (str, optional): Status of the interaction. Default is an empty string.
        message (str, optional): Message associated with the interaction. Default is an empty string.
        current_step (str, optional): Current step of the interaction. Default is an empty string.
        update_time (str, optional): Time at which the interaction was last updated. Default is an empty string.
        is_deleted (bool, optional): Flag indicating whether the interaction has been deleted. Default is False.
    """
    def __init__(self,
                interaction_id: str,
                user_id: str,
                create_time: str,
                description: str,
                agent: str = "",
                mode: str = "",
                file_list: list = [],
                recorder_root_dir: str = "",
                status: str = "",
                message: str = "",
                current_step: str = "",
                update_time: str = "",
                is_deleted: bool = False,
                ):

        """Initializes the InteractionBase instance."""

        self.interaction_id = interaction_id
        self.user_id = user_id
        self.create_time = create_time
        self.description = description
        self.agent = agent
        self.mode = mode
        self.file_list = file_list
        self.recorder_root_dir = recorder_root_dir
        self.status = status
        self.message = message
        self.current_step = current_step
        self.update_time = update_time
        self.is_deleted = is_deleted

    def to_dict(self, include=None, exclude=None):
        """
        Converts the InteractionBase instance to a dictionary.

        Args:
            include (list, Optional): List of keys to be included in the dictionary.
            exclude (list, Optional): List of keys to be excluded from the dictionary.

        Returns:
            data (dict): Dictionary representation of the InteractionBase instance.
        """

        data = {
            "interaction_id": self.interaction_id,
            "user_id": self.user_id,
            "create_time": self.create_time,
            "description": self.description,
            "agent": self.agent,
            "mode": self.mode,
            "file_list": self.file_list,
            "recorder_root_dir": self.recorder_root_dir,
            "status": self.status,
            "message": self.message,
            "current_step": self.current_step,
            "update_time": self.update_time,
            "is_deleted": self.is_deleted,
        }
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}
        return data
    
    def to_json(self):
        """
        Converts the InteractionBase instance to a JSON string.

        Returns:
            string: JSON representation of the InteractionBase instance.
        """

        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_data):
        """
        Creates an InteractionBase instance from a JSON string.

        Args:
            json_data (str): JSON string representation of the InteractionBase instance.

        Returns:
            InteractionBase: New InteractionBase instance.
        """

        return cls(**json_data)
    
    @classmethod
    def from_db(cls, interaction):
        """
        Creates an InteractionBase instance from a database object.

        Args:
            interaction (Interaction): Object representing the interaction in the database.

        Returns:
            InteractionBase: New InteractionBase instance.
        """

        return cls(interaction.interaction_id,
                    interaction.user_id,
                    interaction.create_time,
                    interaction.description,
                    interaction.agent,
                    interaction.mode,
                    interaction.file_list,
                    interaction.recorder_root_dir,
                    interaction.status,
                    interaction.message,
                    interaction.current_step,
                    interaction.update_time,
                    interaction.is_deleted,
                    )