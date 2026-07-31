import importlib.util
import json
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "XAgent"
    / "ai_functions"
    / "request"
    / "function_call_utils.py"
)
SPEC = importlib.util.spec_from_file_location("function_call_utils", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
recover_function_call_from_content = MODULE.recover_function_call_from_content


SUBTASK_HANDLE = {
    "name": "subtask_handle",
    "parameters": {
        "properties": {
            "plan": {"type": "array"},
            "thought": {"type": "string"},
            "reasoning": {"type": "string"},
            "criticism": {"type": "string"},
            "tool_call": {"type": "object"},
        }
    },
}


def test_recovers_text_tool_call_as_subtask_handle():
    content = """I will write the report.
```json
{"tool_name": "FileSystemEnv_write_to_file", "tool_input": {"filepath": "a.md"}}
```"""

    function_call = recover_function_call_from_content(
        content, [SUBTASK_HANDLE]
    )
    arguments = json.loads(function_call["arguments"])

    assert function_call["name"] == "subtask_handle"
    assert arguments["tool_call"] == {
        "tool_name": "FileSystemEnv_write_to_file",
        "tool_input": {"filepath": "a.md"},
    }
