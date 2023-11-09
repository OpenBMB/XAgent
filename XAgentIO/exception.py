class XAgentIOError(Exception):
    """Base class for exceptions in this module."""

    pass


class XAgentIOInterruptError(XAgentIOError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO Interrupt!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOTimeoutError(XAgentIOError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO Timeout!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOCloseError(XAgentIOError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO Close!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketError(XAgentIOError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO WebSocket Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketTimeoutError(XAgentIOWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO WebSocket Timeout!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketDisconnectError(XAgentIOWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO WebSocket Disconnect!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketConnectError(XAgentIOWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO WebSocket Connect Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketCloseError(XAgentIOWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO WebSocket Close!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketSendError(XAgentIOWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO WebSocket Send Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketReceiveError(XAgentIOWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent IO WebSocket Receive Error!"):
        self.message = message
        super().__init__(self.message)
