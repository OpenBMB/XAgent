
import os
import base64
import uuid
import json5 as json
import requests

from colorama import Fore
from XAgent.utils import ToolCallStatusCode
from XAgent.ai_functions import function_manager
from XAgent.recorder import RunningRecoder


def is_wrapped_response(obj: dict) -> bool:
    """
    Check if the response object is wrapped.

    Args:
        obj (dict): The response object.

    Returns:
        bool: True if the response object is wrapped, False otherwise.
    """
    if 'type' in obj and obj['type'] in ['simple', 'composite', 'binary'] and 'data' in obj:
        return True
    return False


def unwrap_tool_response(obj, logger=None):
    """
    Unwrap the tool response object.

    Args:
        obj: The tool response object.
        logger: The logger.

    Returns:
        The unwrapped tool response object.
    """
    if isinstance(obj, dict):
        if is_wrapped_response(obj):
            match obj['type']:
                case 'simple':
                    return obj['data']
                case 'binary':
                    name = obj.get('name', uuid.uuid4().hex)
                    if obj['media_type'] == 'image/png' and not str(name).endswith('.png'):
                        name += '.png'
                    with open(os.path.join('local_workspace', name), 'wb') as f:
                        f.write(base64.b64decode(obj['data']))
                    return {
                        'media_type': obj['media_type'],
                        'file_name': name
                    }
                case 'composite':
                    return [unwrap_tool_response(o, logger) for o in obj['data']]
        else:
            return obj
    elif isinstance(obj, (str, int, float, bool, list)):
        return obj
    elif obj is None:
        return None
    else:
        logger.typewriter_log(
            f'Unknown type {type(obj)} in unwrap_tool_response', Fore.YELLOW)
        return None


class ToolServerInterface():
    """
    The interface to communicate with the ToolServer.
    """

    def __init__(self, recorder: RunningRecoder, logger=None):
        self.recorder = recorder
        self.logger = logger

    def lazy_init(self, config):
        """
        Lazy initialization of the ToolServer interface.

        Args:
            config: The configuration for the ToolServer.

        Raises:
            NotImplementedError: If trying to use a non-selfhost ToolServer.
        """
        self.config = config
        if config.use_selfhost_toolserver:
            self.url = config.selfhost_toolserver_url
        else:
            raise NotImplementedError('Please use selfhost toolserver')
        self.logger.typewriter_log("ToolServer connected in", Fore.RED, self.url)
        response = requests.post(f'{self.url}/get_cookie',)
        self.cookies = response.cookies

    def close(self):
        """
        Close the ToolServer session.
        """
        requests.post(f'{self.url}/close_session', cookies=self.cookies)

    def upload_file(self, file_path) -> str:
        """
        Upload a file to the ToolServer.

        Args:
            file_path (str): The path to the file to be uploaded.

        Returns:
            str: The response from the ToolServer.
        """
        url = f"{self.url}/upload_file"
        response = requests.post(url, timeout=10, cookies=self.cookies,
                                 files={'file': open(file_path, 'rb'), 'filename': os.path.basename(file_path)})
        response.raise_for_status()
        response = response.json()
        return response

    def download_file(self, file_path) -> str:
        """
        Download a file from the ToolServer.

        Args:
            file_path (str): The path to the file to be downloaded.

        Returns:
            str: The save path of the downloaded file.
        """
        url = f"{self.url}/download_file"
        payload = {
            'file_path': file_path
        }
        response = requests.post(
            url, json=payload, timeout=10, cookies=self.cookies,)
        response.raise_for_status()

        save_path = os.path.join(self.recorder.record_root_dir, file_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path

    def get_workspace_structure(self) -> dict:
        """
        Get the structure of the workspace from the ToolServer.

        Returns:
            dict: The structure of the workspace.
        """
        url = f"{self.url}/get_workspace_structure"
        response = requests.post(url, timeout=10, cookies=self.cookies,)
        response.raise_for_status()
        response = response.json()
        return response

    def download_all_files(self):
        """
        Download all the files in the workspace from the ToolServer.

        Returns:
            str: The save path of the downloaded workspace.
        """
        url = f"{self.url}/download_workspace"
        response = requests.post(url, cookies=self.cookies,)
        response.raise_for_status()

        save_path = os.path.join(
            self.recorder.record_root_dir, 'workspace.zip')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path

    def get_available_tools(self):
        """
        Get the available tools from the ToolServer.

        Returns:
            The available tools.
        """
        payload = {
        }
        url = f"{self.url}/get_available_tools"
        cache_output = self.recorder.query_tool_server_cache(url, payload)
        try:
            if cache_output != None:

                response = cache_output["tool_output"]
                status_code = cache_output["response_status_code"]
            else:
                response = requests.post(
                    url, json=payload, timeout=10, cookies=self.cookies)
                status_code = response.status_code
                response.raise_for_status()
                response = response.json()
                if not isinstance(response, dict):
                    response = json.loads(response)

            self.recorder.regist_tool_server(url=url,
                                             payload=payload,
                                             tool_output=response,
                                             response_status_code=status_code)
            return response
        except Exception as e:
            raise Exception(f"Error when fetching available tools: {e}")

    def retrieve_rapidapi_tools(self, query: str, top_k: int = 10):
        """
        Retrieve RapidAPI tools from the ToolServer.

        Args:
            query (str): The query for retrieving tools.
            top_k (int, optional): The number of tools to retrieve. Defaults to 10.

        Returns:
            The retrieved tools and the description of the tools in JSON format.
        """
        url = f"{self.url}/retrieving_tools"
        payload = {
            "question": query,
            "top_k": top_k
        }
        cache_output = self.recorder.query_tool_server_cache(url, payload)
        try:
            if cache_output != None:
                response = cache_output["tool_output"]
                status_code = cache_output["tool_output_status_code"]
            else:
                response = requests.post(
                    url, json=payload, timeout=20, cookies=self.cookies)
                status_code = response.status_code
                response = response.json()
                if not isinstance(response, dict):
                    response = json.loads(response)
            self.recorder.regist_tool_server(url=url,
                                             payload=payload,
                                             tool_output=response,
                                             response_status_code=status_code)
            retrieved_tools = response["retrieved_tools"]
            tools_json = response["tools_json"]
            for tool_json in tools_json:
                function_manager.register_function(tool_json)
        except Exception as e:
            self.logger.typewriter_log(
                "Tool Retrieval Failed, nothing will be retrieved, please fix here.",
                Fore.RED,
            )
            print(f"Error when retrieving tools: {e}")
            print(response)
            return None, None

        return retrieved_tools, tools_json

    def get_json_schema_for_tools(self, command_names):
        """
        Get the JSON schema for the specified tools from the ToolServer.

        Args:
            command_names: The names of the tools.

        Returns:
            The JSON schema for the tools.
        """
        url = f"{self.url}/get_json_schema_for_tools"
        payload = {
            "tool_names": command_names
        }
        cache_output = self.recorder.query_tool_server_cache(url, payload)
        try:
            if cache_output != None:
                response = cache_output["tool_output"]
                status_code = cache_output["tool_output_status_code"]
            else:
                response = requests.post(
                    url, json=payload, timeout=10, cookies=self.cookies)
                status_code = response.status_code
                response = response.json()
                if not isinstance(response, dict):
                    try:
                        response = json.loads(response)
                    except:
                        pass
            self.recorder.regist_tool_server(url=url,
                                             payload=payload,
                                             tool_output=response,
                                             response_status_code=status_code)
            function_manager.register_function(response)
            return response

        except Exception as e:
            print(f"Error when fetching openai function jsons: {e}")
            return None

    # @func_set_timeout()

    def execute_command_client(
        self,
        command_name,
        arguments={},
        # input_hash_id,
    ):
        """
        Execute a command on the ToolServer.

        Args:
            command_name (str): The name of the command.
            arguments (dict, optional): The arguments for the command. Defaults to {}.
            input_hash_id: The hash ID of the input.

        Returns:
            mixed: The result of the command and the tool output status code.
        """
        # return "sorry, the server is not available now", ToolCallStatusCode.SERVER_ERROR, input_hash_id
        url = f"{self.url}/execute_tool"
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except:
                pass
        payload = {
            "tool_name": command_name,
            "arguments": arguments,
            # "hash_id": input_hash_id,
        }

        cache_output = self.recorder.query_tool_server_cache(url, payload)

        if self.config['experiment']['redo_action'] or cache_output is None:
            response = requests.post(url, json=payload, cookies=self.cookies)
            response_status_code = response.status_code
            if response.status_code == 200 or response.status_code == 450:
                command_result = response.json()
                command_result = unwrap_tool_response(command_result, self.logger)
            else:
                command_result = response.text

        if cache_output != None:
            command_result = cache_output["tool_output"]
            response_status_code = cache_output["response_status_code"]

        self.recorder.regist_tool_server(url=url,
                                         payload=payload,
                                         tool_output=command_result,
                                         response_status_code=response_status_code)

        # setting tool_output_status_code according to status_code
        if response_status_code == 200:
            tool_output_status_code = ToolCallStatusCode.TOOL_CALL_SUCCESS
        elif response_status_code == 404:
            tool_output_status_code = ToolCallStatusCode.HALLUCINATE_NAME
        elif response_status_code == 422:
            tool_output_status_code = ToolCallStatusCode.FORMAT_ERROR
        elif response_status_code == 450:
            tool_output_status_code = ToolCallStatusCode.TIMEOUT_ERROR
        elif response_status_code == 500:
            tool_output_status_code = ToolCallStatusCode.TOOL_CALL_FAILED
        elif response_status_code == 503:
            tool_output_status_code = ToolCallStatusCode.SERVER_ERROR
            raise Exception("Server Error: " + command_result)
        else:
            tool_output_status_code = ToolCallStatusCode.OTHER_ERROR

        return command_result, tool_output_status_code