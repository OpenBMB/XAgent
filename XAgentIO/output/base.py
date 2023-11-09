from abc import ABCMeta, abstractmethod

from XAgentIO.exception import XAgentIOCloseError


class BaseOutput(metaclass=ABCMeta):
    """
    Abstract base class representing an output. The class object allows setting of
    logger and control of the execution process through run() and close() functions.
    
    Attributes:
        kwargs (dict): A dictionary containing the arguments for the output object.
        logger (object): Logger object to be used.
    """

    def __init__(self, kwargs: dict = None):
        """
        Initialize output object with the provided arguments.

        Args:
            kwargs (dict, optional): dictionary of arguments for the output object.
        """
        self.kwargs = kwargs

    def set_logger(self, logger):
        """
        Set the logger for this output object.

        Args:
            logger (object): Logger object to be set.
        """
        self.logger = logger

    @abstractmethod
    def run(self):
        """
        Executes the main functionality of the derived classes.
        Each derived class must implement this method.

        Raises:
            NotImplementedError: If the derived class does not implement this method.
        """
        raise NotImplementedError

    def close(self):
        """
        Close the output object. Does nothing in the base class, but
        can be overridden in subclasses to handle resources cleanup.

        Raises:
            XAgentIOCloseError: If an error occurs while closing the connection
        """
        # raise XAgentIOCloseError("close connection!")
        pass