import os
import time
import json
import uuid
from colorama import Fore, Style
from XAgent.loggers.logs import logger
from XAgent.workflow.base_query import AutoGPTQuery
from XAgent.config import XAgentConfig


def dump_common_things(object):
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

    def __init__(self, record_root_dir="./running_records/"):
        now = int(round(time.time() * 1000))
        strip = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(now / 1000)) + uuid.uuid4().hex[:8]

        self.record_root_dir = os.path.join(record_root_dir, strip)
        os.makedirs(self.record_root_dir, exist_ok=True)

        for subdir_name in ["LLM_inout_pair", "tool_server_pair"]:
            os.makedirs(os.path.join(self.record_root_dir, subdir_name), exist_ok=True)

        self.newly_start = True  

        self.llm_interface_id = 0
        self.tool_server_interface_id = 0

        self.tool_call_id = 0
        self.plan_refine_id = 0

        self.llm_server_cache = []
        self.tool_server_cache = []
        self.tool_call_cache = []
        self.plan_refine_cache = []

    def change_now_task(self, new_subtask_id):
        self.now_subtask_id = new_subtask_id
        self.tool_call_id = 0
        self.plan_refine_id = 0

    def regist_plan_modify(self, refine_function_name, refine_function_input, refine_function_output, plan_after):
        os.makedirs(os.path.join(self.record_root_dir, self.now_subtask_id), exist_ok=True)
        with open(
                os.path.join(self.record_root_dir, self.now_subtask_id, f"plan_refine_{self.plan_refine_id:05d}.json"),
                "w") as writer:
            plan_refine_record = {
                "refine_function_name": dump_common_things(refine_function_name),
                "refine_function_input": dump_common_things(refine_function_input),
                "refine_function_output": dump_common_things(refine_function_output),
                "plan_after": dump_common_things(plan_after),
            }
            json.dump(plan_refine_record, writer, indent=2, ensure_ascii=False)

        self.plan_refine_id += 1

    def regist_llm_inout(self, messages, functions, function_call, model, stop, other_args, output_data):
        with open(os.path.join(self.record_root_dir, "LLM_inout_pair", f"{self.llm_interface_id:05d}.json"),
                  "w") as writer:
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
            json.dump(llm_inout_record, writer, indent=2, ensure_ascii=False)
            self.llm_server_cache.append(llm_inout_record)

        self.llm_interface_id += 1

    def query_llm_inout(self, restrict_cache_query, messages, functions, function_call, model, stop, other_args):
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
                logger.typewriter_log(
                    "get a llm_server response from Record",
                    Fore.RED,
                )
                # import pdb; pdb.set_trace()
                return cache["output"]
        return None

    def regist_tool_call(self, tool_name, tool_input, tool_output, tool_status_code, thought_data=None):
        os.makedirs(os.path.join(self.record_root_dir, self.now_subtask_id), exist_ok=True)
        with open(os.path.join(self.record_root_dir, self.now_subtask_id, f"tool_{self.tool_call_id:05d}.json"),
                  "w") as writer:
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

    def regist_tool_server(self, url, payload, output):
        with open(os.path.join(self.record_root_dir, "tool_server_pair", f"{self.tool_server_interface_id:05d}.json"),
                  "w") as writer:
            tool_record = {
                "url": dump_common_things(url.split("/")[-1]),
                "payload": dump_common_things(payload),
                "tool_output": dump_common_things(output),
            }
            json.dump(tool_record, writer, indent=2, ensure_ascii=False)

        self.tool_server_interface_id += 1

    def query_tool_server_cache(self, url, payload):
        if self.newly_start:
            return None
        for cache in self.tool_server_cache:
            # import pdb; pdb.set_trace()
            if cache["url"] == url.split("/")[-1] and cache["payload"] == dump_common_things(payload):
                logger.typewriter_log(
                    "get a tool_server response from Record",
                    Fore.RED,
                    cache["url"],
                )
                return cache["tool_output"]

        return None

    def regist_query(self, query):
        with open(os.path.join(self.record_root_dir, f"query.json"), "w") as writer:
            json.dump(query.to_json(), writer, indent=2, ensure_ascii=False)

    def get_query(self):
        logger.typewriter_log(
            "load a query from Record",
            Fore.RED,
        )
        return self.query

    def regist_config(self, config: XAgentConfig):
        with open(os.path.join(self.record_root_dir, f"config.json"), "w") as writer:
            json.dump(config.to_dict(), writer, indent=2, ensure_ascii=False)

    def get_config(self):
        logger.typewriter_log(
            "load a config from Record",
            Fore.RED,
        )
        return self.config

    def load_from_disk(self, record_dir):
        logger.typewriter_log(
            "load from a disk record",
            Fore.RED,
            record_dir,
        )

        self.newly_start = False

        for dir_name in os.listdir(record_dir):
            if dir_name == "query.json":
                with open(os.path.join(record_dir, dir_name), "r") as reader:
                    self.query_json = json.load(reader)
                    self.query = AutoGPTQuery.from_json(self.query_json)
            elif dir_name == "config.json":
                with open(os.path.join(record_dir, dir_name), "r") as reader:
                    self.config_json = json.load(reader)
                    self.config = XAgentConfig()
                    self.config.merge_from_dict(self.config_json)
            elif dir_name == "LLM_inout_pair":
                for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                    with open(os.path.join(record_dir, dir_name, file_name), "r") as reader:
                        llm_pair = json.load(reader)
                        self.llm_server_cache.append(llm_pair)
            elif dir_name == "tool_server_pair":
                for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                    with open(os.path.join(record_dir, dir_name, file_name), "r") as reader:
                        tool_pair = json.load(reader)
                        self.tool_server_cache.append(tool_pair)
            else:
                for file_name in os.listdir(os.path.join(record_dir, dir_name)):
                    if file_name.startswith("plan_refine"):
                        with open(os.path.join(record_dir, dir_name, file_name)) as reader:
                            plan_refine = json.load(reader)
                            self.plan_refine_cache.append(plan_refine)
                    elif file_name.startswith("tool"):
                        with open(os.path.join(record_dir, dir_name, file_name)) as reader:
                            tool_call = json.load(reader)
                            self.tool_call_cache.append(tool_call)
                    else:
                        raise NotImplementedError

recorder = RunningRecoder()