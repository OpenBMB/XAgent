import os
import yaml
from copy import deepcopy

class XAgentConfig(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'DotDict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"'DotDict' object has no attribute '{key}'")
    def to_dict(self, safe=False):
        if safe:
            right_value = deepcopy(self)
            right_value.pop("api_keys","")
            return right_value
        else:
            return self
    
    def reload(self,config_file='assets/config.yml'):
        config_file = os.getenv('CONFIG_FILE', config_file)
        print('---config file---\n'+str(config_file))
        self.__init__(**yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader))
        # check environment variables
        self['selfhost_toolserver_url'] = os.getenv('TOOLSERVER_URL', self['selfhost_toolserver_url'])
        print('---args---\n'+str(ARGS))
        self.update(ARGS)
        
    @staticmethod
    def get_default_config(config_file='assets/config.yml'):
        try:
            config_file = os.getenv('CONFIG_FILE', config_file)
            cfg = yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader)
        except:
            cfg = {}
        return XAgentConfig(**cfg)

CONFIG = XAgentConfig.get_default_config()
ARGS = {}

def get_model_name(model_name:str=None):
    if model_name is None:
        model_name = CONFIG.default_completion_kwargs['model']
    normalized_model_name = ''
    match model_name.lower():
        case 'gpt-4':
            normalized_model_name = 'gpt-4'
        case 'gpt-4-32k':
            normalized_model_name = 'gpt-4-32k'
        case 'gpt-3.5-turbo-16k':
            normalized_model_name = 'gpt-3.5-turbo-16k'
            
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
    normalized_model_name = get_model_name(model_name)
    apiconfig = deepcopy(CONFIG.api_keys[normalized_model_name][0])
    CONFIG.api_keys[normalized_model_name].append(CONFIG.api_keys[normalized_model_name].pop(0))
    return apiconfig

