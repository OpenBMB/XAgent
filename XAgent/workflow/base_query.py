import abc
from colorama import Fore, Style


from XAgent.logs import logger


class BaseQuery(metaclass = abc.ABCMeta):
    def __init__(self, role_name="",task="",plan=[]):
        self.role_name = role_name
        self.task = task
        self.plan = plan
    @abc.abstractmethod
    def log_self(self):
        pass

    def to_json(self):
        return {
            "task": self.task,
            "role_name": self.role_name,
            "plan": self.plan,
        }

    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)



class AutoGPTQuery(BaseQuery):
    def __init__(self,**args):
        super().__init__(**args)

    def log_self(self):
        logger.typewriter_log("Role", Fore.YELLOW, self.role_name)
        logger.typewriter_log("Task", Fore.YELLOW, self.task)
        if self.plan != []:
            logger.typewriter_log("Plan", Fore.YELLOW)
            for k, plan in enumerate(self.plan):
                logger.typewriter_log(f"    {k+1}.{plan}", Style.RESET_ALL)