from abc import ABCMeta, abstractmethod
import asyncio

from XAgentIO.exception import XAgentIOCloseError


class BaseInput(metaclass=ABCMeta):
    """
    An abstract base class that serves as an interface for classes interacting with external inputs.
    
    Attributes:
        do_interrupt: (bool) flag indicating whether to perform an interrupt after a certain period.
        max_wait_seconds: (int) maximum wait time in seconds if the input is set to interrupt.
        logger: (Object) standard Python logger used for logging.

    Methods:
        set_wait(self, do_interrupt: bool = True): Sets the `do_interrupt` attribute of the object
        set_logger(self, logger): Sets the logger used by the object.
        interrupt(self): An abstract method. Implementation should provide behavior to interrupt the input process.
        run(self): An abstract method. Implementation should provide behavior to initiate a process.
        close(self): Closes the connection, and raises an exception if unsuccessful.
    """

    def __init__(self, do_interrupt: bool = False, max_wait_seconds: int = 600):
        """
        Constructor of the BaseInput class.

        Args:
            do_interrupt: (bool, optional) flag indicating whether to perform an interrupt after a certain 
            period. Defaults to False.
            max_wait_seconds: (int, optional) maximum wait time in seconds if the input is interrupt.
            Defaults to 600.
        """
        self.do_interrupt = do_interrupt
        if self.do_interrupt:
            self.max_wait_seconds = max_wait_seconds

    def set_wait(self, do_interrupt: bool = True):
        """
        Sets the `do_interrupt` attribute of the object.

        Args:
            do_interrupt: flag indicating whether to perform an interrupt after a certain period. Defaults to True.
        """
        self.do_interrupt = do_interrupt

    def set_logger(self, logger):
        """
        Sets the logger used by the object.

        Args:
            logger: A standard Python logger to be used for logging messages.
        """
        self.logger = logger

    @abstractmethod
    async def interrupt(self):
        """
        An abstract method. When overridden in a derived class, it should provide behavior 
        to interrupt the input process at a regular time interval.

        Raises:
            NotImplementedError: If the method is not overridden in a derived class.
        """
        raise NotImplementedError 

    @abstractmethod
    def run(self):
        """
        An abstract method. When overridden in a derived class, it should provide behavior 
        to initiate a process.

        Raises:
            NotImplementedError: If the method is not overridden in a derived class.
        """
        raise NotImplementedError
    
    def close(self):
        """
        Closes the connection.

        Raises:
            XAgentIOCloseError: If there is an issue during closing operation.
        """
        # raise XAgentIOCloseError("close connection!")
        pass