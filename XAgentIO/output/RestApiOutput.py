from XAgentIO.output.base import BaseOutput


class RestApiOutput(BaseOutput):
    def __init__(self):
        super().__init__()

    def run(self, output):
        print(output)