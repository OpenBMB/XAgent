"""common functions for websocket handlers"""
import base64
import os
from XAgentServer.application.cruds.user import UserCRUD
from XAgentServer.database.models import Raw
from XAgentServer.exts.exception_ext import XAgentWebSocketConnectError


async def check_user(db, user_id, token):
    """
    check user for websocket connection
    """
    if not UserCRUD.is_exist(db=db, user_id=user_id):
        raise XAgentWebSocketConnectError("user is not exist!")
    # auth
    if not UserCRUD.user_is_valid(db=db, user_id=user_id, token=token):
        raise XAgentWebSocketConnectError("user is not available!")

    user = UserCRUD.get_user(db=db, user_id=user_id)
    if not user or user.token != token or user.available is False or user.is_beta is False:
        raise XAgentWebSocketConnectError(
            "XAgentServer is running in production mode, if you want to use it, please contact the administrator.")

def handle_data(row: Raw, root_dir: str):
    """
    handle data for websocket response
    """
    data = row.data
    try:
        using_tools = data.get("using_tools", "")
        if not using_tools:
            return data
        tool_name = using_tools.get("tool_name", "") if isinstance(
            using_tools, dict) else ""
        tool_output = using_tools.get(
            "tool_output", {}) if isinstance(using_tools, dict) else ""
        tool_input = using_tools.get(
            "tool_input", {}) if isinstance(using_tools, dict) else ""
        if row.include_pictures:
            if tool_name == "PythonNotebook_execute_cell":
                for output in tool_output:
                    if isinstance(output, dict) and 'file_name' in output:
                        file_name = output['file_name']
                        png_base64 = None
                        if file_name:
                            file_path = os.path.join(
                                root_dir, "workspace", file_name)
                            if os.path.exists(file_path):
                                try:
                                    with open(file_path, "rb") as f:
                                        png_base64 = base64.b64encode(
                                            f.read()).decode("utf-8")
                                except Exception:
                                    pass

                        output["file_data"] = png_base64
                        using_tools["is_include_pictures"] = True
    
        if tool_input:
            data["using_tools"]["tool_input"] = tool_input.encode("utf-8").decode("unicode_escape")
        if tool_output and isinstance(tool_output, str):
            data["using_tools"]["tool_output"] = tool_output.encode("utf-8").decode("unicode_escape")
    except Exception:
        pass
    return data


def handle_workspace_filelist(file_list):
    """handle workspace file list

    Args:
        file_list (_type_): file_list is a list of file name

    Returns:
        List[Dict]: element list, each element is a dict with name and suffix
    """
    if not isinstance(file_list, list) or not file_list:
        return []
    return [{"name": file, "suffix": file.split(".")[-1]}  for file in file_list]
