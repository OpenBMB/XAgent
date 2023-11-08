import requests

def send_post_request(url, data, headers=None):
    """
    Sends a POST request to the specified URL.

    Args:
        url (str): The URL to send the POST request to.
        data (str, dict): The data to be sent in the POST request. Can be string or dictionary.
        headers (dict, optional): A dictionary of HTTP headers to send with the request. Defaults to None.

    Returns:
        response (requests.models.Response): The server's response to the request.

    Raises: 
        requests.exceptions.RequestException: If there was an issue with sending the request.
    """
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response


def send_get_request(url, params=None, headers=None):
    """
    Sends a GET request to the specified URL.

    Args:
        url (str): The URL to send the GET request to.
        params (dict, optional): A dictionary of parameters to send with the request. Defaults to None.
        headers (dict, optional): A dictionary of HTTP headers to send with the request. Defaults to None.

    Returns:
        response (requests.models.Response): The server's response to the request.

    Raises: 
        requests.exceptions.RequestException: If there was an issue with sending the request.
    """
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response