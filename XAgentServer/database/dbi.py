from datetime import datetime

from sqlalchemy.sql import func

from XAgentServer.database import InteractionBaseInterface, UserBaseInterface
from XAgentServer.database.connect import DBConnection
from XAgentServer.database.models import (Interaction, Parameter,
                                          SharedInteraction, User)
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.shared_interaction import SharedInteractionBase
from XAgentServer.models.user import XAgentUser


class UserDBInterface(UserBaseInterface):
    def __init__(self, envs: XAgentServerEnv) -> None:
        if envs.DB.use_db and envs.DB.db_type == "file":
            raise ValueError("UserDB except a sql database, such as sqlite, mysql, postgresql")
        self.db_url = envs.DB.db_url


    def register_db(self, connection: DBConnection):
        self.db = connection.get_db()

    def init(self):
        raise NotImplementedError

    def get_user_list(self) -> list[XAgentUser]:
        users = self.db.query(User).all()
        users = [XAgentUser.from_db(user) for user in users]
        return users

    def get_user_dict_list(self):
        return self.user_list_cache

    def get_user(self, user_id: str | None = None, email: str | None = None) -> XAgentUser | None:
        if not email and not user_id:
            return None
        if email:
            user = self.db.query(User).filter(User.email == email, User.deleted == False).first()
        else:
            user = self.db.query(User).filter(User.user_id == user_id, User.deleted == False).first()
        
        return XAgentUser.from_db(user) if user else None

    def user_is_exist(self, user_id: str | None = None, email: str | None = None):
        if not email and not user_id:
            return False
        if email:
            user = self.db.query(User).filter(User.email == email, User.deleted == False).first()
        else:
            user = self.db.query(User).filter(User.user_id == user_id, User.deleted == False).first()
        return user is not None

    def token_is_exist(self, user_id: str, token: str | None = None):

        if not token:
            return False

        user = self.db.query(User).filter(User.user_id == user_id, User.token == token, User.deleted == False).first()
        return user is not None

    def user_is_valid(self,
                      user_id: str | None = None,
                      email: str | None = None,
                      token: str | None = None):
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
        self.db.add(User(**user_dict))
        self.db.commit()

    def update_user(self, user: XAgentUser):
        db_user = self.db.query(User).filter(User.user_id == user.user_id, User.deleted == False).first()
        db_user.available = user.available
        db_user.email = user.email
        db_user.name = user.name
        db_user.token = user.token
        self.db.commit()


class InteractionDBInterface(InteractionBaseInterface):
    def __init__(self, envs: XAgentServerEnv) -> None:
        super().__init__(envs)
        if envs.DB.use_db and envs.DB.db_type not in ["sqlite", "mysql", "postgresql"]:
            raise ValueError("UserDB except a sql database, such as sqlite, mysql, postgresql")
        self.db_url = envs.DB.db_url


    def register_db(self, connection: DBConnection):
        self.db = connection.get_db()

    def init(self):
        raise NotImplementedError
    

    def get_interaction_dict_list(self):
        raise NotImplementedError

    def get_interaction_list(self) -> list[InteractionBase]:
        interactions = self.db.query(Interaction).all()
        return [InteractionBase.from_db(interaction) for interaction in interactions]

    def get_interaction(self, interaction_id: str) -> InteractionBase | None:
        interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id).first()
        return InteractionBase.from_db(interaction) if interaction else None

    def create_interaction(self, base: InteractionBase) -> InteractionBase:
        self.db.add(Interaction(**base.to_dict()))
        self.db.commit()
        return None
    
    def add_parameter(self, parameter: InteractionParameter):
        self.db.add(Parameter(**parameter.to_dict()))
        self.db.commit()
        return None

    def get_interaction_by_user_id(self, user_id: str, page_size: int = 20, page_num: int = 1) -> list[dict]:
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
        interaction = self.db.query(SharedInteraction).filter(SharedInteraction.interaction_id == interaction_id, SharedInteraction.is_deleted == False).first()
        return SharedInteractionBase.from_db(interaction) if interaction else None


    def interaction_is_exist(self, interaction_id: str) -> bool:
        interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id, Interaction.is_deleted == False).first()
        return interaction is not None
    

    def update_interaction(self, base_data: dict):
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

    def update_interaction_status(self, interaction_id: str, status: str, message: str, current_step: int):
        db_interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id).first()
        db_interaction.status = status
        db_interaction.message = message
        db_interaction.current_step = current_step
        db_interaction.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.commit()

    def update_interaction_parameter(self, interaction_id: str, parameter: InteractionParameter):
        db_parameter = self.db.query(Parameter).filter(Parameter.interaction_id == interaction_id, Parameter.parameter_id == parameter.parameter_id).first()
        if db_parameter is None:
            self.db.add(Parameter(**parameter.to_dict()))
        self.db.commit()

    def is_running(self, user_id: str):
        interaction = self.db.query(Interaction).filter(Interaction.user_id == user_id, Interaction.status.in_(("running", "waiting"))).first()
        return interaction is not None
    
    def get_parameter(self, interaction_id: str):
        parameters = self.db.query(Parameter).filter(Parameter.interaction_id == interaction_id).all()
        return [InteractionParameter.from_db(param) for param in parameters]
    
    def delete_interaction(self, interaction_id: str):
        interaction = self.db.query(Interaction).filter(Interaction.interaction_id == interaction_id).first()
        if interaction is None:
            raise ValueError("interaction is not exist")
        interaction.is_deleted = True
        self.db.commit()

    def add_share(self, shared: SharedInteractionBase):
        self.db.add(SharedInteraction(**shared.to_dict()))
        self.db.commit()