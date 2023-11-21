"""XAgentServer application cruds interaction module."""
import abc
from datetime import datetime
from typing import List
import uuid

from sqlalchemy.orm import Session

from XAgentServer.database.interface.interaction import InteractionDBInterface
from XAgentServer.exts.exception_ext import XAgentDBError
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.database.models import Raw
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.raw import XAgentRaw


class InteractionCRUD(metaclass=abc.ABCMeta):
    """
    interaction crud
    """

    @classmethod
    def search_many_interaction(cls, db: Session) -> list:
        """
        search many interaction
        """
        try:
            return InteractionDBInterface.search_many_interaction(db=db)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def get_interaction(cls, db: Session, interaction_id: str) -> InteractionBase | None:
        """
        get interaction
        Args:
            db: db
            interaction_id: interaction id
        Returns:
            interaction InteractionBase
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.get_interaction(db=db, interaction_id=interaction_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def create_interaction(cls, db: Session, base: InteractionBase):
        """
        create interaction
        Args:
            db: db
            base: base
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.create_interaction(db=db, base=base)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e
        
    @classmethod
    def get_ready_interaction(cls, db: Session, user_id: str):
        """
        create interaction
        Args:
            db: db
            user_id: user_id
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.get_ready_interaction(db=db, user_id=user_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e


    @classmethod
    def add_parameter(cls, db: Session, parameter: InteractionParameter = None):
        """
        add parameter
        Args:
            db: db
            parameter: parameter
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.add_parameter(db=db, parameter=parameter)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def get_parameter(cls, db: Session, interaction_id: str) -> list:
        """
        get parameter
        Args:
            db: db
            interaction_id: interaction id
        Returns:
            parameter list [InteractionParameter]
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.get_parameter(db=db, interaction_id=interaction_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e
        
        
    @classmethod
    def get_init_parameter(cls, db: Session, interaction_id: str) -> InteractionParameter:
        """
        get init parameter
        Args:
            db: db
            interaction_id: interaction id
        Returns:
            parameter InteractionParameter
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            parameters = InteractionDBInterface.get_parameter(db=db, interaction_id=interaction_id)
            init_parameter = parameters[0]
            parameter = InteractionParameter.from_json({"args": init_parameter, "interaction_id": interaction_id, "parameter_id": None})
            return parameter
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def search_interaction_by_user_id(cls,
                                   db: Session,
                                   user_id: str,
                                   page_size: int = 10,
                                   page_num: int = 1) -> list[dict]:
        """
        get interaction by user id
        Args:
            db: db
            user_id: user id
            page_size: page size
            page_num: page num
        Returns:
            interaction list [dict]
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        return InteractionDBInterface.search_interaction_by_user_id(db=db,
                                                        user_id=user_id,
                                                        page_size=page_size,
                                                        page_num=page_num)

    @classmethod
    def is_exist(cls, db: Session, interaction_id: str) -> bool:
        """
        interaction is exist
        Args:
            db: db
            interaction_id: interaction id
        Returns:
            True if interaction is exist, else False
        
        Raises:
            XAgentDBError: XAgent DB Error    
        """
        try:
            return InteractionDBInterface.is_exist(db=db, interaction_id=interaction_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def update_interaction(cls, db: Session, base_data: dict):
        """
        update interaction
        Args:
            db: db
            base_data: base data
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.update_interaction(db=db, base_data=base_data)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

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
            db: db
            interaction_id: interaction id
            status: status
            message: message
            current_step: current step
        
        Raises:
            XAgentDBError: XAgent DB Error    
        """
        try:
            InteractionDBInterface.update_interaction_status(
                db=db,
                interaction_id=interaction_id,
                status=status,
                message=message,
                current_step=current_step)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def update_interaction_parameter(cls,
                                     db: Session,
                                     interaction_id: str,
                                     parameter: InteractionParameter):
        """
        update interaction parameter
        Args:
            db: db
            interaction_id: interaction id
            parameter: parameter
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.update_interaction_parameter(
                db=db,
                interaction_id=interaction_id,
                parameter=parameter)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def is_running(cls, db: Session, user_id: str):
        """
        is running
        Args:
            db: db
            user_id: user id
        Returns:
            True if running, else False
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.is_running(db=db, user_id=user_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def delete_interaction(cls, db: Session, interaction_id: str):
        """
        delete interaction
        Args:
            db: db
            interaction_id: interaction id
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.delete_interaction(
                db=db, interaction_id=interaction_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def get_shared_interaction(cls,
                               db: Session,
                               interaction_id: str) -> InteractionBase | None:
        """
        get shared interaction
        Args:
            db: db
            interaction_id: interaction id
            Returns:
                interaction InteractionBase, if not found, return None
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.get_shared_interaction(
                db=db,
                interaction_id=interaction_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def search_many_shared(cls,
                           db: Session,
                           page_size: int = 20,
                           page_index: int = 1) -> list[dict]:
        """
        search many shared
        Args:
            db: db
            page_size: page size
            page_index: page index
        Returns:
            interaction list [dict]
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.search_many_shared(db=db,
                                                    page_size=page_size,
                                                    page_index=page_index)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def insert_raw(cls, db: Session, process: XAgentRaw):
        """
        insert raw
        Args:
            db: db
            process: process
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.insert_raw(db=db, process=process)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def search_many_raws(cls, db: Session, interaction_id: str) -> List[XAgentRaw] | None:
        """
        search many raws
        Args:
            db: db
            interaction_id: interaction id
        Returns:
            raw list [XAgentRaw]
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return [XAgentRaw.from_db(raw) for raw in 
                    InteractionDBInterface.search_many_raws(db=db, interaction_id=interaction_id)]
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def get_raw(cls, db: Session, interaction_id: str, node_id: str) -> XAgentRaw | None:
        """
        get raw
        Args:
            db: db
            interaction_id: interaction id
            node_id: node id
        Returns:
            raw XAgentRaw, if not found, return None
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.get_raw(db=db,
                                                  interaction_id=interaction_id,
                                                  node_id=node_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def get_next_send(cls, db: Session, interaction_id: str) -> List[Raw] | None:
        """
        get next send
        Args:
            db: db
            interaction_id: interaction id
        Returns:
            raw list [Raw]
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            return InteractionDBInterface.get_next_send(db=db, interaction_id=interaction_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def update_send_flag(cls, db: Session, interaction_id: str, node_id: str):
        """
        update send flag
        Args:
            db: db
            interaction_id: interaction id
            node_id: node id
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.update_send_flag(
                db=db, interaction_id=interaction_id, node_id=node_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def update_receive_flag(cls, db: Session, interaction_id: str, node_id: str):
        """
        update receive flag
        Args:
            db: db
            interaction_id: interaction id
            node_id: node id
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.update_receive_flag(
                db=db, interaction_id=interaction_id, node_id=node_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def update_human_data(cls,
                          db: Session,
                          interaction_id: str,
                          node_id: str,
                          human_data: dict):
        """
        update human data
        Args:
            db: db
            interaction_id: interaction id
            node_id: node id
            human_data: human data
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.update_human_data(db=db,
                                            interaction_id=interaction_id,
                                            node_id=node_id,
                                            human_data=human_data)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def insert_error(cls,
                     db: Session,
                     interaction_id: str,
                     message: str,
                     status: str = "failed"):
        """
        insert error
        Args:
            db: db
            interaction_id: interaction id
            message: message
            status: status, default is failed
        Returns:
            raw XAgentRaw
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            process = XAgentRaw(
                node_id=uuid.uuid4().hex,
                interaction_id=interaction_id,
                current="",
                step=0,
                data=message,
                file_list=[],
                status=status,
                do_interrupt=False,
                wait_seconds=0,
                ask_for_human_help=False,
                create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                is_deleted=False,
                is_human=False,
                human_data={},
                human_file_list=[],
                is_send=False,
                is_receive=False,
                include_pictures=False,
            )
            InteractionDBInterface.insert_raw(db=db, process=process)
            return process
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e

    @classmethod
    def add_share(cls, db: Session, share):
        """
        add share
        Args:
            db: db
            share: share
        
        Raises:
            XAgentDBError: XAgent DB Error
        """
        try:
            InteractionDBInterface.add_share(db=db, shared=share)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e
        
        
    @classmethod
    def get_finish_status(cls, db: Session, interaction_id: str) -> bool:
        """
        get finish status
        
        Args:
            db: db
            interaction_id: interaction id
            
        Returns:
            True if finish, else False
        """
        try:
            return InteractionDBInterface.get_finish_status(db=db, interaction_id=interaction_id)
        except Exception as e:
            raise XAgentDBError(f"XAgent DB Error [Interact Module]: {str(e)}") from e
