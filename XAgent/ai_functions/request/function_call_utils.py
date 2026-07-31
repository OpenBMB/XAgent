import json
import re


def _extract_json_object(content: str):
    if not content:
        return None

    fenced_blocks = re.findall(
        r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.DOTALL | re.IGNORECASE
    )
    candidates = fenced_blocks + [content[content.find("{") :]]
    decoder = json.JSONDecoder()
    for candidate in candidates:
        if not candidate:
            continue
        try:
            value, _ = decoder.raw_decode(candidate.strip())
        except (TypeError, ValueError):
            continue
        if isinstance(value, dict):
            return value
    return None


def recover_function_call_from_content(content: str, functions: list[dict]):
    """Recover common JSON tool-call output emitted as assistant content."""
    payload = _extract_json_object(content)
    if payload is None:
        return None

    if "tool_name" in payload:
        for function in functions:
            properties = function.get("parameters", {}).get("properties", {})
            if "tool_call" not in properties:
                continue
            arguments = {
                "plan": [f"Call {payload['tool_name']} to continue the task."],
                "thought": "The model selected a tool in its text response.",
                "reasoning": content[:4000],
                "criticism": "",
                "tool_call": {
                    "tool_name": payload["tool_name"],
                    "tool_input": payload.get("tool_input", {}),
                },
            }
            return {
                "name": function["name"],
                "arguments": json.dumps(arguments, ensure_ascii=False),
            }

    if len(functions) == 1:
        return {
            "name": functions[0]["name"],
            "arguments": json.dumps(payload, ensure_ascii=False),
        }
    return None
