import abc
import json
from typing import Union


class InteractionParameter(metaclass=abc.ABCMeta):
    """
    Abstract base class for defining an interaction object with relevant parameters.

    Attributes:
        interaction_id (str): The unique identifier for the interaction.
        parameter_id (str): The unique identifier for the parameter.
        args (Union[str, dict, None]): The arguments used for the interaction, may be None.
    """

    def __init__(self,
                 interaction_id: str,
                 parameter_id: str,
                 args: Union[str, dict, None] = None):
        """
        Initialize an instance of the InteractionParameter class.

        Args:
            interaction_id (str): The unique identifier for the interaction.
            parameter_id (str): The unique identifier for the parameter.
            args (Union[str, dict, None]): The arguments used for the interaction, may be None.
        """
        self.interaction_id = interaction_id
        self.args = args
        self.parameter_id = parameter_id

    def to_dict(self):
        """
        Convert the InteractionParameter instance to a dictionary.

        Returns:
            dict: A dictionary representation of the InteractionParameter instance.
        """
        return {
            "interaction_id": self.interaction_id,
            "parameter_id": self.parameter_id,
            "args": self.args,
        }

    def to_json(self):
        """
        Convert the InteractionParameter instance to a JSON-formatted string.

        Returns:
            str: A JSON-formatted string representing the InteractionParameter instance.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        """
        Create an instance of InteractionParameter from JSON-formatted data.

        Args:
            json_data (str): A JSON-formatted string representing an InteractionParameter instance.

        Returns:
            InteractionParameter: An instance of InteractionParameter created from the given JSON data.
        """
        return cls(**json_data)

    @classmethod
    def from_db(cls, interaction):
        """
        Create an instance of InteractionParameter from a database entry.

        Args:
            interaction (Object): An object representing a row from a interactions table in a database.

        Returns:
            InteractionParameter: An instance of InteractionParameter created from the interaction database entry.
        """
        return cls(interaction.interaction_id,
                   interaction.parameter_id,
                   interaction.args)