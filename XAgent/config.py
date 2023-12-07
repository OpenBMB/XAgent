
import os
import yaml
from copy import deepcopy


class XAgentConfig(dict):
    """
    A dictionary-like configuration class with attribute-style access.

    Inherited from dictionary, this class provides methods for accessing and modifying
    dictionary items using attributes and methods.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize class instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        """
        Access the class attribute.

        Args:
            key (str): Key to access the class attribute.

        Returns:
            Value of the class attribute for the input key.

        Raises:
            AttributeError: If the input key is not present in the dictionary.
        """
        if key in self:
            return self[key]
        raise AttributeError(f"'DotDict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        """
        Set the value of the class attribute.

        Args:
            key (str): Key for the attribute to set.
            value : Value to be set for the input key.
        """
        self[key] = value

    def __delattr__(self, key):
        """
        Delete the class attribute.

        Args:
            key (str): Key of the attribute to delete.

        Raises:
            AttributeError: If the input key is not present in the dictionary.
        """
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"'DotDict' object has no attribute '{key}'")

    def to_dict(self, safe=False):
        """
        Convert the xAgentConfig object to dictionary.

        Args:
            safe (bool, optional): If True, 'api_keys' will be excluded from the output.
                Default is False.

        Returns:
            dict: Dictionary representation of the instance.
        """
        if safe:
            right_value = deepcopy(self)
            right_value.pop("api_keys", "")
            return right_value
        else:
            return self

    def reload(self, config_file='assets/config.yml'):
        """
        Load configuration data from YAML file and environment variables. And also update
        the ARGS with new data.

        Args:
            config_file (str, optional): Path to the YAML configuration file.
                Default is 'assets/config.yml'.
        """
        config_file = os.getenv('CONFIG_FILE', config_file)
        print('---config file---\n'+str(config_file))
        self.__init__(
            **yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader))
        # check environment variables
        self['selfhost_toolserver_url'] = os.getenv(
            'TOOLSERVER_URL', self['selfhost_toolserver_url'])
        print('---args---\n'+str(ARGS))
        self.update(ARGS)

    @staticmethod
    def get_default_config(config_file='assets/config.yml'):
        """
        Get default configuration data from given file through environment variable.

        Args:
            config_file (str, optional): Path to the YAML configuration file.
                Default is 'assets/config.yml'.

        Returns:
            XAgentConfig: An instance of XAgentConfig with loaded configuration data.
        """
        try:
            config_file = os.getenv('CONFIG_FILE', config_file)
            cfg = yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader)
        except:
            cfg = {}
        return XAgentConfig(**cfg)


CONFIG = XAgentConfig.get_default_config()
ARGS = {}


def get_model_name(model_name: str = None):
    """
    Get the normalized model name for a given input model name.

    Args:
        model_name (str, optional): Input model name. Default is None.

    Returns:
        str: Normalized model name.

    Raises:
        Exception: If the model name is not recognized.
    """
    if model_name is None:
        model_name = CONFIG.default_completion_kwargs['model']

    normalized_model_name = ''
    match model_name.lower():
        case 'gpt-4':
            normalized_model_name = 'gpt-4'
        case 'gpt-4-32k':
            normalized_model_name = 'gpt-4-32k'
        case 'gpt-4-1106-preview':
            normalized_model_name = 'gpt-4-1106-preview'
        case 'gpt-4-turbo':
            normalized_model_name = 'gpt-4-1106-preview'
        case 'gpt-3.5-turbo-16k':
            normalized_model_name = 'gpt-3.5-turbo-16k'
        case 'gpt-3.5-turbo-1106':
            normalized_model_name = 'gpt-3.5-turbo-1106'

        case 'gpt4':
            normalized_model_name = 'gpt-4'
        case 'gpt4-32':
            normalized_model_name = 'gpt-4-32k'
        case 'gpt-35-16k':
            normalized_model_name = 'gpt-3.5-turbo-16k'
        case 'xagentllm':
            normalized_model_name = 'xagentllm'
        case _:
            raise Exception(f"Unknown model name {model_name}")

    return normalized_model_name


def get_apiconfig_by_model(model_name: str) -> dict:
    """
    Get API configuration for a model by its name.

    The function first normalizes the name, then fetches the API keys for this model
    from the CONFIG and rotates the keys.

    Args:
        model_name (str): Name of the model.

    Returns:
        dict: Dictionary containing the fetched API configuration.
    """
    normalized_model_name = get_model_name(model_name)
    apiconfig = deepcopy(CONFIG.api_keys[normalized_model_name][0])
    CONFIG.api_keys[normalized_model_name].append(
        CONFIG.api_keys[normalized_model_name].pop(0))
    return apiconfig
