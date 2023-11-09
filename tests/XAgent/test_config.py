from XAgent.config import XAgentConfig


def test_xagent_config_to_dict_safely():
    config = XAgentConfig()

    config["key1"] = "value1"
    config["key2"] = "value2"
    config["api_keys"] = ["agasegeas", "gaeges"]

    result = config.to_dict(safe=True)

    # api_keys should be ignored internally.
    expected_result = {
        "key1": "value1",
        "key2": "value2",
    }
    assert result == expected_result
