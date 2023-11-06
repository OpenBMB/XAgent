from XAgent.config import XAgentConfig


def test_xagent_config_to_dict_safely():
    # 创建一个XAgentConfig实例
    config = XAgentConfig()

    # 设置实例的属性和数据
    config['key1'] = 'value1'
    config['key2'] = 'value2'
    config['api_keys'] = ['agasegeas', 'gaeges']

    # 调用to_dict方法并获取结果
    result = config.to_dict(safe=True)

    # 断言结果是否与预期相符
    expected_result = {'key1': 'value1', 'key2': 'value2', }
    assert result == expected_result
