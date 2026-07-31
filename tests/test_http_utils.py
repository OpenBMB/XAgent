from XAgent.http_utils import toolserver_request_timeout


def test_toolserver_timeout_allows_slow_node_startup():
    assert toolserver_request_timeout({}) == (10.0, 600.0)
    assert toolserver_request_timeout(
        {"toolserver_request_timeout": 120}
    ) == (10.0, 120.0)
