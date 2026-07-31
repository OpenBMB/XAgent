from datetime import date, datetime

from XAgent.serialization import to_json_compatible


def test_to_json_compatible_serializes_dates_recursively():
    value = {
        "api_version": date(2023, 7, 1),
        "created_at": datetime(2023, 7, 1, 12, 30),
        "nested": [date(2024, 1, 2)],
    }

    assert to_json_compatible(value) == {
        "api_version": "2023-07-01",
        "created_at": "2023-07-01T12:30:00",
        "nested": ["2024-01-02"],
    }
