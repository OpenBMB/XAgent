from XAgentIO.input.CommandLineInput import CommandLineInput
from XAgentIO.input.base import BaseInput
from XAgentIO.output.CommandLineOutput import CommandLineOutput
from XAgentIO.output.base import BaseOutput


class XAgentIO:
    """
    A class to represent the input and output settings of the XAgent.

    It takes an input and an output as arguments which should be
    instances of the BaseInput and BaseOutput classes respectively.

    If the specified input/output is not given or incorrect, 
    CommandLineInput/CommandLineOutput instance is used.

    Attributes:
        Input: An instance of the BaseInput class to take input.
        Output: An instance of the BaseOutput class to give output.
        logger: The logging instance used.
    """

    def __init__(self, input: BaseInput, output: BaseOutput) -> None:
        """
        Initializes XAgent's input and output settings.

        Args:
            input (BaseInput): An instance of BaseInput class to be used for taking input.
            output (BaseOutput): An instance of BaseOutput class to be used for giving output.

        Raises:
            TypeError: If the input is not an instance of BaseInput.
            TypeError: If the output is not an instance of BaseOutput.
        """
        
        if input is None:
            self.Input = CommandLineInput()
        else:
            if not isinstance(input, BaseInput):
                raise TypeError("input must be a BaseInput instance")
            
        self.Input = input

        if output is None:
            self.Output = CommandLineOutput()
        else:
            if not isinstance(output, BaseOutput):
                raise TypeError("output must be a BaseOutput instance")
            
        self.Output = output


    def set_logger(self, logger):
        """
        Set the logger for the XAgentIO instance and the 
        input and output instances as well.

        Args:
            logger: Logging instance to be set.
        """
        self.logger = logger
        self.Input.set_logger(logger)
        self.Output.set_logger(logger)

    def close(self):
        """
        Closes the Input and Output for the current XAgentIO instance.
        """
        self.Input.close()
        self.Output.close()