import os
import yaml
import logging
from typing import Dict, Any


class ManagerConfig:
    def __init__(
        self,
        config_file_path="./assets/config.yml",
    ):
        self.cfg: Dict = yaml.load(
            open(config_file_path, "r", encoding="utf-8").read(), Loader=yaml.FullLoader
        )

        for k in os.environ.keys():
            if k in self.cfg:
                self.cfg[k] = os.environ[
                    k
                ]  # overwrite the config with environment variables

    def __getitem__(self, key):
        return self.cfg[key]

    def dict(self) -> Dict[str, Any]:
        return self.cfg

    def update(self, new_config: Dict) -> None:
        self.cfg.update(new_config)


CONFIG = ManagerConfig()
logger = logging.getLogger(CONFIG["logger"])
logger.setLevel(CONFIG["logger_level"])
console_handler = logging.StreamHandler()
console_handler.setLevel(CONFIG["logger_level"])
console_handler.setFormatter(logging.Formatter("%(levelname)s:\t %(message)s"))
logger.addHandler(console_handler)
