"""Response body"""
import json
from typing import Union

from pydantic import BaseModel, Json


class ResponseBody(BaseModel):
    """Response body
    """
    data: Union[str, dict, list, Json, None] = None
    success: bool = True
    message: Union[str, None] = None

    def to_dict(self):
        """to dict
        """
        return self.dict()

    def to_json(self):
        """to json
        """
        return self.json()


class WebsocketResponseBody():
    r"""
    WerSocket 返回值对象

    Attributes:
        data: 返回的数据

        status: 状态

        message: 消息

        kwargs: 其他参数, 会被添加到返回值中
    """

    def __init__(self,
                 data: Union[str, dict, list, Json, None],
                 status: str = "success",
                 message: Union[str, None] = None,
                 **kwargs):
        self.data = data
        self.status = status
        self.message = message
        self.extend(kwargs)

    def to_text(self):
        r"""
        返回json格式的字符串
        """

        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)

    def extend(self, extend: dict):
        """extend attributes
        """
        for key, value in extend.items():
            if key not in self.__dict__.keys():
                self.__dict__[key] = value
