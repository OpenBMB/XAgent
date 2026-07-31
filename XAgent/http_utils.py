def toolserver_request_timeout(config) -> tuple[float, float]:
    """Return short connect and configurable long read timeouts."""
    read_timeout = float(config.get("toolserver_request_timeout", 600))
    return 10.0, read_timeout
