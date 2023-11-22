import os
import yaml
import logging
from typing import Dict, Any


class ManagerConfig:
    """
    A class used to manage configuration settings.

    Attributes:
        cfg (Dict): Dictionary holding configuration settings read from file and environment.
    """

    def __init__(self, config_file_path="./assets/config/monitor.yml"):
        """
        Initializes ManagerConfig with configuration settings read from a YAML file 
        and overrides these settings with environment variables if they exist.

        Args:
            config_file_path (str, optional): Location of YAML configuration file. Defaults to "./assets/config.yml".
        """
        self.cfg: Dict = yaml.load(open(config_file_path, "r", encoding="utf-8").read(), Loader=yaml.FullLoader)

        for k in os.environ.keys():
            if k in self.cfg:
                self.cfg[k] = os.environ[k]  # overwrite the config with environment variables

    def __getitem__(self, key):
        """
        Override built-in function to enable indexing of ManagerConfig objects directly.

        Args:
            key (str): Configuration setting key. 

        Returns:
            Any: The value associated with the provided key.
        """
        return self.cfg[key]

    def dict(self) -> Dict[str, Any]:
        """
        Returns the internal dictionary holding configuration settings.

        Returns:
            Dict[str, Any]: Configuration settings dictionary.
        """
        return self.cfg

    def update(self, new_config: Dict) -> None:
        """
        Updates the configuration settings with the provided new_config dictionary. 

        Args:
            new_config (Dict): A dictionary with new configuration settings.
        """
        self.cfg.update(new_config)


CONFIG = ManagerConfig()
logger = logging.getLogger(CONFIG['logger'])
logger.setLevel(CONFIG['logger_level'])
console_handler = logging.StreamHandler()
console_handler.setLevel(CONFIG['logger_level'])
console_handler.setFormatter(logging.Formatter('%(levelname)s:\t %(message)s'))
logger.addHandler(console_handler)