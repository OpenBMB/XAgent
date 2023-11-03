from abc import ABCMeta, abstractmethod
import asyncio

from XAgentIO.exception import XAgentIOCloseError


class BaseInput(metaclass=ABCMeta):
    def __init__(self, do_interrupt: bool = False, max_wait_seconds: int = 600):
        self.do_interrupt = do_interrupt
        if self.do_interrupt:
            self.max_wait_seconds = max_wait_seconds

    def set_wait(self, do_interrupt: bool = True):
        self.do_interrupt = do_interrupt

    def set_logger(self, logger):
        self.logger = logger

    async def interrupt(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def close(self):
        # raise XAgentIOCloseError("close connection!")
        pass
