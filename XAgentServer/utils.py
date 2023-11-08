import abc
import asyncio
import json
import os
import random
import shutil
import time
import traceback

from fastapi import WebSocket

from XAgentServer.database import InteractionBaseInterface, UserBaseInterface
from XAgentServer.envs import XAgentServerEnv
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.shared_interaction import SharedInteractionBase
from XAgentServer.response_body import WebsocketResponseBody


class Util(metaclass=abc.ABCMeta):
    """
    Base utility class with static methods for sending and receiving messages.
    """

    @staticmethod
    def send_message(client, message):
        """
        Sends a message from a client.

        Args:
            client: The client.
            message: The message to be sent.

        """
        client.sendall(message.encode())

    @staticmethod
    def recv_message(client):
        """
        Receives a message from a client.

        Args:
            client: The client.

        Returns:
            Returns a message sent by the client.

        """
        return client.recv(1024).decode()


class AutoReplayUtil(metaclass=abc.ABCMeta):
    """
    Utility class with static methods to handle automatic replay.
    """
    
    @staticmethod
    async def do_replay(websocket: WebSocket, base: InteractionBase):
        """
        Performs a replay of an interaction.

        Args:
            websocket: WebSocket object used to implement the communication.
            base: InteractionBase object containing the details of the interaction to replay.

        """
        with open(os.path.join(XAgentServerEnv.base_dir, "localstorage", "interact_records", base.create_time[:10], base.interaction_id, "cache.json"), "r") as f:
            history = json.load(f)

        await AutoReplayUtil.do_replay_start(websocket, history)

    @staticmethod
    async def do_replay_start(websocket: WebSocket, history: dict):
        """
        Starts the replay of interaction.

        Args:
            websocket: WebSocket object used to implement the communication.
            history: Dictionary containing history of user interaction.

        """
        init_data = {}
        for key, value in history.items():
            if key == "subtasks":
                init_data[key] = [{**v, "inner": []} for v in value]
            else:
                init_data[key] = value

        await asyncio.sleep(random.randint(1, 5))
        await websocket.send_text(WebsocketResponseBody(status="start", data=init_data, message="success").to_text())
        await AutoReplayUtil.do_auto_replay(websocket, history)

    @staticmethod
    async def do_auto_replay(websocket: WebSocket, history: dict):
        """
        Performs the automatic replay of interaction.

        Args:
            websocket: WebSocket object used to implement the communication.
            history: Dictionary containing history of user interaction.

        """

        cache_list = history.get("subtasks", [])
        item = cache_list.pop(0)
        while item is not None:
            inner = item.get("inner", [])
            if inner:
                inner_props = inner.pop(0)
                while inner_props is not None:
                    send = True
                    tool_name = inner_props.get("using_tools", {}).get(
                        "tool_name", "") if isinstance(inner_props, dict) else ""

                    await asyncio.sleep(random.randint(1, 5))
                    if tool_name == "subtask_submit":
                        send_data = {
                            "task_id": item.get("task_id", ""),
                            "name": item.get("name", ""),
                            "goal": item.get("goal", ""),
                            "handler": item.get("handler", ""),
                            "data": inner_props,
                            "current": item.get("task_id", ""),
                            "status": "subtask_submit",
                            "message": ""
                        }

                    else:
                        send_data = {
                            "task_id": item.get("task_id", ""),
                            "name": item.get("name", ""),
                            "goal": item.get("goal", ""),
                            "handler": item.get("handler", ""),
                            "data": inner_props,
                            "current": item.get("task_id", ""),
                            "status": "inner",
                            "message": ""
                        }
                        await websocket.send_text(WebsocketResponseBody(**send_data).to_text())
                    if inner:
                        inner_props = inner.pop(0)
                    else:
                        inner_props = None
                    if inner_props is None:
                        await asyncio.sleep(random.randint(1, 5))
                        send_data = {
                            "task_id": item.get("task_id", ""),
                            "name": item.get("name", ""),
                            "goal": item.get("goal", ""),
                            "handler": item.get("handler", ""),
                            "data": item.get("refinement", {}),
                            "current": item.get("task_id", ""),
                            "status": "refinement",
                            "message": ""
                        }
                        await websocket.send_text(WebsocketResponseBody(**send_data).to_text())
                        await asyncio.sleep(5)
            
            if cache_list:
                await asyncio.sleep(random.randint(1, 5))
                sub_send_data = {
                    "data": [{**r_, "inner": []}for r_ in cache_list],
                    "current": cache_list[0]["task_id"],
                    "status": "subtask",
                    "message": ""
                }
                
                await websocket.send_text(WebsocketResponseBody(**sub_send_data).to_text())
                item = cache_list.pop(0)
            else:
                item = None
  

class ShareUtil(metaclass=abc.ABCMeta):
    """
    Utility class with static methods to handle the sharing of interactions.

    Attributes:
        db: InteractionBaseInterface object to connect to the interactions database.
        user_db: UserBaseInterface object to connect to the user's database.
    """
    db: InteractionBaseInterface = None
    user_db: UserBaseInterface = None

    @staticmethod
    def register_db(db, user_db):
        """
        Registers the interaction database and user's database.

        Args:
            db: The interaction database.
            user_db: The user's database.

        """
        ShareUtil.db = db
        ShareUtil.user_db = user_db

    @staticmethod
    def share_interaction(interaction_id: str, user_id: str):
        """
        Shares an interaction.

        Args:
            interaction_id: The ID of the interaction.
            user_id: The ID of the user who owns the interaction.

        Returns:
            True if the interaction was successfully shared, False otherwise.

        """
        try:
            interaction = ShareUtil.db.get_interaction(interaction_id)
            if interaction is None:
                return False
            user_name = ShareUtil.user_db.get_user(user_id).name
            record_dir = os.path.join(XAgentServerEnv.base_dir, "localstorage", "interact_records", interaction.create_time[:10], interaction_id)
            if not os.path.exists(record_dir):
                return False
            shared_dir = os.path.join(XAgentServerEnv.base_dir, "localstorage", "shared_interact_records", interaction_id)
            if not os.path.exists(shared_dir):

                os.makedirs(shared_dir)
            for file in os.listdir(record_dir):
                shutil.copy(os.path.join(record_dir, file), shared_dir)
            shared = SharedInteractionBase(interaction_id=interaction_id,
                                           user_name=user_name,
                                           create_time=interaction.create_time,
                                           update_time=interaction.update_time,
                                           description=interaction.description,
                                           agent=interaction.agent,
                                           mode=interaction.mode,
                                           is_deleted=interaction.is_deleted,
                                           star=0,
                                           record_dir=shared_dir,
                                           )
            ShareUtil.db.add_share(shared)
            return True
        except Exception as e:
            traceback.print_exc()
            return False


    @staticmethod
    async def do_replay(websocket: WebSocket, shared: SharedInteractionBase):
        """
        Performs a replay of a shared interaction.

        Args:
            websocket: WebSocket object used to implement the communication.
            shared: SharedInteractionBase object containing the details of the shared interaction to replay.

        """
        with open(os.path.join(shared.record_dir, "cache.json"), "r") as f:
            history = json.load(f)

        await AutoReplayUtil.do_replay_start(websocket, history)


