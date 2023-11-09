from XAgentIO.exception import XAgentIOCloseError
from XAgentIO.output.base import BaseOutput

class CommandLineOutput(BaseOutput):
    """
    This class is derived from the 'BaseOutput' class and overrides its methods.
    It provides an interface for sending the output to the command line.
    Note that the close method raises an 'XAgentIOCloseError' exception.
    """

    def __init__(self):
        """
        Constructor for CommandLineOutput class. Calls base class constructor.
        """
        super().__init__()

    async def run(self, output):
        """
        Creates an asynchronous task to send the output to the command line.
        This is a placeholder function that needs to be implemented.

        Args:
            output (Any): The data to be output to the command line.
        """
        pass

    def close(self):
        """
        Closes the connection to the command line output. Note that this
        function always raises an 'XAgentIOCloseError' exception.

        Raises:
            XAgentIOCloseError: Exception indicating that a connection close 
            operation has happened.
        """
        raise XAgentIOCloseError("close connection!")