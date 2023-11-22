import os
import yaml
import logging
from typing import Dict, Any, Union

class NodeConfig:
    """
    A class used to load and manage the configurations defined in a specified configuration file and the environment variables.

    Methods
    -------
    __getitem__(self, key):
        Fetches a configuration value for a given key.
    dict():
        Returns the entire configuration dictionary.
    update(new_config: Dict):
        Updates the configuration dictionary with new configurations.
    """
    def __init__(self,
                 config_file_path="./assets/config/node.yml",):
        """
        The constructor for NodeConfig class that loads the configuration details.

        Args:
          config_file_path (str, optional): The path to the configuration file. Defaults to "assets/config.yml".

        Raises:
          FileNotFoundError: If specified configuration file path could not be located.
          yaml.YAMLError: If there are syntax errors in the provided yaml configuration file.
        """
        self.cfg:Dict = yaml.load(open(config_file_path, "r", encoding="utf-8").read(), Loader=yaml.FullLoader)
        
        for k in os.environ.keys():
            if k in self.cfg:
                self.cfg[k] = os.environ[k] # overwrite the config with environment variables

    def __getitem__(self, key):
        """
        Fetches a configuration value for a given key.

        Args:
          key (str): The configuration key to fetch value for.
        
        Returns:
          Any: The value of the requested configuration key.
        
        Raises:
          KeyError: If the given key is not found in the configuration.
        """
        return self.cfg[key]
    
    def dict(self)-> Dict[str, Any]:
        """
        Returns the entire configuration dictionary.
        
        Returns:
          Dict[str, Any]: The entire configuration dictionary.
        """
        return self.cfg

    def update(self, new_config: Dict)-> None:
        """
        Updates the configuration dictionary with new configurations.

        Args:
          new_config (Dict): The new configurations dictionary to update the existing configurations.

        Returns:
          None
        """
        self.cfg.update(new_config)
        
CONFIG = NodeConfig()
logger = logging.getLogger(CONFIG['logger'])
logger.setLevel(CONFIG['logger_level'])