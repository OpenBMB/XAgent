"""XAgent Running Recorder Type Enum"""


class RecorderTypeEnum:
    """XAgent Running Recorder Type Enum
    """
    QUERY = "query"
    CONFIG = "config"
    LLM_INPUT_PAIR = "llm_input_pair"
    TOOL_SERVER_PAIR = "tool_server_pair"
    NOW_SUBTASK_ID = "now_subtask_id"
    TOOL_CALL = "tool_call"
    PLAN_REFINE = "plan_refine"
    LLM_SERVER_CACHE = "llm_server_cache"
    TOOL_SERVER_CACHE = "tool_server_cache"
    TOOL_CALL_CACHE = "tool_call_cache"
    PLAN_REFINE_CACHE = "plan_refine_cache"
    LLM_INTERFACE_ID = "llm_interface_id"
    TOOL_SERVER_INTERFACE_ID = "toolserver_interface_id"
    TOOL_CALL_ID = "tool_call_id"
    