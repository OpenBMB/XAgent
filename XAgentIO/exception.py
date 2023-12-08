class XAgentIOError(Exception):
    """The base class for exceptions in related to XAgent input/output (IO) operations."""
    
    pass


class XAgentIOInterruptError(XAgentIOError):
    """A type of XAgentIOError that's raised when an IO operation is interrupted.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO Interrupt!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOTimeoutError(XAgentIOError):
    """A type of XAgentIOError that's raised when an IO operation times out.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO Timeout!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOCloseError(XAgentIOError):
    """A type of XAgentIOError that's raised when an error occurs while closing an IO stream.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO Close!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketError(XAgentIOError):
    """A type of XAgentIOError that's raised for errors in websocket communications.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO WebSocket Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketTimeoutError(XAgentIOWebSocketError):
    """A type of XAgentIOWebSocketError that's raised when a websocket operation times out.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO WebSocket Timeout!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketDisconnectError(XAgentIOWebSocketError):
    """A type of XAgentIOWebSocketError that's raised when a websocket disconnects unexpectedly.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO WebSocket Disconnect!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketConnectError(XAgentIOWebSocketError):
    """A type of XAgentIOWebSocketError that's raised when a connection to a websocket cannot be established.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO WebSocket Connect Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketCloseError(XAgentIOWebSocketError):
    """A type of XAgentIOWebSocketError that's raised when a websocket cannot be closed properly.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO WebSocket Close!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketSendError(XAgentIOWebSocketError):
    """A type of XAgentIOWebSocketError that's raised when a message cannot be sent over a websocket.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO WebSocket Send Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentIOWebSocketReceiveError(XAgentIOWebSocketError):
    """A type of XAgentIOWebSocketError that's raised when a message cannot be received from a websocket.

    Attributes:
        message (str): An explanation of the error.
    """

    def __init__(self, message="XAgent IO WebSocket Receive Error!"):
        self.message = message
        super().__init__(self.message)