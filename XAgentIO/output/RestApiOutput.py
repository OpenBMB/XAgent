from XAgentIO.output.base import BaseOutput

class RestApiOutput(BaseOutput):
    """
    Class for handling the REST API outputs.

    This class extends from the BaseOutput class and it contains methods to handle output in REST API format.
    """

    def __init__(self):
        """
        Initializes the RestApiOutput instance by calling the BaseOutput's __init__ method.
        Here, the purpose of the method is to provide a clear initialization for the REST API output.
        """
        super().__init__()

    def run(self, output):
        """
        Method for processing and displaying the output.

        Args:
            output: The output data to be printed.

        Returns:
            None. It prints the received output to the console.
        """
        print(output)