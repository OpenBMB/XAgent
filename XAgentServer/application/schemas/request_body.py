""" Desc: Request body schema"""


from pydantic import BaseModel


class RequestBody(BaseModel):
    """RequestBody
    """
    token: str
    query: str
    mode: str
