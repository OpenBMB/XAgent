from pydantic import BaseModel
from typing import Optional

class FuncReq(BaseModel):
    """The request for function call"""
    messages:Optional[list[dict]]
    arguments:Optional[dict]
    functions:Optional[list[dict]]
    function_call:Optional[dict]
    temperature:Optional[float]
    max_tokens:Optional[int]
    top_p:Optional[float]
    top_k:Optional[int]
    repetition_penalty:Optional[float]
    model:str


class Usage(BaseModel):
    """The record for token consumption"""
    prompt_tokens:int
    completion_tokens:int
    total_tokens:int

class FuncResult(BaseModel):
    """The response for function call"""
    arguments:Optional[dict]
    function_call:Optional[dict]

class Message(BaseModel):
    content: str

class XAgentMessage(BaseModel):
    message:Message
    finish_reason:str
    index:int

class XAgentResponse(BaseModel):
    model:str
    usage:Optional[Usage]
    choices:list[XAgentMessage]
