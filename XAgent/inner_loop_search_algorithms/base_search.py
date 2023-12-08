from colorama import Fore

from XAgent.logs import logger
from XAgent.utils import SearchMethodStatusCode

class BaseSearchMethod:
    """The base class for all search methods. It defines the common elements and actions that all search 
    methods have.
    
    Attributes:
        status (SearchMethodStatusCode): The status of the search method. It can be 'DOING', 'SUCCESS' or 'FAILED'.
        need_for_plan_refine (bool): A flag that indicates if the plan needs to be refined. It starts as False.
    """
    def __init__(self):
        """Initializes the search method instance and logs its creation."""
        logger.typewriter_log(
            f"Constructing a searching method:",
            Fore.YELLOW,
            self.__class__.__name__,
        )
        self.status: SearchMethodStatusCode = SearchMethodStatusCode.DOING
        self.need_for_plan_refine: bool = False

    def run(self):
        """A Placeholder function for running the search method. 
           This should be implemented by all search method subclasses.
        """
        pass

    def to_json(self):
        """A Placeholder function for creating a json representation of the search method. 
           This should be implemented by all search method subclasses.
        """
        pass
    
    def get_finish_node(self):
        """A Placeholder function for getting the final node of the search method run.
           This should be implemented by all search method subclasses.
        """
        pass

    def status(self):
        """Gets the current status of the search method.

        Returns:
            SearchMethodStatusCode: The current status of the search method.
        """
        return self.status
