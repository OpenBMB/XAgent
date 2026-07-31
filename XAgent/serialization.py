from datetime import date, datetime


def to_json_compatible(value):
    """Recursively convert runtime values into JSON-compatible data."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {
            to_json_compatible(key): to_json_compatible(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [to_json_compatible(item) for item in value]

    method = getattr(value, "to_json", None)
    if callable(method):
        return to_json_compatible(method())
    return str(value)


def parse_serialized_value(value, loads):
    """Deserialize text while preserving values already decoded by a client."""
    if isinstance(value, (str, bytes, bytearray)):
        return loads(value)
    return value
