"""XAgent Redis Client"""
from redis import Redis

from XAgentServer.application.core.envs import XAgentServerEnv
import os


class RedisClient:
    """
    RedisClient
    """

    def __init__(self):
        self.client = Redis(host=os.getenv('REDIS_HOST', XAgentServerEnv.Redis.redis_host),
                            port=XAgentServerEnv.Redis.redis_port,
                            db=XAgentServerEnv.Redis.redis_db,
                            password=XAgentServerEnv.Redis.redis_password)

    def set_key(self, key, value, ex=None, px=None, nx=False, xx=False):
        """redis set key

        Args:
            key (_type_): _description_
            value (_type_): _description_
            ex (_type_, optional): _description_. Defaults to None.
            px (_type_, optional): _description_. Defaults to None.
            nx (bool, optional): _description_. Defaults to False.
            xx (bool, optional): _description_. Defaults to False.
        """
        self.client.set(key, value, ex, px, nx, xx)

    def get_key(self, key):
        """redis get key

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        value = self.client.get(key)
        if value:
            return value.decode("utf-8")
        else:
            return None

    def delete_key(self, key):
        """redis delete key

        Args:
            key (_type_): _description_
        """
        self.client.delete(key)

    def get_all_keys(self):
        """redis get all keys

        Returns:
            _type_: _description_
        """
        return self.client.keys()

    def delete_all_keys(self):
        """redis delete all keys
        """
        self.client.flushdb()

    def set_parent_key(self, key, value):
        """redis set parent key

        Args:
            key (_type_): _description_
            value (_type_): _description_
        """
        self.client.set(key, value)

    def get_parent_key(self, key):
        """redis get parent key

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.client.get(key)

    def delete_parent_key(self, key):
        """redis delete parent key

        Args:
            key (_type_): _description_
        """
        self.client.delete(key)

    def set_child_key(self, parent_key, key, value):
        """redis set child key

        Args:
            key (_type_): _description_
            value (_type_): _description_
        """
        parent = self.client.get(parent_key)
        if parent:
            parent[key] = value
        else:
            parent = {key: value}
        self.set_key(parent_key, parent)
        
    def get_child_key(self, key):
        """redis get child key

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.client.get(key)

    def delete_child_key(self, key):
        """redis delete child key

        Args:
            key (_type_): _description_
        """
        self.client.delete(key)

    def get_child_keys(self, parent_key):
        """

        Args:
            parent_key (_type_): _description_
        """
        return self.client.keys(parent_key)
