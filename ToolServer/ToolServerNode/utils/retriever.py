import os
import re
import json
import tqdm
import requests
import numpy as np
import logging

from concurrent.futures import ThreadPoolExecutor
from sklearn.metrics.pairwise import cosine_similarity
from config import CONFIG

logger = logging.getLogger(CONFIG['logger'])
STANDARDIZING_PATTERN = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9^_]")

def standardizing(string: str) -> str:
    """
    Return a standardized string by replacing non-alphanumeric characters with underscores,
    reducing multiple underscores to one, and converting all characters to lowercase.

    Args:
        string: The input string to be standardized.

    Returns: 
        A standardized version of the input string.
    """
    string = STANDARDIZING_PATTERN.sub("_", string)
    string = re.sub(r"(_)\1+","_", string)
    string = string.strip("_").lower()
    return string

def ada_retriever(doc_embeddings: list, id2tool:dict, question: str, top_k: int=5) -> list:
    """
    Retrieve tools related to the provided question.

    Args:
        doc_embeddings: The list of document embeddings.
        id2tool: A dictionary mapping tool id to tool name.
        question: The question for the ADA retriever.
        top_k: The number of top tools to return (default is 5).

    Returns:
        A list of retrieved tools.
    """
    cfg = CONFIG['retriver']
    url = cfg['endpoint']
    headers = cfg['headers']
    payload = {'input':question}
    payload.update(cfg['payload'])
    
    response = requests.post(url, json=payload, headers=headers)
    query_embedding = np.array(response.json()['data'][0]['embedding'])

    similarities = cosine_similarity([query_embedding], doc_embeddings)

    sorted_doc_indices = sorted(range(len(similarities[0])), key=lambda i: similarities[0][i], reverse=True)
    retrieved_tools = list(map(lambda doc_id: id2tool[str(doc_id)],sorted_doc_indices[:top_k]))
    
    return retrieved_tools

def build_tool_embeddings(tools_json: list[dict]) -> tuple:
    """
    Build tool embeddings.

    Args:
        tools_json: The list of dictionaries containing tool data.

    Returns:
        A tuple containing a list of document embeddings and a dictionary
        mapping tool id to tool name.
    """
    cfg = CONFIG['retriver']
    if os.path.exists(cfg['id2tool_file']) and os.path.exists(cfg['embedding_file']):
        id2tool = json.load(open(cfg['id2tool_file'], "r"))
        doc_embedings = np.load(cfg['embedding_file'])
        if len(id2tool) != len(doc_embedings):
            logger.error('Embedding file and id2tool file do not match! Rebuild embeddings!')
            id2tool = {}
            doc_embedings = []
    else:
        id2tool = {}
        doc_embedings = []

    # check embedding file whether need to be updated
    # get all current tool names
    # tool_names = set(map(lambda tool_json: tool_json['name'], tools_json))
    # cached_tool_names = set(id2tool.values())
    # if tool_names == cached_tool_names:
    #     logger.info('No tools change, use cached embeddings!')
    #     return doc_embedings, id2tool
    return doc_embedings, id2tool
    
    # update embeddings
    logger.info('Tools change detected, updating embeddings...')
    url = cfg['endpoint']
    headers = cfg['headers']
    
    new_id2tool = { str(i):tool_json['name'] for i,tool_json in enumerate(tools_json) }
    json.dump(new_id2tool, open(cfg['id2tool_file'], "w"), indent=4)

    def get_embedding(tool_json:dict) -> list:
        """
        Get embedding for a certain tool.

        Args:
            tool_json: The dictionary containing tool data.

        Returns:
            A list of tool embeddings.
        """
        payload = {'input':json.dumps(tool_json)}
        payload.update(cfg['payload'])
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            logger.error(f'Failed to get embedding for tool {tool_json["name"]}! Error: {e}')
            return [-1.000001] * cfg['embedding_dim']
        return response.json()['data'][0]['embedding']
    
    uncached_tools = list(filter(lambda tool_json: tool_json['name'] not in cached_tool_names, tools_json))
    uncached_tools_name = list(map(lambda tool_json: tool_json['name'],uncached_tools))
    uncached_doc_embedings = []
    with ThreadPoolExecutor(16) as pool:
        futures = [pool.submit(get_embedding, tool_json) for tool_json in uncached_tools]
        
        for future in tqdm.tqdm(futures,ncols=100):
            uncached_doc_embedings.append(future.result())
    
    new_doc_embedings = []
    for tool_json in tools_json:
        if tool_json['name'] not in cached_tool_names:
            new_doc_embedings.append(
                uncached_doc_embedings[
                    uncached_tools_name.index(tool_json['name'])
                    ])
        else:
            for doc_id in id2tool.keys():
                if id2tool[doc_id] == tool_json['name']:
                    new_doc_embedings.append(doc_embedings[int(doc_id)])
                    break

    new_doc_embedings = np.array(new_doc_embedings)
    np.save(cfg['embedding_file'], new_doc_embedings)

    logger.info('Embeddings updated! New embeddings saved!')
    return doc_embedings, new_id2tool