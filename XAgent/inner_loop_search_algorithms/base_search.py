import abc
from colorama import Fore

from XAgent.logs import logger
from XAgent.utils import SearchMethodStatusCode
from XAgent.data_structure.node import ToolNode

class BaseSearchMethod(metaclass = abc.ABCMeta):
    def __init__(self):
        logger.typewriter_log(
            f"Constructing a searching method:",
            Fore.YELLOW,
            self.__class__.__name__,
        )
        self.status: SearchMethodStatusCode = SearchMethodStatusCode.DOING
        self.need_for_plan_refine: bool = False

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def to_json(self):
        pass
    
    @abc.abstractmethod
    def get_finish_node(self):
        pass

    def status(self):
        return self.status

    