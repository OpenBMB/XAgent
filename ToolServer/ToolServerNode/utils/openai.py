import os
import json
import openai
import random
import logging

from copy import deepcopy
from config import CONFIG
from typing import List,Dict,Any
from tenacity import wait_random_exponential,stop_after_attempt,retry

logger = logging.getLogger(CONFIG['logger'])

class OpenaiPoolRequest:
    """
    Handles all OpenAI requests by dispatching them to the API endpoints.

    Attributes:
        openai_cfg: Configuration dictionary containing OpenAI parameters.
        pool: list of dictionaries, where each dictionary has all the required details of an endpoint.
    """
    def __init__(self,):
        """
        Initializes the OpenaiPoolRequest class by setting the configuration and loading the pool.
        """
        self.openai_cfg = deepcopy(CONFIG['openai'])
        
        self.pool:List[Dict] = []
        
        __pool_file = self.openai_cfg['key_pool_json']
        if os.environ.get('API_POOL_FILE',None) is not None:
            __pool_file = os.environ.get('API_POOL_FILE')
        
        if os.path.exists(__pool_file):
            self.pool = json.load(open(__pool_file))
        
        if os.environ.get('OPENAI_KEY',None) is not None:
            self.pool.append({
                'api_key':os.environ.get('OPENAI_KEY'),
                'organization':os.environ.get('OPENAI_ORG',None),
                'api_type':os.environ.get('OPENAI_TYPE',None),
                'api_version':os.environ.get('OPENAI_VER',None)
            })
        if len(self.pool) == 0:
            logger.warning('No openai api key found! Some functions will be disable!')

    @retry(wait=wait_random_exponential(multiplier=1, max=10), stop=stop_after_attempt(5),reraise=True)
    async def request(self,messages,**kwargs) -> Dict[str, Any]:
        """
        Sends a request to the OpenAI and gets a response.

        Args:
            messages: Payload to be sent to OpenAI.
            kwargs: Optional arguments that the function takes.

        Returns:
            A dictionary containing the response from the OpenAI.

        Raises:
            Exception: If the attempt to reach the endpoint exceed limit.
        """
        
        chat_args:dict = deepcopy(self.openai_cfg['chat_args'])
        chat_args.update(kwargs)

        item = random.choice(self.pool)
        chat_args['api_key'] = item['api_key']
        if 'organization' in item:
            chat_args['organization'] = item['organization']
        if 'api_type' in item:
            chat_args['api_type'] = item['api_type']
        if 'api_version' in item:
            chat_args['api_version'] = item['api_version']

        return await openai.ChatCompletion.acreate(messages=messages,**chat_args)
    
    async def __call__(self,messages,**kwargs) -> Dict[str, Any]:
        """
        Makes a request to the OpenAI by calling the instance of the class.

        Args:
            messages: Payload to be sent to OpenAI.
            kwargs: Optional arguments that the function takes.

        Returns:
            A dictionary containing the response from the OpenAI.

        Raises:
            Exception: If there are no API keys available in the pool.
        """
        if len(self.pool)==0:
            raise Exception('No openai api key found! OPENAI_PR Disabled!')
        return await self.request(messages,**kwargs)
    
OPENAI_PR = OpenaiPoolRequest()

