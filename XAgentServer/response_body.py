import json
from typing import Optional, Union

from pydantic import BaseModel, Json


class ResponseBody(BaseModel):
    data: Union[str, dict, list, Json, None] = None
    success: bool = True
    message: Union[str, None] = None

    def to_dict(self):
        return self.dict()

    def to_json(self):
        return self.json()


class WebsocketResponseBody:
    def __init__(
        self,
        data: Union[str, dict, list, Json, None],
        status: str = "success",
        message: Union[str, None] = None,
        **kwargs
    ):
        self.data = data
        self.status = status
        self.message = message
        self.extend(kwargs)

    def to_text(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)

    def extend(self, extend: dict):
        for key, value in extend.items():
            if key not in self.__dict__.keys():
                self.__dict__[key] = value
