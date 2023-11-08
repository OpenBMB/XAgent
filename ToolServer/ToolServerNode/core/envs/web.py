import httpx

from typing import Callable,Any,Coroutine,List
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from config import logger
from core.base import BaseEnv
from core.register import toolwrapper

@toolwrapper()
class WebEnv(BaseEnv):
    """Web Environment providing web interface and browsering.

    Attributes:
        bing_cfg (dict): Bing specific configurations.
        web_cfg (dict): Web specific configurations.
        headers (dict): HTTP headers used while making HTTP requests.
        client (httpx.AsyncClient): HTTP client used for making HTTP requests.
    """

    def __init__(self,config:dict = {}):
        """Initializes WebEnv with the provided configurations.

        Args:
            config (dict, optional): Configurations for WebEnv. Defaults to {}.
        """
        super().__init__(config=config)
        self.bing_cfg = self.config['bing']
        if self.bing_cfg['api_key'] is None:
            logger.warning("Bing API key is not provided, rollback to duckduckgo.")
        
        self.web_cfg = self.config['web']
        self.headers = {
            "User-Agent":self.web_cfg['user_agent']
        }
        self.client = httpx.AsyncClient(headers=self.headers,verify=False,timeout=30.0,http2=True)

    def _check_url_valid(self,url:str):
        """Checks if the provided URL is valid or not

        Args:
            url (str): URL to check.

        Raises:
            ValueError: If the URL is a local URL or if it is not a http or https URL.
        """
        local_prefixes = [
            "file:///",
            "file://127.0.0.1",
            "file://localhost",
            "http://localhost",
            "https://localhost",
            "http://2130706433",
            "https://2130706433",
            "http://127.0.0.1",
            "https://127.0.0.1",
            "https://0.0.0.0",
            "http://0.0.0.0",
            "http://0000",
            "https://0000",
        ]
        if any(url.startswith(prefix) for prefix in local_prefixes):
            raise ValueError(f"URL {url} is a local url, blocked!")
        if not (url.startswith("http") or url.startswith("file")):
            raise ValueError(f"URL {url} is not a http or https url, please give a valid url!")
        
    async def search_and_browse(self, search_query:str,goals_to_browse:str,region:str=None,num_results = 3) -> List[str]:
        """Search with search tools and browse the website returned by search. Note some websites may not be accessable due to network error.
        
        

        Args:
            search_query (str): The search query.
            goals_to_browse (str): What's you want to find on the website returned by search.
            region (str, optional): The region code of the search. Defaults to 'en-US'.
            num_results (int, optional): Number of results to fetch. Defaults to 3.

        Returns:
            List[str]: The results of the search.

        Raises:
            httpx.HTTPStatusError: If there's an HTTP error while making the request.
            Exception: For any other unhandled exceptions.

        """

        api_key = self.bing_cfg["api_key"]
        endpoint = self.bing_cfg["endpoint"]
        if region is None:
            region = 'en-US'
        if api_key is None:
            pages = [{
                'name':ret['title'],
                'snippet':ret['body'],
                'url':ret['href']
            } for ret in DDGS().text(search_query, region='wt-wt')]
            
        else:
            result = await self.client.get(endpoint,
                        headers={'Ocp-Apim-Subscription-Key': api_key},
                        params={'q': search_query, 'mkt': region },
                        timeout=10)
            result.raise_for_status()
            result = result.json()
            pages = result["webPages"]["value"]
            
        search_results = []

        for idx in range(min(len(pages),num_results)):
            try:
                page = await self.browse_website(pages[idx]['url'],goals_to_browse)
            except httpx.HTTPStatusError as e:
                page = e.response.text
            except Exception as e:
                page = str(e)
                
            message = {
                'name':pages[idx]['name'],
                'snippet':pages[idx]['snippet'],
                'page':page
            }
            search_results.append(message)

        return search_results
    
    async def browse_website(self,url:str,goals_to_browse:str)->str:
        """Gives a http or https url to browse a website and return the summarize text.

        Args:
            url (str): The real world Uniform Resource Locator (web address)
            goals_to_browse (str): The goals for browse the given `url` (e.g. what you want to find on webpage.)

        Returns:
            str: The content of the website, with formatted text.

        Raises:
            httpx.HTTPStatusError: If there's an HTTP error while making the request.

        """

        # self._check_url_valid(url)
        res = await self.client.get(url)
        if res.status_code in [301,302,307,308]:
            res = await self.client.get(res.headers['location'])
        else:
            res.raise_for_status()
        
        soup = BeautifulSoup(res.text,"html.parser")
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        links = soup.find_all('a')
        if len(links) > 0:
            text += '\n\nLinks:\n'
            for link in links:
                if link.string != None and link.get('href')!= None:
                    # print(''.join(link.string.split()),link.get('href'))
                    striped_link_string = link.string.strip()
                    if striped_link_string != '' and  link.get('href').startswith('http'):
                        text += f"{striped_link_string} ({link.get('href')})\n"
        
        return text