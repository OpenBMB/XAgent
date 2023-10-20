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
            right_value.pop("openai_keys","")
            return right_value
        else:
            return self
    
    def reload(self,config_file='config.yml'):
        self.__init__(**yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader))
    
    @staticmethod
    def get_default_config(config_file='config.yml'):
        try:
            cfg = yaml.load(open(config_file, 'r'), Loader=yaml.FullLoader)
        except:
            cfg = {}
        return XAgentConfig(**cfg)

CONFIG = XAgentConfig.get_default_config()

def get_openai_model_name(model_name:str):
    openai_model_name = ''
    match model_name.lower():
        case 'gpt-4':
            openai_model_name = 'gpt-4'
        case 'gpt-4-32k':
            openai_model_name = 'gpt-4-32k'
        case 'gpt-3.5-turbo-16k':
            openai_model_name = 'gpt-3.5-turbo-16k'
            
        case 'gpt4':
            openai_model_name = 'gpt-4'
        case 'gpt4-32':
            openai_model_name = 'gpt-4-32k'
        case 'gpt-35-16k':
            openai_model_name = 'gpt-3.5-turbo-16k'
        case _:
            raise Exception(f"Unknown model name {model_name}")
    return openai_model_name

def get_apiconfig_by_model(model_name: str) -> dict:
    openai_model_name = get_openai_model_name(model_name)
    apiconfig = deepcopy(CONFIG.openai_keys[openai_model_name][0])
    CONFIG.openai_keys[openai_model_name].append(CONFIG.openai_keys[openai_model_name].pop(0))
    return apiconfig

