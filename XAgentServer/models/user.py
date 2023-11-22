import abc
import json

from XAgentServer.database.models import User


class XAgentUser(metaclass=abc.ABCMeta):

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
                 deleted: bool = False,
                 is_beta: bool = False,):
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
        self.is_beta = is_beta

    def to_dict(self):
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
            "deleted": self.deleted,
            "is_beta": self.is_beta
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @staticmethod
    def from_dict(user_dict: dict):
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
            deleted=user_dict["deleted"],
            is_beta=user_dict["is_beta"]
        )

    @staticmethod
    def from_json(user_json: str):
        return XAgentUser.from_dict(json.loads(user_json))

    def is_available(self):
        return self.available
    
    @staticmethod
    def from_db(user: User):
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
        is_beta = user.is_beta
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
            deleted=deleted,
            is_beta=is_beta
        )
        
