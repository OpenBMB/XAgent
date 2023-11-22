"""XAgentRaw Object"""
import abc
import json


class XAgentRaw(metaclass=abc.ABCMeta):
    """XAgent Raw Object"""

    def __init__(self, node_id: str,
                 interaction_id: str,
                 current: str,
                 step: int,
                 data: dict,
                 file_list: list,
                 status: str,
                 do_interrupt: bool,
                 wait_seconds: int,
                 ask_for_human_help: bool,
                 create_time: str,
                 update_time: str,
                 is_deleted: bool,
                 is_human: bool,
                 human_data: dict,
                 human_file_list: list,
                 is_send: bool,
                 is_receive: bool,
                 include_pictures: bool = False,):
        self.node_id = node_id
        self.interaction_id = interaction_id
        self.current = current
        self.step = step
        self.data = data
        self.file_list = file_list
        self.status = status
        self.do_interrupt = do_interrupt
        self.wait_seconds = wait_seconds
        self.ask_for_human_help = ask_for_human_help
        self.create_time = create_time
        self.update_time = update_time
        self.is_deleted = is_deleted
        self.is_human = is_human
        self.human_data = human_data
        self.human_file_list = human_file_list
        self.is_send = is_send
        self.is_receive = is_receive
        self.include_pictures = include_pictures

    def to_dict(self):
        """XAgent Raw Object to dict"""
        return {
            "node_id": self.node_id,
            "interaction_id": self.interaction_id,
            "current": self.current,
            "step": self.step,
            "data": self.data,
            "file_list": self.file_list,
            "status": self.status,
            "do_interrupt": self.do_interrupt,
            "wait_seconds": self.wait_seconds,
            "ask_for_human_help": self.ask_for_human_help,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "is_deleted": self.is_deleted,
            "is_human": self.is_human,
            "human_data": self.human_data,
            "human_file_list": self.human_file_list,
            "is_send": self.is_send,
            "is_receive": self.is_receive,
            "include_pictures": self.include_pictures
        }

    def to_json(self):
        """XAgent Raw Object to json"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_data):
        """XAgent Raw Object from json"""
        return cls(**json_data)

    def update(self, update_data: dict):
        """XAgent Raw Object update"""
        for k, v in update_data.items():
            setattr(self, k, v)
        return self

    @classmethod
    def from_db(cls, db_data):
        """XAgent Raw Object from db"""
        return cls(
            node_id=db_data.node_id,
            interaction_id=db_data.interaction_id,
            current=db_data.current,
            step=db_data.step,
            data=db_data.data,
            file_list=db_data.file_list,
            status=db_data.status,
            do_interrupt=db_data.do_interrupt,
            wait_seconds=db_data.wait_seconds,
            ask_for_human_help=db_data.ask_for_human_help,
            create_time=db_data.create_time,
            update_time=db_data.update_time,
            is_deleted=db_data.is_deleted,
            is_human=db_data.is_human,
            human_data=db_data.human_data,
            human_file_list=db_data.human_file_list,
            is_send=db_data.is_send,
            is_receive=db_data.is_receive,
            include_pictures=db_data.include_pictures
        )
