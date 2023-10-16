import requests

from config import CONFIG
from core.register import toolwrapper


bing_cfg = CONFIG['bing']

@toolwrapper()
def bing_search(query:str,region:str = None)->str|list[str]:
    """Return 3 most relevant results of a Bing search using the official Bing API. This tool does not provide website details, use other tools to browse website if you need.
    
    :param string query: The search query.
    :param string? region: The region code of the search, default to `en-US`. Available regions: `en-US`, `zh-CN`, `ja-JP`, `en-AU`, `en-CA`, `en-GB`, `de-DE`, `en-IN`, `en-ID`, `es-ES`, `fr-FR`, `it-IT`, `en-MY`, `nl-NL`, `en-NZ`, `en-PH`, `en-SG`, `en-ZA`, `sv-SE`, `tr-TR`.
    :return string: The results of the search.
    """
    #     :param int num_results: The number of results to return.
    
    num_results = 3
    endpoint = bing_cfg["endpoint"]
    api_key = bing_cfg["api_key"]
    if region is None:
        region = 'en-US'
    result = requests.get(endpoint, headers={'Ocp-Apim-Subscription-Key': api_key}, params={'q': query, 'mkt': region }, timeout=10)
    result.raise_for_status()
    result = result.json()

    pages = result["webPages"]["value"]
    search_results = []

    for idx in range(min(len(pages),num_results)):
        message = {
            'url':pages[idx]['url'],
            'name':pages[idx]['name'],
            'snippet':pages[idx]['snippet']
        }
        search_results.append(message)

    # Return the list of search result
    return search_results