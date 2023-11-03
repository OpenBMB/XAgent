from XAgentIO.input.base import BaseInput


class HttpInput(BaseInput):
    def __init__(self):
        super().__init__()

    def run(self):
        raise NotImplementedError
