"""XAgent Running Recorder Util"""
from contextlib import contextmanager
import datetime
import os
import time
import json
import re
from colorama import Fore
from XAgent.workflow.base_query import AutoGPTQuery
from XAgent.config import XAgentConfig
from XAgentServer.database.connect import SessionLocal
from XAgentServer.loggers.logs import Logger
from XAgentServer.models.recorder import XAgentRunningRecord
from XAgentServer.application.cruds.recorder import RunningRecordCRUD
from XAgentServer.enums.recorder_type import RecorderTypeEnum



def dump_common_things(object):
    """common"""
    if type(object) in [str, int, float, bool]:
        return object
    if isinstance(object, dict):
        return {dump_common_things(key): dump_common_things(value) for key, value in object.items()}
    if isinstance(object, list):
        return [dump_common_things(cont) for cont in object]
    method = getattr(object, 'to_json', None)
    if callable(method):
        return method()


@contextmanager
def get_db():
    """
    Provide a transactional scope around a series of operations.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class RunningRecoder():
    """A class used to record the running sequences of the program, also including program query status and config data.
    """

    def __init__(self, record_id: str, newly_start=True, root_dir=None, logger: Logger=None):
        self.record_id = record_id
        self.record_root_dir = root_dir
        if not os.path.exists(self.record_root_dir):
            os.makedirs(self.record_root_dir, exist_ok=True)

        self.newly_start = newly_start  # 是全新启动的
        self.logger = logger
        self.query = {}
        self.config = {}

        self.llm_interface_id = 0
        self.toolserver_interface_id = 0

        self.tool_call_id = 0
        self.plan_refine_id = 0

        self.llm_server_cache = []
        self.tool_server_cache = []
        self.tool_call_cache = []
        self.plan_refine_cache = []

        self.now_subtask_id = None

    def change_now_task(self, new_subtask_id):
        """change now task"""
        self.now_subtask_id = new_subtask_id
        self.tool_call_id = 0
        self.plan_refine_id = 0

    def generate_record(self, current, node_id, node_type, data):
        """generate a recorder"""
        self.logger.typewriter_log(title="-=-=-=-=-=-=-=Recorder Start-=-=-=-=-=-=-=\n",
                                   title_color=Fore.GREEN,
                                   content=f"Current: {current} Node: {node_type} {node_id}")
        json_str = json.dumps(data, ensure_ascii=False, indent=4)
        json_str=re.sub(r'"api_key": "(.+?)"', r'"api_key": "**"', json_str)
        self.logger.typewriter_log(title="-=-=-=-=-=-=-=Data -=-=-=-=-=-=-=\n",
                                   title_color=Fore.GREEN,
                                   content=json_str)
        self.logger.typewriter_log(title="-=-=-=-=-=-=-=Recorder End-=-=-=-=-=-=-=",
                                   title_color=Fore.GREEN,
                                   content="")

        return XAgentRunningRecord(
            record_id=self.record_id,
            current=current,
            node_id=node_id,
            node_type=node_type,
            data=data,
            create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            is_deleted=False,
        )


    def regist_plan_modify(self,
                           refine_function_name,
                           refine_function_input,
                           refine_function_output,
                           plan_after):
        """注册一个plan_refine的记录"""
        plan_refine_record = {
            "refine_function_name": dump_common_things(refine_function_name),
            "refine_function_input": dump_common_things(refine_function_input),
            "refine_function_output": dump_common_things(refine_function_output),
            "plan_after": dump_common_things(plan_after),
        }
        record = self.generate_record(
            current=self.now_subtask_id,
            node_id=self.plan_refine_id,
            node_type=RecorderTypeEnum.PLAN_REFINE,
            data=plan_refine_record,
        )


        with get_db() as db:
            RunningRecordCRUD.insert_record(db=db, record=record)
        self.plan_refine_id += 1

    def regist_llm_inout(self,
                         messages,
                         functions,
                         function_call,
                         model,
                         stop,
                         other_args,
                         output_data):
        """注册一个llm_inout的记录"""
        llm_inout_record = {
            "input": {
                "messages": dump_common_things(messages),
                "functions": dump_common_things(functions),
                "function_call": dump_common_things(function_call),
                "model": dump_common_things(model),
                "stop": dump_common_things(stop),
                "other_args": dump_common_things(other_args),
            },
            "output": dump_common_things(output_data),
            "llm_interface_id": self.llm_interface_id,
        }
        record = self.generate_record(
            current=self.now_subtask_id,
            node_id=self.llm_interface_id,
            node_type=RecorderTypeEnum.LLM_INPUT_PAIR,
            data=llm_inout_record,
        )
        with get_db() as db:
            RunningRecordCRUD.insert_record(db=db, record=record)
        self.llm_interface_id += 1

    def query_llm_inout(self, restrict_cache_query, messages, functions, function_call, model, stop, other_args):
        """restrict_cache_query: 是否要求llm_interface_id也一样

        """
        if self.newly_start:
            return None
        input_data = {
            "messages": dump_common_things(messages),
            "functions": dump_common_things(functions),
            "function_call": dump_common_things(function_call),
            "model": dump_common_things(model),
            "stop": dump_common_things(stop),
            "other_args": dump_common_things(other_args),
        }
        for cache in self.llm_server_cache:
            if input_data == cache["input"]:
                if restrict_cache_query and self.llm_interface_id != cache["llm_interface_id"]:
                    continue

                # import pdb; pdb.set_trace()
                return cache["output"]
        return None

    def regist_tool_call(self,
                         tool_name,
                         tool_input,
                         tool_output,
                         tool_status_code,
                         thought_data=None):
        """代管tool server上的所有操作
        """
        tool_record = {
            "tool_name": dump_common_things(tool_name),
            "tool_input": dump_common_things(tool_input),
            "tool_output": dump_common_things(tool_output),
            "tool_status_code": dump_common_things(tool_status_code),
        }
        if thought_data:
            tool_record["thought"] = dump_common_things(thought_data)

        record = self.generate_record(
            current=self.now_subtask_id,
            node_id=self.tool_call_id,
            node_type=RecorderTypeEnum.TOOL_CALL,
            data=tool_record,
        )
        with get_db() as db:
            RunningRecordCRUD.insert_record(db=db, record=record)

        self.tool_call_id += 1

    def regist_tool_server(self,
                           url,
                           payload,
                           tool_output,
                           response_status_code):
        """
        Register tool server.

        Args:
            url (str): The url of the server.
            payload (Any): The payload for the tool.
            tool_output (Any): The output from the tool.
            response_status_code (int): The response status code.
        """
        tool_record = {
            "url": dump_common_things(url.split("/")[-1]),
            "payload": dump_common_things(payload),
            "response_status_code": dump_common_things(response_status_code),
            "tool_output": dump_common_things(tool_output),
        }
        record = self.generate_record(
            current=self.now_subtask_id,
            node_id=self.toolserver_interface_id,
            node_type=RecorderTypeEnum.TOOL_SERVER_PAIR,
            data=tool_record,
        )
        with get_db() as db:
            RunningRecordCRUD.insert_record(db=db, record=record)

        self.toolserver_interface_id += 1

    def query_tool_server_cache(self, url, payload):
        """query tool server cache"""
        if self.newly_start:
            return None

        if not self.tool_server_cache:
            with get_db() as db:
                tool_record = RunningRecordCRUD.get_record_by_type(
                    db=db,
                    record_id=self.record_id,
                    node_id=0,
                    node_type=RecorderTypeEnum.TOOL_SERVER_PAIR,
                )

            self.tool_server_cache = [json.loads(
                record.data) for record in tool_record]

        for cache in self.tool_server_cache:
            # import pdb; pdb.set_trace()
            if cache["url"] == url.split("/")[-1] \
                    and cache["payload"] == dump_common_things(payload):
                print(f"get a tool_server response from Record: {cache['tool_output']}")
                return cache["tool_output"]

        return None

    def regist_query(self, query):
        """记录query的相关信息
        """
        record = self.generate_record(
            current=self.now_subtask_id,
            node_id=0,
            node_type=RecorderTypeEnum.QUERY,
            data=query.to_json(),
        )
        with get_db() as db:
            RunningRecordCRUD.insert_record(db=db, record=record)

    def get_query(self):
        """get query from db"""
        with get_db() as db:
            records = RunningRecordCRUD.get_record_by_type(
                db=db,
                record_id=self.record_id,
                node_id=0,
                node_type=RecorderTypeEnum.QUERY,
            )

        self.query = AutoGPTQuery.from_json(records[0].data)
        return self.query

    def regist_config(self, config: XAgentConfig):
        """记录config的相关信息
        """
        record = self.generate_record(
            current=self.now_subtask_id,
            node_id=0,
            node_type=RecorderTypeEnum.CONFIG,
            data=config.to_dict(),
        )
        with get_db() as db:
            RunningRecordCRUD.insert_record(db=db, record=record)

    def get_config(self):
        """get running config from db"""
        with get_db() as db:
            records = RunningRecordCRUD.get_record_by_type(
                db=db,
                record_id=self.record_id,
                node_id=0,
                node_type=RecorderTypeEnum.CONFIG,
            )
        return json.loads(records[0].data)

    def load_from_db(self, record_id):
        """从本地文件夹加载record，用于后面的直接复现
        """

        self.newly_start = False

        with get_db() as db:
            records = RunningRecordCRUD.get_record_by_type(
                db=db,
                record_id=record_id
            )

        for record in records:
            if record.node_type == RecorderTypeEnum.QUERY:
                self.query = AutoGPTQuery.from_json(record.data)
            elif record.node_type == RecorderTypeEnum.CONFIG:
                self.config = XAgentConfig()
                self.config.merge_from_dict(record.data)
            elif record.node_type == RecorderTypeEnum.LLM_INPUT_PAIR:
                self.llm_server_cache.append(record.data)
            elif record.node_type == RecorderTypeEnum.TOOL_SERVER_PAIR:
                self.tool_server_cache.append(record.data)
            elif record.node_type == RecorderTypeEnum.PLAN_REFINE:
                self.plan_refine_cache.append(record.data)
            elif record.node_type == RecorderTypeEnum.TOOL_CALL:
                self.tool_call_cache.append(record.data)
            else:
                raise NotImplementedError
