import copy
import json
import os
from datetime import datetime

from sqlalchemy.orm import Session

from XAgentServer.database import InteractionBaseInterface, UserBaseInterface
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.interaction import InteractionParameter
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.user import XAgentUser


class UserLocalStorageInterface(UserBaseInterface):
    """
    Manage user data through local file storage,
    serving as an interface for operations such as retrieving data, checking existence, adding, and updating.
    """

    def __init__(self, envs: XAgentServerEnv) -> None:
        """
        Args:
            envs (XAgentServerEnv): The environment configuration.

        Raises:
            ValueError: if the database type is not "file".
            ValueError: if the local storage does not support json file.
        """
        if envs.DB.db_type != "file":
            raise ValueError("UserLocalStorageInterface only support file db")
        try:
            self.db_url = envs.DB.db_url.get("users", "users/users.json")
        except Exception as e:
            raise ValueError(
                "UserLocalStorageInterface only support json file")
        self.envs = envs
        self.user_list_cache = []
        self.init()

    def register_db(self, db: Session):
        """
        Assign the database instance to the instance variable.

        Args:
            db (Session): The database connectivity session needs to be registered.

        Returns:
            None
        """
        self.db = db

    def init(self):
        """
        Create a local storage for users if it doesn't exist and cache all the user data.

        Returns:
            None
        """
        if not os.path.exists(os.path.dirname(self.db_url)):
            os.makedirs(os.path.dirname(self.db_url))

        # If user stored path doesn't exist, initialize the json file.
        if not os.path.exists(self.db_url):
            with open(self.db_url, "w", encoding="utf-8") as f:
                if self.envs.default_login:
                    json.dump([{
                        "user_id": "admin",
                        "email": "admin",
                        "token": "xagent-admin",
                        'name': 'admin',
                        "available": True,
                        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "corporation": "xagent",
                        "industry": "AI",
                        "position": "xagent",
                        "deleted": False
                    }], f, indent=2, ensure_ascii=False)
                else:
                    json.dump([], f, indent=2, ensure_ascii=False)

        # Load and cache user data.
        with open(self.db_url, "r", encoding="utf-8") as f:
            self.user_list_cache = json.load(f)

    def get_user_list(self) -> list:
        """
        Returns a list of user instances from the cached data.
        
        Returns:
            list: A list of XAgentUser instances.
        """
        users = []
        for user_dict in self.user_list_cache:
            users.append(XAgentUser(**user_dict))

        return users

    def get_user_dict_list(self):
        """
        Returns the cached user data.

        Returns:
            list: A list of dictionaries that each contain a user's information.
        """
        return self.user_list_cache

    def get_user(self, user_id: str | None = None, email: str | None = None) -> XAgentUser | None:
        """
        Retrieve a user instance by either the provided user_id or email.
        Args:
            user_id (str, optional): The user ID.
            email (str, optional): The user's email.

        Returns:
            `XAgentUser`: A user instance if find a match, else `None`.
        """
        if not email and not user_id:
            return None
        user_list = self.get_user_list()
        for user in user_list:
            if user.email == email and not user.deleted:
                return user
            if user.user_id == user_id and not user.deleted:
                return user
        return None

    def user_is_exist(self, user_id: str | None = None, email: str | None = None):
        """
        Check the existence of a user by its user_id or email.

        Args:
            user_id (str, optional): The user ID.
            email (str, optional): The user's email.

        Returns:
            bool: True if the user exist, False otherwise.
        """
        if not email and not user_id:
            return False

        user_list = self.get_user_list()

        for user in user_list:
            if user.email == email and not user.deleted:
                return True
            if user.user_id == user_id and not user.deleted:
                return True
        return False

    def token_is_exist(self, user_id: str, token: str | None = None):
        """
        Verify a token associated with a user_id.

        Args:
            user_id (str): The user ID.
            token (str, optional): The token.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        if not token:
            return False

        user_list = self.get_user_list()

        for user in user_list:
            if user.user_id == user_id and user.token == token and not user.deleted:
                return True
        return False

    def user_is_valid(self,
                      user_id: str | None = None,
                      email: str | None = None,
                      token: str | None = None):
        """
        Check the validity and availability of a user by user_id, email, and token.

        Args:
            user_id (str, optional): The user ID.
            email (str, optional): The user's email.
            token (str, optional): The token.

        Returns:
            bool: True if the user is valid, False otherwise.
        """
        if email == "":
            return False
        user_list = self.get_user_list()
        for user in user_list:
            if token == None:
                if user.email == email and user.available and not user.deleted:
                    return True
            if user_id != None:
                if user.user_id == user_id and user.token == token and user.available and not user.deleted:
                    return True
            if email != None:
                if user.email == email and user.token == token and user.available and not user.deleted:
                    return True
        return False

    def add_user(self, user_dict: dict):
        """
        Add a user to the local storage and update the cached data.

        Args:
            user_dict (dict): A dictionary containing a user's information.

        Returns:
            None
        """
        self.user_list_cache.append(user_dict)
        with open(self.db_url, "w", encoding="utf-8") as f:
            json.dump(self.user_list_cache, f, indent=2, ensure_ascii=False)

    def update_user(self, user: XAgentUser):
        """
        Update a user's availability in the local storage and cache.

        Args:
            user (XAgentUser): A user instance.

        Returns:
            None
        """
        for i, user_dict in enumerate(self.user_list_cache):
            if user.user_id == user_dict["user_id"]:
                user_dict["available"] = user.available

        with open(self.db_url, "w", encoding="utf-8") as f:
            json.dump(self.user_list_cache, f, indent=2, ensure_ascii=False)


class InteractionLocalStorageInterface(InteractionBaseInterface):
    """
    Manage interactions through local file storage,
    serving as an interface for operations such as retrieving data, checking existence, adding, and updating.
    """

    def __init__(self, envs: XAgentServerEnv) -> None:
        """
        Args:
            envs (XAgentServerEnv): The environment configuration.

        Raises:
            ValueError: if the database type is not "file".
            ValueError: if the local storage does not support json file.
        """
        super().__init__(envs)
        if envs.DB.db_type != "file":
            raise ValueError(
                "InteractionLocalStorageInterface only support file db")
        try:
            self.db_url = envs.DB.db_url.get(
                "interactions", "XAgentServer/localstorage/records/interaction.json")
            self.parameter_url = envs.DB.db_url.get(
                "parameter", "XAgentServer/localstorage/records/parameter.json")
        except Exception as e:
            raise ValueError(
                "InteractionLocalStorageInterface only support json file")
        self.interaction_list_cache = []
        self.interaction_parameter_cache = []
        self.init()

    def register_db(self, db: Session):
        """
        Assign the database instance to the instance variable.

        Args:
            db (Session): The database connectivity session needs to be registered.

        Returns:
            None
        """
        self.db = db

    def init(self):
        """
        Create local storages for interactions and interaction parameters if they don't exist 
        and cache all the interaction data and interaction parameter data.

        Returns:
            None
        """
        if not os.path.exists(os.path.dirname(self.db_url)):
            os.makedirs(os.path.dirname(self.db_url))

        if not os.path.exists(self.db_url):
            with open(self.db_url, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        if not os.path.exists(os.path.dirname(self.parameter_url)):
            os.makedirs(os.path.dirname(self.parameter_url))

        if not os.path.exists(self.parameter_url):
            with open(self.parameter_url, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

        with open(self.db_url, "r", encoding="utf-8") as f:
            self.interaction_list_cache = json.load(f)

        with open(self.parameter_url, "r", encoding="utf-8") as f:
            self.interaction_parameter_cache = json.load(f)

    def get_interaction_dict_list(self):
        """
        Returns a deepcopy of the cached interaction data.

        Returns:
            list: A list of dictionaries that each contains an interaction's information.
        """
        interactions  = copy.deepcopy(self.interaction_list_cache)
        return interactions

    def get_interaction_list(self) -> list:
        """
        Returns a deepcopy of the cached interaction data.

        Returns:
            list: A list of dictionaries that each contains an interaction's information.
        """
        interactions  = copy.deepcopy(self.interaction_list_cache)
        return interactions

    def get_interaction(self, interaction_id: str) -> InteractionBase | None:
        """
        Retrieve an interaction by its interaction_id.

        Args:
            interaction_id (str): The interaction ID.

        Returns:
            `InteractionBase`: An interaction instance if there is a match, else `None`.
        """
        interaction_list = self.get_interaction_list()
        for interaction in interaction_list:
            if interaction["interaction_id"] == interaction_id:
                return InteractionBase(**interaction)
        return None

    def create_interaction(self, base: InteractionBase):
        """
        Add an interaction to the local storage and update the cached data.

        Args:
            base (InteractionBase): An interaction instance.

        Returns:
            None
        """
        self.interaction_list_cache.append(base.to_dict())
        with open(self.db_url, "w", encoding="utf-8") as f:
            json.dump(self.interaction_list_cache, f,
                      indent=2, ensure_ascii=False)

    def add_parameter(self, parameter: InteractionParameter = None):
        """
        Add an interaction parameter to associated interaction and update the cached parameter data.

        Args:
            parameter (InteractionParameter, optional): An interaction parameter instance.

        Returns:
            None
        """
        if parameter is not None:
            interaction_ids = [
                k for k in self.interaction_parameter_cache.keys()]
            if parameter.interaction_id not in interaction_ids:
                self.interaction_parameter_cache[parameter.interaction_id] = [
                    parameter.to_dict()]
            else:
                self.interaction_parameter_cache[parameter.interaction_id].append(
                    parameter.to_dict())

            with open(self.parameter_url, "w", encoding="utf-8") as f:
                json.dump(self.interaction_parameter_cache,
                          f, indent=2, ensure_ascii=False)
                
    def get_parameter(self, interaction_id: str) -> list[InteractionParameter]:
        """
        Retrieve interaction parameters for an interaction.

        Args:
            interaction_id (str): The interaction ID.

        Returns:
            list: Returns a list of InteractionParameter instances if found, else an empty list.
        """
        interaction_ids = [k for k in self.interaction_parameter_cache.keys()]
        if interaction_id not in interaction_ids:
            return []
        else:
            return [InteractionParameter(**p) for p in self.interaction_parameter_cache[interaction_id]]

    def get_interaction_by_user_id(self, user_id: str, page_size: int = 10, page_num: int = 1) -> list[dict]:
        """
        Retrieve interactions for a user with pagination.

        Args:
            user_id (str): The user ID.
            page_size (int, optional): The maximum number of interactions per page.Default is 10.
            page_num (int, optional): The page number. Default is 1.

        Returns:
            dict: A dictionary containing the total numbers of interaction and the interactions of each page.
        """
        _data = []
        interaction_list = self.get_interaction_list()
        user_interaction_list = [interaction for interaction in interaction_list if interaction["user_id"] == user_id and not interaction["is_deleted"]]
        total = len(user_interaction_list)
        user_interaction_list = user_interaction_list[::-1]
        user_interaction_list = user_interaction_list[(
            page_num-1)*page_size:page_num*page_size]
        
        for i, interaction in enumerate(user_interaction_list):
            parameter = [{**p.args} if isinstance(p.args, dict) else p.args for p in self.get_parameter(interaction["interaction_id"])]
            interaction["parameters"] = parameter
            _data.append(interaction)
        return {
            "total": total,
            "rows": user_interaction_list
        }

    def get_interaction_by_interaction_id(self, interaction_id: str) -> InteractionBase | None:
        """
        Retrieve an interaction by its interaction_id.

        Args:
            interaction_id (str): The interaction ID.

        Returns:
            `InteractionBase`: An interaction instance if there is a match, else `None`.
        """
        interaction_list = self.get_interaction_list()
        for interaction in interaction_list:
            if interaction["interaction_id"] == interaction_id:
                return interaction
        return None

    def interaction_is_exist(self, interaction_id: str) -> bool:
        """
        Check if an interaction does exist by its interaction_id.

        Args:
            interaction_id (str): The interaction ID.

        Returns:
            bool: True if the interaction exists, else False.
        """
        interaction_list = self.get_interaction_list()
        for interaction in interaction_list:
            if interaction["interaction_id"] == interaction_id and not interaction["is_deleted"]:
                return True
        return False

    def update_interaction(self, base_data: dict):
        """
        Update an interaction's information in the local storage and cached data.

        Args:
            base_data (dict): A dictionary containing the interaction's updated data. The interaction IDmust be included in the dictionary.

        Raises:
            ValueError: If the interaction_id is not in `base_data`.

        Returns:
            None
        """
        if "interaction_id" not in base_data.keys():
            raise ValueError("interaction_id must be in base_data")
        for i, interaction_dict in enumerate(self.interaction_list_cache):
            if interaction_dict["interaction_id"] == base_data["interaction_id"]:
                for k, v in base_data.items():
                    if k == "interaction_id":
                        continue
                    self.interaction_list_cache[i][k] = v
                break

        with open(self.db_url, "w", encoding="utf-8") as f:
            json.dump(self.interaction_list_cache, f,
                      indent=2, ensure_ascii=False)

    def update_interaction_status(self, interaction_id: str, status: str, message: str, current_step: int):
        """
        Update an interaction's status, message, current step in the local storage and cached data.

        Args:
            interaction_id (str): The interaction ID.
            status (str): The updated status.
            message (str): The updated message.
            current_step (int): The updated current step.

        Returns:
            None
        """
        for i, interaction_dict in enumerate(self.interaction_list_cache):
            if interaction_dict["interaction_id"] == interaction_id:
                self.interaction_list_cache[i]["status"] = status
                self.interaction_list_cache[i]["message"] = message
                self.interaction_list_cache[i]["current_step"] = current_step
                self.interaction_list_cache[i]["update_time"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                break

        with open(self.db_url, "w", encoding="utf-8") as f:
            json.dump(self.interaction_list_cache, f,
                      indent=2, ensure_ascii=False)

    def update_interaction_parameter(self, interaction_id: str, parameter: InteractionParameter):
        """
        Update the interaction parameters for an interaction.

        Args:
            interaction_id (str): The interaction ID.
            parameter (InteractionParameter): The interaction parameter to be added.

        Returns:
            None
        """
        interaction_ids = [k for k in self.interaction_parameter_cache.keys()]
        if interaction_id not in interaction_ids:
            self.interaction_parameter_cache[interaction_id] = [
                parameter.to_dict()]
        else:
            self.interaction_parameter_cache[interaction_id].append(
                parameter.to_dict())

        with open(self.parameter_url, "w", encoding="utf-8") as f:
            json.dump(self.interaction_parameter_cache,
                      f, indent=2, ensure_ascii=False)

    def is_running(self, user_id: str):
        """
        Check if there is any running or waiting interaction associated with a user.

        Args:
            user_id (str): The user ID.

        Returns:
            bool: True if there is any running or waiting interaction, False otherwise.
        """
        interaction_list = self.get_interaction_list()
        for interaction in interaction_list:
            if interaction["user_id"] == user_id and interaction["status"] in ["running", "waiting"] and not interaction["is_deleted"]:
                return True
        return False
    
    def delete_interaction(self, interaction_id: str):
        """
        Delete an interaction in the local storage and cached data by marking its `is_deleted` attribute as True.

        Args:
            interaction_id (str): The interaction ID.

        Returns:
            None
        """
        interaction_list = self.get_interaction_list()
        for i, interaction_dict in enumerate(interaction_list):
            if interaction_dict["interaction_id"] == interaction_id:
                self.interaction_list_cache[i]["is_deleted"] = True
                break

        with open(self.db_url, "w", encoding="utf-8") as f:
            json.dump(self.interaction_list_cache, f,
                      indent=2, ensure_ascii=False)

    def get_shared_interaction(self, interaction_id: str) -> InteractionBase | None:
        """
        Retrieve a shared interaction by its interaction_id.

        Args:
            interaction_id (str): The interaction ID.

        Returns:
            `InteractionBase`: An interaction instance if there is a match, else `None`.
        """
        interaction_list = self.get_interaction_list()
        for interaction in interaction_list:
            if interaction["interaction_id"] == interaction_id:
                return InteractionBase(**interaction)
        return None