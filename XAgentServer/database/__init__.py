from typing import Union

from sqlalchemy.orm import Session

from XAgentServer.envs import XAgentServerEnv
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.shared_interaction import SharedInteractionBase


class UserBaseInterface:
    """ """

    def __init__(self, envs: XAgentServerEnv) -> None:
        pass

    def register_db(self, db: Session):
        self.db = db

    def init(self):
        raise NotImplementedError

    def get_user_list(self) -> list:
        raise NotImplementedError

    def get_user_dict_list(self):
        raise NotImplementedError

    def get_user(
        self, user_id: Union[str, None] = None, email: Union[str, None] = None
    ):
        raise NotImplementedError

    def user_is_exist(
        self, user_id: Union[str, None] = None, email: Union[str, None] = None
    ):
        raise NotImplementedError

    def token_is_exist(self, user_id: str, token: Union[str, None] = None):
        raise NotImplementedError

    def user_is_valid(
        self,
        user_id: Union[str, None] = None,
        email: Union[str, None] = None,
        token: Union[str, None] = None,
    ):
        raise NotImplementedError

    def add_user(self, user_dict: dict):
        raise NotImplementedError

    def update_user(self, user):
        raise NotImplementedError


class InteractionBaseInterface:
    def __init__(self, envs: XAgentServerEnv) -> None:
        pass

    def register_db(self, db: Session):
        self.db = db

    def init(self):
        raise NotImplementedError

    def get_interaction_dict_list(self):
        raise NotImplementedError

    def get_interaction_list(self) -> list:
        raise NotImplementedError

    def get_interaction(self, interaction_id: str) -> InteractionBase:
        raise NotImplementedError

    def create_interaction(self, interaction: InteractionBase):
        raise NotImplementedError

    def add_parameter(self, parameter: InteractionParameter):
        raise NotImplementedError

    def get_interaction_by_user_id(self, user_id: str) -> list:
        raise NotImplementedError

    def get_shared_interactions(self, page_size: int = 20, page_index: int = 1):
        raise NotImplementedError

    def get_interaction_by_interaction_id(self, interaction_id: str):
        raise NotImplementedError

    def interaction_is_exist(self, interaction_id: str):
        raise NotImplementedError

    def update_interaction(self, interaction: InteractionBase):
        raise NotImplementedError

    def update_interaction_status(
        self, interaction_id: str, status: str, message: str, current_step: int
    ):
        raise NotImplementedError

    def update_interaction_parameter(
        self, interaction_id: str, parameter: InteractionParameter
    ):
        raise NotImplementedError

    def is_running(self, user_id: str):
        raise NotImplementedError

    def delete_interaction(self, interaction_id: str):
        raise NotImplementedError

    def add_share(self, shared: SharedInteractionBase):
        raise NotImplementedError

    def get_shared_interaction(
        self, interaction_id: str
    ) -> SharedInteractionBase | None:
        raise NotImplementedError
