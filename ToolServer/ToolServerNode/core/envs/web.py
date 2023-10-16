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
    """
    def __init__(self,config:dict = {}):
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
    
        :param string search_query: The search query.
        :param string goals_to_browse: What's you want to find on the website returned by search. If you need more details, request it in here. Examples: 'What is latest news about deepmind?', 'What is the main idea of this article?'
        :param string? region: The region code of the search, default to `en-US`. Available regions: `en-US`, `zh-CN`, `ja-JP`, `de-DE`, `fr-FR`, `en-GB`.
        :return string: The results of the search.
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
        """Give a http or https url to browse a website and return the summarize text. Note some websites may not be accessable due to network error. This tool only return the content of give url and cannot provide any information need interaction with the website.
        
        :param string url: The realworld Uniform Resource Locator (web address) to scrape text from. Never provide something like "<URL of the second news article>", give real url!!! Example: 'https://www.deepmind.com/'
        :param string goals_to_browse: The goals for browse the given `url` (e.g. what you want to find on webpage.). If you need more details, request it in here.
        :return string: The content of the website, with formatted text.
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