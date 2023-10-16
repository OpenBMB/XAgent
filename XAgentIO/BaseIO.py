from XAgentIO.input.CommandLineInput import CommandLineInput
from XAgentIO.input.base import BaseInput
from XAgentIO.output.CommandLineOutput import CommandLineOutput
from XAgentIO.output.base import BaseOutput


class XAgentIO:
    def __init__(self, input: BaseInput, output: BaseOutput) -> None:
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
        self.logger = logger
        self.Input.set_logger(logger)
        self.Output.set_logger(logger)

    def close(self):
        self.Input.close()
        self.Output.close()
