from beanie import Document
from datetime import datetime


class ToolServerNode(Document):
    """
    A class that represents a node in the database. 
    """
    id: str
    short_id: str
    status: str
    health: str
    last_req_time: datetime
    ip: str
    port: int

class NodeChecker(Document):
    manager_id: str
    interval: float
    pid: int