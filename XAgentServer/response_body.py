import json
from typing import Optional, Union

from pydantic import BaseModel, Json


class ResponseBody(BaseModel):
    """
    Class for creating a response body for a request.

    Attributes:
        data (Union[str, dict, list, Json, None]): The data to include in the response body.
        success (bool): Indicates whether the request was successful. Default is True.
        message (Union[str, None]): The message to include in the response body.
    """

    data: Union[str, dict, list, Json, None] = None
    success: bool = True
    message: Union[str, None] = None

    def to_dict(self):
        """
        Converts the response body to a dictionary.

        Returns:
            dict: The response body as a dictionary.
        """
        return self.dict()
    
    def to_json(self):
        """
        Converts the response body to a JSON string.

        Returns:
            str: The response body as a JSON string.
        """
        return self.json()
    

class WebsocketResponseBody():
    """
    Class for creating a response body for a Websocket request.

    Attributes:
        data (Union[str, dict, list, Json, None]): The data to include in the response body.
        status (str): The status of the Websocket request. Default is 'success'.
        message (Union[str, None]): The message to include in the response body.
    """

    def __init__(self, data: Union[str, dict, list, Json, None], status: str = "success", message: Union[str, None] = None, **kwargs):
        self.data = data
        self.status = status
        self.message = message
        self.extend(kwargs)

    
    def to_text(self):
        """
        Converts the response body to a text string.

        Returns:
            str: The response body as a text string.
        """
        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)
    

    def extend(self, extend: dict):
        """
        Adds additional data to the response body.

        Args:
             extend (dict): Dictionary to be added to the response body if its keys don't exist in response.

        """
        for key, value in extend.items():
            if key not in self.__dict__.keys():
                self.__dict__[key] = value