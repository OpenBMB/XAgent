import traceback
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from XAgentServer.database import InteractionBaseInterface, UserBaseInterface
from XAgentServer.database.models import (Interaction, Parameter,
                                          SharedInteraction, User)
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.shared_interaction import SharedInteractionBase
from XAgentServer.models.user import XAgentUser


class UserDBInterface(UserBaseInterface):
    """
    Database interface for user interactions.

    Args:
        envs (XAgentServerEnv): The server environment variables.

    Raises:
        ValueError: If the database type is 'file'.
    """
    def __init__(self, envs: XAgentServerEnv) -> None:
        if envs.DB.use_db and envs.DB.db_type == "file":
            raise ValueError("UserDB except a sql database, such as sqlite, mysql, postgresql")
        self.db_url = envs.DB.db_url

    def register_db(self, db: Session):
        """
        Registers a database session.

        Args:
            db (Session): The database session to be registered.
        """
        self.db = db

    def init(self):
        """
        Initializes the database, currently not implemented.
        """
        raise NotImplementedError

    def get_user_list(self) -> list[XAgentUser]:
        """
        Gets a list of all users.

        Returns:
            list: A list of all users.
        """
        users = self.db.query(User).all()
        users = [XAgentUser.from_db(user) for user in users]
        return users

    def get_user_dict_list(self):
        """
        Gets a list of user data in dictionary format. The actual function is not implemented.
        """
        return self.user_list_cache

    def get_user(self, user_id: str | None = None, email: str | None = None) -> XAgentUser | None:
        """
        Get user information via user's id or email.

        Args:
            user_id (str | None): User's id.  
            email (str | None): User's email.

        Returns:
            XAgentUser | None: The requested user or None if the user doesn't exist.
        """
        if not email and not user_id:
            return None
        if email:
            user = self.db.query(User).filter(User.email == email, User.deleted == False).first()
        else:
            user = self.db.query(User).filter(User.user_id == user_id, User.deleted == False).first()

        return XAgentUser.from_db(user) if user else None

    def user_is_exist(self, user_id: str | None = None, email: str | None = None):
        """
        Checks whether a user exists by user's id or email.

        Args:
            user_id (str | None): User's id.  
            email (str | None): User's email.

        Returns:
            bool: True if the user exists, otherwise False.
        """
        if not email and not user_id:
            return False
        if email:
            user = self.db.query(User).filter(User.email == email, User.deleted == False).first()
        else:
            user = self.db.query(User).filter(User.user_id == user_id, User.deleted == False).first()
        return user is not None

    def token_is_exist(self, user_id: str, token: str | None = None):
        """
        Checks token existence for a user.

        Args:
            user_id (str): The id of the user.  
            token (str | None): Token to check.

        Returns:
            bool: True if the token exists, otherwise False.
        """
        if not token:
            return False

        user = self.db.query(User).filter(User.user_id == user_id, User.token == token, User.deleted == False).first()
        return user is not None

    def user_is_valid(self,
                      user_id: str | None = None,
                      email: str | None = None,
                      token: str | None = None):
        """
        Checks user's validity via user's id, email or token.

        Args:
            user_id (str | None): User's id.  
            email (str | None): User's email.
            token (str | None): User's token.

        Returns:
            bool: The validity of the user.
        """
        if email == "":
            return False
        user = self.db.query(User).filter(User.user_id == user_id, User.token == token, User.deleted == False).first()
        if token == None:
            if user.email == email and user.available:
                return True
        if user_id != None:
            if user.user_id == user_id and user.token == token and user.available:
                return True
        if email != None:
            if user.email == email and user.token == token and user.available:
                    return True
        return False

    def add_user(self, user_dict: dict):
        """
        Adds a new user to the database.

        Args:
            user_dict (dict): A dictionary containing the user's data.

        Raises:
            Exception: If there is a database error.
        """
        try:
            self.db.add(User(**user_dict))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())

    def update_user(self, user: XAgentUser):
        """
        Updates an existing user's information.

        Args:
            user (XAgentUser): Updated data for the user.

        Raises:
            Exception: If there is a database error.
        """
        db_user = self.db.query(User).filter(User.user_id == user.user_id, User.deleted == False).first()
        try:
            db_user.available = user.available
            db_user.email = user.email
            db_user.name = user.name
            db_user.token = user.token
            db_user.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())


class InteractionDBInterface(InteractionBaseInterface):
    """
    Database interface for user's interactions.

    Args:
        envs (XAgentServerEnv): The server environment variables.

    Raises:
        ValueError: If the database type is not supported.
    """
    def __init__(self, envs: XAgentServerEnv) -> None:
        super().__init__(envs)
        if envs.DB.use_db and envs.DB.db_type not in ["sqlite", "mysql", "postgresql"]:
            raise ValueError("UserDB except a sql database, such as sqlite, mysql, postgresql")
        self.db_url = envs.DB.db_url

    def register_db(self, db: Session):
        """
        Registers a database session.

        Args:
            db (Session): The database session to be registered.
        """
        self.db = db

    def init(self):
        """
        Initializes the database, currently not implemented.
        """
        raise NotImplementedError


    def get_interaction_dict_list(self):
        """
        Gets a list of user's interactions in dictionary format. The actual function is not implemented.
        """
        raise NotImplementedError

    def get_interaction_list(self) -> list[InteractionBase]:
        """
        Gets a list of all interactions.

        Returns:
            list: A list of all interactions.
        """
        interactions = self.db.query(Interaction).all()
        return [InteractionBase.from_db(interaction) for interaction in interactions]

    def get_interaction(self, interaction_id: str) -> InteractionBase | None:
        """
        Get an interaction information via interaction's id.

        Args:
            interaction_id (str): Interaction's id.

        Returns:
            InteractionBase | None: The requested Interaction or None if the Interaction doesn't exist.
        """
        interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id).first()
        return InteractionBase.from_db(interaction) if interaction else None

    def create_interaction(self, base: InteractionBase) -> InteractionBase:
        """
        Creates an interaction.

        Args:
            base (InteractionBase): Base interaction data.

        Returns:
            InteractionBase: The created interaction.

        Raises:
            Exception: If there is a database error.
        """
        try:
            self.db.add(Interaction(**base.to_dict()))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())
        return None

    def add_parameter(self, parameter: InteractionParameter):
        """
        Adds a parameter to an interaction.

        Args:
            parameter (InteractionParameter): Parameter to be added.

        Returns:
            None: The function currently always returns None.

        Raises:
            Exception: If there is a database error.
        """
        try:
            self.db.add(Parameter(**parameter.to_dict()))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())

        return None

    def get_interaction_by_user_id(self, user_id: str, page_size: int = 20, page_num: int = 1) -> list[dict]:
        """
        Checks if a user has interactions

        Args:
            user_id (str): The id of the user.
            page_size (int): Number of results per page.
            page_num (int): Page number.

        Returns:
            dict: A dictionary containing the total number of interactions and a list of dictionaries 
            that represent each interaction.
        """
        total = self.db.query(func.count(Interaction.id)).filter(Interaction.user_id == user_id, Interaction.is_deleted == False).scalar()
        interaction_list = self.db.query(Interaction).filter(Interaction.user_id == user_id, Interaction.is_deleted == False).limit(page_size).offset((page_num - 1) * page_size).all()
        data = []
        for i, interaction in enumerate(interaction_list):
            d_ = InteractionBase.from_db(interaction).to_dict(exclude=["recorder_root_dir", "is_deleted"])
            parameter = [{**p.args} if isinstance(p.args, dict) else p.args for p in self.get_parameter(d_["interaction_id"])]
            d_["parameters"] = parameter
            data.append(d_)
        return {
            "total": total,
            "rows": data
        }

    def get_shared_interactions(self, page_size: int = 20, page_num: int = 1) -> list[dict]:
        """
        Gets shared interactions for a user.

        Args:
            page_size (int): Number of results per page.
            page_num (int): Page number.

        Returns:
            dict: A dictionary containing the total number of shared interactions and a list of dictionaries 
            that represent each shared interaction.
        """
        total = self.db.query(func.count(SharedInteraction.id)).filter(SharedInteraction.is_deleted == False).scalar()
        interaction_list = self.db.query(SharedInteraction).filter(SharedInteraction.is_deleted == False).order_by(SharedInteraction.star.desc()).limit(page_size).offset((page_num - 1) * page_size).all()
        data = []
        for i, interaction in enumerate(interaction_list):
            d_ = SharedInteractionBase.from_db(interaction).to_dict(exclude=["record_dir", "is_deleted"])
            parameter = [{**p.args} if isinstance(p.args, dict) else p.args for p in self.get_parameter(d_["interaction_id"])]
            d_["parameters"] = parameter
            data.append(d_)
        return {
            "total": total,
            "rows": data
        }

    def get_shared_interaction(self, interaction_id: str) -> SharedInteractionBase | None:
        """
        Get shared interaction information via interaction's id.

        Args:
            interaction_id (str): Interaction's id.

        Returns:
            SharedInteractionBase | None: The requested shared Interaction or None if the shared Interaction doesn't exist.
        """
        interaction = self.db.query(SharedInteraction).filter(SharedInteraction.interaction_id == interaction_id, SharedInteraction.is_deleted == False).first()
        return SharedInteractionBase.from_db(interaction) if interaction else None

    def interaction_is_exist(self, interaction_id: str) -> bool:
        """
        Checks whether an interaction exists by interaction's id.

        Args:
            interaction_id (str): Interaction's id.

        Returns:
            bool: True if the interaction exists, otherwise False.
        """
        interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id, Interaction.is_deleted == False).first()
        return interaction is not None

    def update_interaction(self, base_data: dict):
        """
        Updates an interaction's information.

        Args:
            base_data (dict): Updated data for the interaction.

        Raises:
            Exception, ValueError: If there is a database error or interaction is not exist.
        """
        try:
            if "interaction_id" not in base_data:
                raise ValueError("interaction_id is required")
            interaction = self.db.query(Interaction).filter(Interaction.interaction_id == base_data["interaction_id"]).first()
            if interaction is None:
                raise ValueError("interaction is not exist")
            for k, v in base_data.items():
                if k == "interaction_id":
                    continue
                setattr(interaction, k, v)
            interaction.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())

    def update_interaction_status(self, interaction_id: str, status: str, message: str, current_step: int):
        """
        Updates the status of an interaction.

        Args:
            interaction_id (str): Interaction's id.
            status (str): Status to be updated to.
            message (str): Message to be updated.
            current_step (str): Current step to be updated.

        Raises:
            Exception: If there is a database error.
        """
        try:
            db_interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id).first()
            db_interaction.status = status
            db_interaction.message = message
            db_interaction.current_step = current_step
            db_interaction.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())
    
    def update_interaction_parameter(self, interaction_id: str, parameter: InteractionParameter):
        """
        Updates the parameter of an interaction.

        Args:
            interaction_id (str): Interaction's id.
            parameter (InteractionParameter): Parameter to be updated.

        Raises:
            Exception: If there is a database error.
        """
        try:
            db_parameter = self.db.query(Parameter).filter(Parameter.interaction_id == interaction_id, Parameter.parameter_id == parameter.parameter_id).first()
            if db_parameter is None:
                self.db.add(Parameter(**parameter.to_dict()))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())
    
    def is_running(self, user_id: str):
        """
        Checks if a certain user is running an interaction.

        Args:
            user_id (str): Id of the user to check.

        Returns:
            bool: True if the user is running an interaction, otherwise False.
        """
        interaction = self.db.query(Interaction).filter(Interaction.user_id == user_id, Interaction.status.in_(("running", "waiting"))).first()
        return interaction is not None
    
    
    def get_parameter(self, interaction_id: str):
        """
        Gets all parameters for a given interaction.

        Args:
            interaction_id (str): The id of the interaction.

        Returns:
            list: A list of all parameters for the interaction.
        """
        parameters = self.db.query(Parameter).filter(Parameter.interaction_id == interaction_id).all()
        return [InteractionParameter.from_db(param) for param in parameters]

    def delete_interaction(self, interaction_id: str):
        """
        Deletes an interaction.

        Args:
            interaction_id (str): The id of the interaction.

        Raises:
            Exception, ValueError: If there is a database error or interaction is not exist.
        """
        try:
            interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id).first()
            if interaction is None:
                raise ValueError("interaction is not exist")
            interaction.is_deleted = True
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())

    
    def add_share(self, shared: SharedInteractionBase):
        """
        Adds a shared interaction to the database.

        Args:
            shared (SharedInteractionBase): Shared interaction to be added.

        Raises:
            Exception: If there is a database error.
        """
        try:
            self.db.add(SharedInteraction(**shared.to_dict()))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(traceback.print_exec())