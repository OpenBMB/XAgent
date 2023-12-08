import abc
import json

from XAgentServer.database.models import User


class XAgentUser(metaclass=abc.ABCMeta):
    """
    A class to represent a XAgent User.

    Attributes
    ----------
    user_id : str
        The unique id of the user.
    email : str
        The email address of the user.
    name : str
        The name of the user.
    token : str
        The token of the user.
    available : bool, optional (True by default)
        The availability status of a user.
    corporation : str, optional (None by default)
        The corporation the user belongs to.
    industry : str, optional (None by default)
        The industry the user belongs to.
    position : str, optional (None by default)
        The position of the user in the corporation.
    create_time : str, optional (None by default)
        The creation time of the user profile.
    update_time : str, optional (None by default)
        The last update time of the user profile
    deleted : bool, optional (False by default)
        The deletion status of a user. 
    """

    def __init__(self, 
                 user_id: str, 
                 email: str, 
                 name: str, 
                 token: str, 
                 available: bool = True,
                 corporation: str = None,
                 industry: str = None,
                 position: str = None,
                 create_time: str = None,
                 update_time: str = None,
                 deleted: bool = False):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.token = token
        self.available = available
        self.corporation = corporation
        self.industry = industry
        self.position = position
        self.create_time = create_time
        self.update_time = update_time
        self.deleted = deleted

    def to_dict(self) -> dict:
        """
        Converts the User object to a dictionary.

        Returns
        -------
        dict
            The User object as a dictionary.
        """
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "token": self.token,
            "available": self.available,
            "corporation": self.corporation,
            "industry": self.industry,
            "position": self.position,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "deleted": self.deleted
        }

    def to_json(self) -> str:
        """
        Converts the User object to a JSON string.

        Returns
        -------
        str
            The User object as a JSON string.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @staticmethod
    def from_dict(user_dict: dict):
        """
        Converts a dictionary to a User object.

        Args
        ----
        user_dict : dict
            dictionary representing a User object.

        Returns
        -------
        XAgentUser object.

        """
        return XAgentUser(
            user_id=user_dict["user_id"],
            email=user_dict["email"],
            name=user_dict["name"],
            token=user_dict["token"],
            available=user_dict["available"],
            corporation=user_dict["corporation"],
            industry=user_dict["industry"],
            position=user_dict["position"],
            create_time=user_dict["create_time"],
            update_time=user_dict["update_time"],
            deleted=user_dict["deleted"]
        )

    @staticmethod
    def from_json(user_json: str):
        """
        Converts a JSON string to a User object.

        Args
        ----
        user_json : str
            JSON string representing a User object.

        Returns
        -------
        XAgentUser object.
        """
        return XAgentUser.from_dict(json.loads(user_json))

    def is_available(self) -> bool:
        """
        Checks the availability of the User.
        
        Returns
        -------
        bool
            The availability status of the user.

        """
        return self.available
    
    @staticmethod
    def from_db(user: User):
        """
        Creates XAgentUser instance from a User instance from database.

        Args
        ----
        user : User
            User instance from database.

        Returns
        -------
        XAgentUser
            An instance of XAgentUser.
        """
        user_id = user.user_id
        email = user.email
        name = user.name
        token = user.token
        available = user.available
        corporation = user.corporation
        industry = user.industry
        position = user.position
        create_time = user.create_time
        update_time = user.update_time
        deleted = user.deleted
        return XAgentUser(
            user_id=user_id,
            email=email,
            name=name,
            token=token,
            available=available,
            corporation=corporation,
            industry=industry,
            position=position,
            create_time=create_time,
            update_time=update_time,
            deleted=deleted
        )