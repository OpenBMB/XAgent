import os
import time
import json
import yaml
import uuid
import logging
from copy import deepcopy
from colorama import Fore, Style
from XAgent.logs import logger
from XAgent.workflow.base_query import AutoGPTQuery
from XAgent.config import XAgentConfig, CONFIG


def dump_common_things(object):
    """
    Serialize commonly used data types, like str, int, float, bool, dictionaries, and lists.

    Args:
        object (Any): The object to serialize.

    Returns:
        object: The cpickled object.
    """
    if type(object) in [str, int, float, bool]:
        return object
    if type(object) == dict:
        return {dump_common_things(key): dump_common_things(value) for key, value in object.items()}
    if type(object) == list:
        return [dump_common_things(cont) for cont in object]
    method = getattr(object, 'to_json', None)
    if callable(method):
        return method()

class RunningRecoder():
    """
    A class used to record the running sequences of the program, also including program query status and config data.

    Attributes:
        record_root_dir (str): The root directory of the running records.
        newly_start (bool): A flag to indicate whether or not a new task has started.
        toolserver_interface_id (int): The id of the tool server interface.
        tool_call_id (int): The id of the tool call.
        plan_refine_id (int): The id of the plan refinement.
        llm_server_cache (dict): The cache for the llm server.
        tool_server_cache (dict): The cache for the tool server.
        tool_call_cache (dict): The cache for the tool call.
        plan_refine_cache (dict): The cache for the plan refinement.
        query_count (int): The count of the queries.
    """
    def __init__(self, record_root_dir="./running_records/"):
        """
        Initialize the RunningRecorder.

        Args:
            record_root_dir (str): The root directory of the running records.
        """
        now = int(round(time.time() * 1000))
        strip = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(now / 1000)) + uuid.uuid4().hex[:8]

        self.record_root_dir = os.path.join(record_root_dir, strip)
        os.makedirs(self.record_root_dir, exist_ok=True)

        for subdir_name in ["LLM_inout_pair", "tool_server_pair"]:
            os.makedirs(os.path.join(self.record_root_dir, subdir_name), exist_ok=True)

        self.newly_start = True  

        self.toolserver_interface_id = 0

        self.tool_call_id = 0
        self.plan_refine_id = 0

        self.llm_server_cache = []
        self.tool_server_cache = []
        self.tool_call_cache = []
        self.plan_refine_cache = []

        self.query_count = 0

    def get_query_id(self):
        """
        Get the query id.

        Returns:
            int: The id of the query.
        """
        query_id = deepcopy(self.query_count)
        self.query_count += 1
        return query_id

    def decrease_query_id(self):
        """
        Decrease the query id.
        """
        self.query_count -= 1
    
    def change_now_task(self, new_subtask_id):
        """
        Change the current subtask.

        Args:
            new_subtask_id (int): The id of the new subtask.
        """
        self.now_subtask_id = new_subtask_id
        self.tool_call_id = 0
        self.plan_refine_id = 0

    def regist_plan_modify(self, refine_function_name, refine_function_input, refine_function_output, plan_after):
        """
        Register plan modification.

        Args:
            refine_function_name (str): The name of the refine function.
            refine_function_input (Any): The input of the refine function.
            refine_function_output (Any): The output of the refine function.
            plan_after (str): The plan after modification.
        """
        os.makedirs(os.path.join(self.record_root_dir, self.now_subtask_id), exist_ok=True)
        with open(
                os.path.join(self.record_root_dir, self.now_subtask_id, f"plan_refine_{self.plan_refine_id:05d}.json"),"w",encoding="utf-8") as writer:
            plan_refine_record = {
                "refine_function_name": dump_common_things(refine_function_name),
                "refine_function_input": dump_common_things(refine_function_input),
                "refine_function_output": dump_common_things(refine_function_output),
                "plan_after": dump_common_things(plan_after),
            }
            json.dump(plan_refine_record, writer, indent=2, ensure_ascii=False)

        self.plan_refine_id += 1
    def regist_llm_inout(self, llm_query_id, messages, functions=None, function_call=None, model=None, stop=None, output_data=None,**other_args):
        """
        Register llm input output pairs.

        Args:
            llm_query_id (int): The id of the llm query.
            messages (Any): The messages communicated.
            functions (list, optional): The list of functions used.
            function_call (Any, optional): The function called.
            model (Any, optional): The model used.
            stop (bool, optional): A flag to indicate whether or not to stop.
            output_data (Any, optional): The output data.
            other_args (dict, optional): Other arguments.
        """
        with open(os.path.join(self.record_root_dir, "LLM_inout_pair", f"{llm_query_id:05d}.json"),"w",encoding="utf-8") as writer:
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
                "llm_interface_id": llm_query_id,
            }
            json.dump(llm_inout_record, writer, indent=2, ensure_ascii=False)
            self.llm_server_cache.append(llm_inout_record)
            logger.typewriter_log("LLM inout registed:",Fore.RED, f"query-id={llm_query_id}",level=logging.DEBUG)

    def query_llm_inout(self, llm_query_id, messages, functions=None, function_call=None, model=None, stop=None, **other_args):
        """
        Query llm input and output pairs.

        Args:
            llm_query_id (int): The id of the llm query.
            messages (Any): The messages communicated.
            functions (list, optional): The list of functions used.
            function_call (Any, optional): The function called.
            model (Any, optional): The model used.
            stop (bool, optional): A flag to indicate whether or not to stop.
            other_args (dict, optional): Other arguments.

        Returns:
            Any: The output data.
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
        if llm_query_id >= len(self.llm_server_cache):
            logger.typewriter_log("Reach the max length of record")
            return None
        cache = self.llm_server_cache[llm_query_id]
        if input_data == cache["input"]:
            logger.typewriter_log(
                "get a llm_server response from Record",
                Fore.BLUE,
                f"query-id={llm_query_id}"
            )
            return cache["output"]
        
        return None

    def regist_tool_call(self, tool_name, tool_input, tool_output, tool_status_code, thought_data=None):
        """
        Register tool call.

        Args:
            tool_name (str): The name of the tool.
            tool_input (Any): The input for the tool.
            tool_output (Any): The output from the tool.
            tool_status_code (int): The status code of the tool.
            thought_data (Any, optional): The thought data.
        """
        os.makedirs(os.path.join(self.record_root_dir, self.now_subtask_id), exist_ok=True)
        with open(os.path.join(self.record_root_dir, self.now_subtask_id, f"tool_{self.tool_call_id:05d}.json"),"w",encoding="utf-8",) as writer:
            tool_record = {
                "tool_name": dump_common_things(tool_name),
                "tool_input": dump_common_things(tool_input),
                "tool_output": dump_common_things(tool_output),
                "tool_status_code": dump_common_things(tool_status_code),
            }
            if thought_data:
                tool_record["thought"] = dump_common_things(thought_data)
            json.dump(tool_record, writer, indent=2, ensure_ascii=False)

        self.tool_call_id += 1

    def regist_tool_server(self, url, payload, tool_output,  response_status_code):
        """
        Register tool server.

        Args:
            url (str): The url of the server.
            payload (Any): The payload for the tool.
            tool_output (Any): The output from the tool.
            response_status_code (int): The response status code.
        """
        with open(os.path.join(self.record_root_dir, "tool_server_pair", f"{self.toolserver_interface_id:05d}.json"),"w",encoding="utf-8",) as writer:
            tool_record = {
                "url": dump_common_things(url.split("/")[-1]),
                "payload": dump_common_things(payload),
                "response_status_code": dump_common_things(response_status_code),
                "tool_output": dump_common_things(tool_output),
            }
            json.dump(tool_record, writer, indent=2, ensure_ascii=False)

        self.toolserver_interface_id += 1

    def query_tool_server_cache(self, url, payload):
        """
        Query the tool server.

        Args:
            url (str): The url of the server.
            payload (Any): The payload to send.

        Returns:
            dict: The output from the tool server and the response status code.
        """
        if self.newly_start:
            return None
        if self.toolserver_interface_id >= len(self.tool_server_cache):
            return None

        cache = self.tool_server_cache[self.toolserver_interface_id]

        if cache["url"] == url.split("/")[-1] and cache["payload"] == dump_common_things(payload):
            logger.typewriter_log(
                "get a tool_server response from Record",
                Fore.BLUE,
                cache["url"],
            )
            return {
                "tool_output": cache["tool_output"], 
                "response_status_code": cache["response_status_code"]
            }

        return None


    def regist_query(self, query):
        """
        Register a query.

        Args:
            query (AutoGPTQuery): The query to register.
        """
        with open(os.path.join(self.record_root_dir, f"query.json"), "w",encoding="utf-8",) as writer:
            json.dump(query.to_json(), writer, indent=2, ensure_ascii=False)

    def get_query(self):
        """
        Get the registered query.

        Returns:
            AutoGPTQuery: The registered query.
        """
        logger.typewriter_log(
            "load a query from Record",
            Fore.BLUE,
        )
        return self.query

    def regist_config(self, config: XAgentConfig):
        """
        Register a configuration.

        Args:
            config (XAgentConfig): The configuration to register.
        """
        with open(os.path.join(self.record_root_dir, f"config.yml"), "w",encoding="utf-8") as writer:
            writer.write(yaml.safe_dump(dict(config.to_dict(safe=True)), allow_unicode=True))


    def get_config(self):
        """
        Get the registered configuration.

        Returns:
            XAgentConfig: The registered configuration.
        """
        logger.typewriter_log(
            "load a config from Record",
            Fore.BLUE,
        )
        return self.config

    def regist_father_info(self, record_dir):
        """
        Register father info.

        Args:
            record_dir (str): The directory of the record.
        """
        with open(os.path.join(self.record_root_dir, f"This-Is-A-Reload-Run.yml"), "w",encoding="utf-8") as writer:
            writer.write(yaml.safe_dump({
                "load_record_dir": record_dir,
            }, allow_unicode=True))

    def load_from_disk(self, record_dir):
        """
        Load from a record in disk.

        Args:
            record_dir (str): The directory of the record.
        """
        logger.typewriter_log(
            "load from a disk record, overwrite all the existing config-info",
            Fore.BLUE,
            record_dir,
        )
        self.regist_father_info(record_dir)
        self.newly_start = False

        for dir_name in os.listdir(record_dir):
            if dir_name == "query.json":
                with open(os.path.join(record_dir, dir_name), "r",encoding="utf-8") as reader:
                    self.query_json = json.load(reader)
                    self.query = AutoGPTQuery.from_json(self.query_json)
            elif dir_name == "config.yml":
                CONFIG.reload(os.path.join(record_dir, dir_name))
            elif dir_name == "LLM_inout_pair":
                inout_count = len(os.listdir(os.path.join(record_dir, dir_name)))
                self.llm_server_cache = [None]*inout_count
                for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                    inout_id = int(file_name.split(".")[0])
                    with open(os.path.join(record_dir, dir_name, file_name), "r",encoding="utf-8") as reader:
                        llm_pair = json.load(reader)
                        self.llm_server_cache[inout_id] = llm_pair
                logger.typewriter_log(
                    f"Record contain {inout_count} LLM inout",
                    Fore.BLUE,
                )
            elif dir_name == "tool_server_pair":
                inout_count = len(os.listdir(os.path.join(record_dir, dir_name)))
                self.tool_server_cache = [None]*inout_count
                for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                    inout_id = int(file_name.split(".")[0])
                    with open(os.path.join(record_dir, dir_name, file_name), "r",encoding="utf-8") as reader:
                        tool_pair = json.load(reader)
                        self.tool_server_cache[inout_id] = tool_pair
                logger.typewriter_log(
                    f"Record contain {len(os.listdir(os.path.join(record_dir, dir_name)))} Tool call",
                    Fore.BLUE,
                )
            elif os.path.isdir(os.path.join(record_dir, dir_name)):
                for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                    if file_name.startswith("plan_refine"):
                        with open(os.path.join(record_dir, dir_name, file_name),encoding="utf-8") as reader:
                            plan_refine = json.load(reader)
                            self.plan_refine_cache.append(plan_refine)
                    elif file_name.startswith("tool"):
                        with open(os.path.join(record_dir, dir_name, file_name),encoding="utf-8") as reader:
                            tool_call = json.load(reader)
                            self.tool_call_cache.append(tool_call)
                    else:
                        raise NotImplementedError


recorder = RunningRecoder()