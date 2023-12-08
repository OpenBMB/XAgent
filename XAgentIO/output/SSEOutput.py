from XAgentIO.output.base import BaseOutput


class SSEOutput(BaseOutput):
    """
    A class used represent Server-Sent-Events output.

    This class inherits from the BaseOutput class and overrides its run method to provide functionality
    for Server-Sent-Events (SSE) output.

    Methods
    -------
    run(output):
        Prints the output data.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the SSEOutput object.

        It inherits all the attributes from its superclass.
        """
        super().__init__()

    def run(self, output):
        """
        Prints the output data. This is an overridden method from its superclass.

        Args:
            output (Any): output data that needs to be printed.
        """
        print(output)