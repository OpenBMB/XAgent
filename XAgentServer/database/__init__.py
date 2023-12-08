from typing import Union

from sqlalchemy.orm import Session

from XAgentServer.envs import XAgentServerEnv
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.shared_interaction import SharedInteractionBase


class UserBaseInterface:
    """
    Base Interface for interacting with User related data in a database.

    Attributes:
        db : Instance of SQLAlchemy's Session class. Provide a connection to a database.
    """

    def __init__(self, envs: XAgentServerEnv) -> None:
        """
        Initialize the UserBaseInterface.

        Args:
            envs (XAgentServerEnv): The environment variables of the XAgentServer.
        """

        pass

    def register_db(self, db: Session):
        """
        Registers a session with the database.

        Args:
            db (Session): Instance of SQLAlchemy's Session class. Provide a connection to a database.
        """
        self.db = db

    def init(self):
        """
        Initialization function, to be implemented by subclasses.
        """
        raise NotImplementedError

    def get_user_list(self) -> list:
        """
        Returns a list of users.

        Returns:
            list: A list of users.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def get_user_dict_list(self):
        """
        Returns a list of user dictionaries.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def get_user(self, user_id: Union[str, None] = None, email: Union[str, None] = None):
        """
        Query a user either by user_id or by email.

        Args:
            user_id (Union[str, None], optional): The user's id. If not provided, it checks the email.
            email (Union[str, None], optional): The user's email. If not provided, it checks the user_id.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def user_is_exist(self, user_id: Union[str, None] = None, email: Union[str, None] = None):
        """
        Check whether a user with a given user_id or email exists.

        Args:
            user_id (Union[str, None], optional): The user's id. If not provided, it checks the email.
            email (Union[str, None], optional): The user's email. If not provided, it checks the user_id.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def token_is_exist(self, user_id: str, token: Union[str, None] = None):
        """
        Check whether a user with a given Auth token and user_id exists.

        Args:
            user_id (str): The user's id.
            token (Union[str, None], optional): The user's Auth token.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def user_is_valid(self,
                      user_id: Union[str, None] = None,
                      email: Union[str, None] = None,
                      token: Union[str, None] = None):
        """
        Check whether a user is valid either by user_id and token or by email and token.

        Args:
            user_id (Union[str, None], optional): The user's id. If not provided, it checks the email.
            email (Union[str, None], optional): The user's email. If not provided, it checks the user_id.
            token (Union[str, None], optional): The user's Auth token.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def add_user(self, user_dict: dict):
        """
        Add a user using a dictionary of user details.

        Args:
            user_dict (dict): Contains user details.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def update_user(self, user):
        """
        Update a user's details.

        Args:
            user: A user object with updated details.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError


class InteractionBaseInterface:
    """
    Base Interface for interacting with Interaction related data in a database.

    Attributes:
        db : Instance of SQLAlchemy's Session class. Provide a connection to a database.
    """

    def __init__(self, envs: XAgentServerEnv) -> None:
        """
        Initialize the InteractionBaseInterface instance.

        Args:
            envs (XAgentServerEnv): The environment variables of the XAgentServer.
        """
        pass

    def register_db(self, db: Session):
        """
        Registers a session with the database.

        Args:
            db (Session): Instance of SQLAlchemy's Session class. Provide a connection to a database.
        """
        self.db = db

    def init(self):
        """
        Initialization function, to be implemented by subclasses.
        """
        raise NotImplementedError

    def get_interaction_dict_list(self):
        """
        Returns a list of interaction dictionaries.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def get_interaction_list(self) -> list:
        """
        Returns a list of interactions.

        Returns:
            list: A list of interactions.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def get_interaction(self, interaction_id: str) -> InteractionBase:
        """
        Query an interaction by its id.

        Args:
            interaction_id (str): The id of the interaction to be queried.

        Returns:
            InteractionBase: The interaction model class instance with respect to the provided interaction_id.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def create_interaction(self, interaction: InteractionBase):
        """
        Creates an interaction.

        Args:
            interaction (InteractionBase): An instance of the Interaction model class representing a single interaction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
    
    def add_parameter(self, parameter: InteractionParameter):
        """
        Add a parameter to an interaction.

        Args:
            parameter (InteractionParameter): A parameter for the interaction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def get_interaction_by_user_id(self, user_id: str) -> list:
        """
        Query interactions by user_id.

        Args:
            user_id (str): The id of the user of the interactions.

        Returns:
            list: A list of interactions that belong to the given user.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
    
    def get_shared_interactions(self, page_size: int=20, page_index: int=1):
        """
        Get a list of shared interactions.

        Args:
            page_size (int, optional): The number of interactions to return. Defaults to 20.
            page_index (int, optional): Specifies which page of results to return. Defaults to 1.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
    
    def get_interaction_by_interaction_id(self, interaction_id: str):
        """
        Query an interaction by its id.

        Args:
            interaction_id (str): The id of the interaction to be queried.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
    
    def interaction_is_exist(self, interaction_id: str):
        """
        Check whether an interaction with a given interaction_id exists.

        Args:
            interaction_id (str): The interaction's id.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError 

    def update_interaction(self, interaction: InteractionBase):
        """
        Update an interaction's details.

        Args:
            interaction (InteractionBase): An instance of the Interaction model class with updated details.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError 
    
    def update_interaction_status(self, interaction_id: str, status: str, message: str, current_step: int):
        """
        Update an interaction's status, message, and current step.

        Args:
            interaction_id (str): The interaction's id.
            status (str): Updated status for the interaction.
            message (str): Message associated with the interaction.
            current_step (int): Current step of the interaction process.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError 
    
    def update_interaction_parameter(self, interaction_id: str, parameter: InteractionParameter):
        """
        Updates the parameter of an interaction.

        Args:
            interaction_id (str): The interaction's id.
            parameter (InteractionParameter): The updated parameter for the interaction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError 
    
    def is_running(self, user_id: str):
        """
        Checks if an interaction is currently running. 

        Args:
            user_id (str): The id of the user of the interaction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def delete_interaction(self, interaction_id: str):
        """
        Delete an interaction.

        Args:
            interaction_id (str): The interaction's id.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError 
    
    def add_share(self, shared: SharedInteractionBase):
        """
        Add a shared interaction.

        Args:
            shared (SharedInteractionBase): An instance of SharedInteractionBase representing a shared interaction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    def get_shared_interaction(self, interaction_id: str) -> SharedInteractionBase | None:
        """
        Get a shared interaction by its id.

        Args:
            interaction_id (str): The id of the shared interaction.

        Returns:
            SharedInteractionBase | None: The SharedInteractionBase instance with respect to the provided interaction_id,
                                          or None if no such shared interaction exists.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError