import abc
from colorama import Fore, Style
from XAgent.logs import logger


class BaseQuery(metaclass = abc.ABCMeta):
    """
    Base class for Query object. This class should be inherited by any other query class that will be used in the XAgent.

    Attributes:
        role_name (str): Name of the role involved in the query.
        task (str): Task that is being queried.
        plan (list): List of the plan details for the query.
    """

    def __init__(self, role_name="", task="", plan=[]):
        """
        Constructs all the necessary attributes for the BaseQuery object.

        Args:
            role_name (str, optional): Name of the role involved in the query.
            task (str, optional): Task that is being queried.
            plan (list, optional): List of the plan details for the query.
        """
        self.role_name = role_name
        self.task = task
        self.plan = plan

    @abc.abstractmethod
    def log_self(self):
        """
        Abstract method to log Query details. 
        This method should be implemented by all classes that inherit from BaseQuery.
        """
        pass

    def to_json(self):
        """
        Serializes the BaseQuery object into a JSON object.

        Returns:
            dict: A dictionary version of the BaseQuery object.
        """
        return {
            "task": self.task,
            "role_name": self.role_name,
            "plan": self.plan,
        }

    @classmethod
    def from_json(cls, json_data):
        """
        Construct a new BaseQuery object from a JSON object.

        Args:
            json_data (dict): The JSON object that will be used to construct the BaseQuery.

        Returns:
            BaseQuery: A new BaseQuery object constructed from the values in `json_data`.
        """
        return cls(**json_data)


class AutoGPTQuery(BaseQuery):
    """
    A specific type of query that inherits from the BaseQuery class.
    Used for specific GPT model actions.
    """

    def __init__(self,**args):
        """
        Constructs all the necessary attributes for the AutoGPTQuery object by inheriting from BaseQuery class.

        Args:
            **args: Variable length argument list which is a dictionary of attribute key-value pairs.
        """
        super().__init__(**args)

    def log_self(self):
        """
        Logs AutoGPTQuery details using logger.

        This method logs "Role", "Task" with role_name and task respectively.
        If there is any detail in the plan, it also logs "Plan" with each detail in the plan.
        """
        logger.typewriter_log("Role", Fore.YELLOW, self.role_name)
        logger.typewriter_log("Task", Fore.YELLOW, self.task)
        if self.plan != []:
            logger.typewriter_log("Plan", Fore.YELLOW)
            for k, plan in enumerate(self.plan):
                logger.typewriter_log(f"    {k+1}.{plan}", Style.RESET_ALL)