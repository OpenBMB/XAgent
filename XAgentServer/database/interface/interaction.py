"""DB Interface: Interaction"""
import abc
from datetime import datetime
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from XAgentServer.database.models import (Interaction, Parameter,
                                          SharedInteraction, Raw)
from XAgentServer.enums.status import StatusEnum
from XAgentServer.exts.exception_ext import XAgentError
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.shared_interaction import SharedInteractionBase
from XAgentServer.models.raw import XAgentRaw


class InteractionDBInterface(metaclass=abc.ABCMeta):
    """Interaction DB Interface
    """

    @classmethod
    def search_many_interaction(cls, db: Session) -> list[InteractionBase]:
        """search many interactions

        Args:
            db (Session): db session

        Returns:
            list[InteractionBase]: interaction list
        """
        interactions = db.query(Interaction).all()
        return [InteractionBase.from_db(interaction) for interaction in interactions]

    @classmethod
    def get_interaction(cls,
                        db: Session,
                        interaction_id: str) -> InteractionBase | None:
        """get interaction by interaction_id

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:
            InteractionBase | None: _description_
        """
        interaction = db.query(Interaction).filter(
            Interaction.interaction_id == interaction_id,
            Interaction.is_deleted.is_not(True)).first()
        return InteractionBase.from_db(interaction) if interaction else None

    @classmethod
    def get_ready_interaction(cls,
                              db: Session,
                              user_id: str) -> InteractionBase | None:
        """get interaction by user_id

        Args:
            db (Session): db session
            user_id (str): user id

        Returns:
            InteractionBase | None: _description_
        """
        interaction = db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.status == 'ready').first()
        return InteractionBase.from_db(interaction) if interaction else None

    @classmethod
    def create_interaction(cls,
                           db: Session,
                           base: InteractionBase) -> InteractionBase:
        """
        create interaction

        Args:
            db (Session): db session
            base (InteractionBase): interaction base

        Returns:
            None
        """
        db.add(Interaction(**base.to_dict()))
        db.commit()
        return None

    @classmethod
    def add_parameter(cls,
                      db: Session,
                      parameter: InteractionParameter):
        """
        add parameter for interaction
        """
        db.add(Parameter(**parameter.to_dict()))
        db.commit()

        return None

    @classmethod
    def search_interaction_by_user_id(cls,
                                      db: Session,
                                      user_id: str,
                                      page_size: int = 20,
                                      page_num: int = 1) -> list[dict]:
        """
        search interaction by user id

        Args:
            db (Session): db session
            user_id (str): user id
            page_size (int, optional): page size. Defaults to 20.
            page_num (int, optional): page num. Defaults to 1.

        Returns:
            list[dict]: interaction list
        """
        total = db.query(func.count(Interaction.id)).filter(
            Interaction.user_id == user_id, Interaction.is_deleted.is_(False)).scalar()

        interaction_list = db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.is_deleted.is_(False),
            Interaction.status.in_([StatusEnum.FINISHED])).limit(
            page_size).offset((page_num - 1) * page_size).all()
        data = []
        for interaction in interaction_list:
            d_ = InteractionBase.from_db(interaction).to_dict(
                exclude=["recorder_root_dir", "is_deleted"])
            parameter = cls.get_parameter(
                db=db, interaction_id=d_["interaction_id"])
            d_["parameters"] = [parameter[0]]
            data.append(d_)
        return {
            "total": total,
            "rows": data
        }

    @classmethod
    def search_many_shared(cls,
                           db: Session,
                           page_size: int = 20,
                           page_index: int = 1) -> list[dict]:
        """
        search many shared interactions from community

        Args:
            db (Session): db session
            page_size (int, optional): page size. Defaults to 20.
            page_index (int, optional): page index. Defaults to 1.

        Returns:
            list[dict]: interaction list
        """
        total = db.query(func.count(SharedInteraction.id)).filter(
            SharedInteraction.is_deleted.is_(False),
            SharedInteraction.is_audit.is_(True)).scalar()
        interaction_list = db.query(SharedInteraction).filter(
            SharedInteraction.is_deleted.is_(False),
            SharedInteraction.is_audit.is_(True)).order_by(
            SharedInteraction.star.desc()).limit(page_size).offset(
                (page_index - 1) * page_size).all()
        data = []
        for interaction in interaction_list:
            d_ = SharedInteractionBase.from_db(interaction).to_dict(
                exclude=["record_dir", "is_deleted"])
            parameter = cls.get_parameter(
                db=db, interaction_id=d_["interaction_id"])
            d_["parameters"] = parameter
            data.append(d_)
        return {
            "total": total,
            "rows": data
        }

    @classmethod
    def get_shared_interaction(cls,
                               db: Session,
                               interaction_id: str) -> SharedInteractionBase | None:
        """
        get shared interaction by interaction id

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:

            SharedInteractionBase | None: shared interaction
        """
        interaction = db.query(SharedInteraction).filter(
            SharedInteraction.interaction_id == interaction_id, SharedInteraction.is_deleted.is_(False)).first()
        return SharedInteractionBase.from_db(interaction) if interaction else None

    @classmethod
    def is_exist(cls,
                 db: Session,
                 interaction_id: str) -> bool:
        """
        check interaction is exist or not

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:
            bool: True or False
        """
        interaction = db.query(Interaction).filter(
            Interaction.interaction_id == interaction_id,
            Interaction.is_deleted.is_(False)).first()
        return interaction is not None

    @classmethod
    def update_interaction(cls, db: Session, base_data: dict):
        """
        update interaction

        Args:
            db (Session): db session
            base_data (dict): interaction data

        Returns:
            None
        """
        if "interaction_id" not in base_data:
            raise XAgentError("interaction_id is required")
        interaction = db.query(Interaction).filter(
            Interaction.interaction_id == base_data["interaction_id"]).first()
        if interaction is None:
            raise XAgentError("interaction is not exist")
        for k, v in base_data.items():
            if k == "interaction_id":
                continue
            setattr(interaction, k, v)
        interaction.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()

    @classmethod
    def update_interaction_status(cls,
                                  db: Session,
                                  interaction_id: str,
                                  status: str,
                                  message: str,
                                  current_step: int):
        """
        update interaction status

        Args:
            db (Session): db session
            interaction_id (str): interaction id
            status (str): status
            message (str): message
            current_step (int): current step

        Returns:
            None
        """
        db_interaction = db.query(Interaction).filter(
            Interaction.interaction_id == interaction_id).first()
        if db_interaction is None:
            raise XAgentError("interaction is not exist")

        db_interaction.status = status
        db_interaction.message = message
        db_interaction.current_step = current_step
        db_interaction.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()

    @classmethod
    def update_interaction_parameter(cls,
                                     db: Session,
                                     interaction_id: str,
                                     parameter: InteractionParameter):
        """
        update interaction parameter

        Args:
            db (Session): db session
            interaction_id (str): interaction id
            parameter (InteractionParameter): parameter

        Returns:
            None
        """
        db_parameter = db.query(Parameter).filter(
            Parameter.interaction_id == interaction_id,
            Parameter.parameter_id == parameter.parameter_id).first()

        if db_parameter is None:
            db.add(Parameter(**parameter.to_dict()))
        db.commit()

    @classmethod
    def is_running(cls, db: Session, user_id: str):
        """
        check user is only running one interaction

        Args:
            db (Session): db session
            user_id (str): user id

        Returns:    
            bool: True or False
        """
        interaction = db.query(Interaction).filter(
            Interaction.user_id == user_id,
            Interaction.status.in_(("running", "waiting"))).first()
        return interaction is not None

    @classmethod
    def get_parameter(cls, db: Session, interaction_id: str) -> list:
        """
        get interaction running parameter

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:
            list: parameter list
        """
        raws = db.query(Raw).filter(
            Raw.interaction_id == interaction_id,
            Raw.is_human.is_(True),
            Raw.human_data.is_not(None)).order_by(Raw.step.asc()).all()
        return [raw.human_data for raw in raws]

    @classmethod
    def delete_interaction(cls, db: Session, interaction_id: str):
        """
        delete interaction

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:
            None

        Raises:
            XAgentError: interaction is not exist
        """
        interaction = db.query(Interaction).filter(
            Interaction.interaction_id == interaction_id).first()
        if interaction is None:
            raise XAgentError("interaction is not exist")
        interaction.is_deleted = True
        db.commit()

    @classmethod
    def add_share(cls, db: Session, shared: SharedInteractionBase):
        """add share interaction

        Args:
            db (Session): db session
            shared (SharedInteractionBase): shared interaction from community
        """
        db.add(SharedInteraction(**shared.to_dict()))

    @classmethod
    def insert_raw(cls, db: Session, process: XAgentRaw):
        """
        insert an interaction process for recording

        Args:
            db (Session): db session
            process (XAgentRaw): interaction process

        Returns:
            None

        Raises:
            XAgentError: interaction is not exist
        """
        interaction = db.query(Interaction).filter(
            process.interaction_id == process.interaction_id).first()
        exist_process = db.query(Raw).filter(
            Raw.interaction_id == process.interaction_id, Raw.is_deleted.is_(False)).order_by(Raw.step.desc()).first()
        if interaction is None:
            raise XAgentError("interaction is not exist")

        if exist_process is not None:
            process.step = exist_process.step + 1
        else:
            process.step = 0

        db.add(Raw(**process.to_dict()))
        db.commit()

    @classmethod
    def search_many_raws(cls, db: Session, interaction_id: str):
        """search many raws

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:
            list[XAgentRaw]: interaction process list
        """
        processes = db.query(Raw).filter(
            Raw.interaction_id == interaction_id, Raw.is_deleted.is_(False)).order_by(Raw.step.asc()).all()
        return processes

    @classmethod
    def get_raw(cls, db: Session, interaction_id: str, node_id: str):
        """
        get raw by interaction id and node id
        """
        process = db.query(Raw).filter(
            Raw.interaction_id == interaction_id, Raw.node_id == node_id, Raw.is_deleted.is_(False)).first()
        return process

    @classmethod
    def get_next_send(cls, db: Session, interaction_id: str):
        """
        get next send process

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:
            XAgentRaw: interaction process
        """
        processes = db.query(Raw).filter(Raw.interaction_id == interaction_id,
                                         Raw.is_send.is_(False),
                                         Raw.is_deleted.is_(False)).order_by(Raw.step.desc()).all()
        return processes

    @classmethod
    def update_send_flag(cls, db: Session, interaction_id: str, node_id: str):
        """
        update send flag, if send success, update flag
        if send flag is True, it means that the process has been sent
        and no longer needs to be sent

        Args:
            db (Session): db session
            interaction_id (str): interaction id
            node_id (str): node id

        Returns:
            None

        Raises:
            XAgentError: process is not exist
        """
        process = db.query(Raw).filter(
            Raw.interaction_id == interaction_id, Raw.node_id == node_id).first()
        if process is None:
            raise XAgentError("process is not exist")
        process.is_send = True
        process.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()

    @classmethod
    def update_receive_flag(cls, db: Session, interaction_id: str, node_id: str):
        """
        update receive flag, if receive success, update flag
        if this flag is True, it means that the process has been received from human

        Args:
            db (Session): db session
            interaction_id (str): interaction id
            node_id (str): node id

        Returns:
            None

        Raises:
            XAgentError: process is not exist
        """
        process = db.query(Raw).filter(
            Raw.interaction_id == interaction_id, Raw.node_id == node_id).first()
        if process is None:
            raise XAgentError("process is not exist")
        process.is_receive = True
        process.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()

    @classmethod
    def update_human_data(cls, db: Session, interaction_id: str, node_id: str, human_data: dict):
        """
        update human data

        Args:
            db (Session): db session
            interaction_id (str): interaction id
            node_id (str): node id
            human_data (dict): human data

        Returns:
            None

        Raises:
            XAgentError: process is not exist
        """
        process = db.query(Raw).filter(
            Raw.interaction_id == interaction_id, Raw.node_id == node_id, Raw.is_deleted.is_(False)).first()
        if process is None:
            raise XAgentError("process is not exist")
        process.is_receive = True
        process.is_human = True
        process.human_data = human_data
        db.commit()

    @classmethod
    def insert_error(cls, db: Session, interaction_id: str, message: str):
        """
        if interaction is failed, insert error message
        this message will be displayed in the interaction list

        Args:
            db (Session): db session
            interaction_id (str): interaction id
            message (str): error message

        Returns:
            None

        Raises:
            None

        """
        process = Raw(
            node_id=uuid.uuid4().hex,
            interaction_id=interaction_id,
            current="",
            step=0,
            data=message,
            file_list=[],
            status=StatusEnum.FAILED,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(process)
        db.commit()

    @classmethod
    def get_finish_status(cls, db: Session, interaction_id: str):
        """
        get interaction finish status

        Args:
            db (Session): db session
            interaction_id (str): interaction id

        Returns:
            Boolean: True or False
        """
        process = db.query(Raw).filter(
            Raw.interaction_id == interaction_id,
            Raw.is_deleted.is_(False),
            Raw.status == "finished").first()
        return process is not None
