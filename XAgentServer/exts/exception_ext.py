"""Exception definitions for XAgentServer"""


class XAgentError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message="XAgent Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentTimeoutError(XAgentError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentTimeout!"):
        self.message = message
        super().__init__(self.message)


class XAgentCloseError(XAgentError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentClose!"):
        self.message = message
        super().__init__(self.message)

class XAgentWebSocketError(XAgentError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentWebSocket Error!"):
        self.message = message
        super().__init__(self.message)

class XAgentWebSocketTimeoutError(XAgentWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentWebSocket Timeout!"):
        self.message = message
        super().__init__(self.message)


class XAgentWebSocketDisconnectError(XAgentWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentWebSocket Disconnect!"):
        self.message = message
        super().__init__(self.message)


class XAgentWebSocketConnectError(XAgentWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentWebSocket Connect Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentWebSocketCloseError(XAgentWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentWebSocket Close!"):
        self.message = message
        super().__init__(self.message)


class XAgentWebSocketSendError(XAgentWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentWebSocket Send Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentWebSocketReceiveError(XAgentWebSocketError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgentWebSocket Receive Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentFileError(XAgentError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent File Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentDownloadFileError(XAgentFileError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Download File Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentWorkspaceFileError(XAgentFileError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent Workspace File Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentUploadFileError(XAgentFileError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent Workspace Upload File Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentDBError(XAgentError):
    """Exception raised because of DB error

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent DB Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentAuthError(XAgentError):
    """Exception raised because of auth error

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent Auth Error!"):
        self.message = message
        super().__init__(self.message)
     

class XAgentRunningError(XAgentError):
    """Exception raised because of Running error

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent Running Error!"):
        self.message = message
        super().__init__(self.message)


class XAgentWebError(XAgentError):
    """Exception raised because of Running error

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="XAgent WEB Error!"):
        self.message = message
        super().__init__(self.message)
