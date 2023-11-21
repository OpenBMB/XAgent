"""DB Interface: Recorder"""
import abc

from sqlalchemy.orm import Session

from XAgentServer.database.models import RunningRecord
from XAgentServer.models.recorder import XAgentRunningRecord


class RecordDBInterface(metaclass=abc.ABCMeta):
    """Recorder DB Interface

    Args:
        RecorderBaseInterface (_type_): _description_
        metaclass (_type_, optional): _description_. Defaults to abc.ABCMeta.
    """

    @classmethod
    def get_record_list(cls, db: Session, record_id: str) -> list[XAgentRunningRecord]:
        """get all records

        Args:
            db (Session): db

        Returns:
            list[XAgentRunningRecord]: Recorder list
        """
        records = db.query(RunningRecord).filter(
            RunningRecord.record_id == record_id).all()
        return [XAgentRunningRecord.from_db(Recorder) for Recorder in records]

    @classmethod
    def get_record(cls,
                     db: Session,
                     record_id: str | None = None
                     ) -> XAgentRunningRecord | None:
        """get Recorder by Recorder_id or email

        Args:
            db (Session): db
            Recorder_id (str | None, optional): Recorder id. Defaults to None.
            email (str | None, optional): email. Defaults to None.

        Returns:
            XAgentRunningRecord | None: Recorder, if Recorder is not exist, return None
        """
        record = db.query(RunningRecord).filter(RunningRecord.record_id == record_id,
                                                  RunningRecord.deleted.is_(False)).first()

        return XAgentRunningRecord.from_db(record) if record else None

    @classmethod
    def insert_record(cls,
                      db: Session,
                      record: XAgentRunningRecord):
        """insert Recorder

        Args:
            db (Session): db
            record (XAgentRunningRecord): Recorder
        """
        db_record = RunningRecord(**record.to_dict())
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @classmethod
    def get_record_by_type(cls,
                           db: Session,
                           record_id: str,
                           node_id: str = "",
                           node_type: str = "") -> list[XAgentRunningRecord]:
        """get Recorder by type

        Args:
            db (Session): db
            record_id (str): record id
            node_id (str): node id
            node_type (str): node type

        Returns:
            list[XAgentRunningRecord]: Recorder list
        """

        filters = [RunningRecord.deleted.is_(False)]

        if record_id:
            filters.append(RunningRecord.record_id == record_id)

        if node_id:
            filters.append(RunningRecord.node_id == node_id)

        if node_type:
            filters.append(RunningRecord.node_type == node_type)

        records = db.query(RunningRecord).filter(*filters).all()

        return [XAgentRunningRecord.from_db(Recorder) for Recorder in records]
