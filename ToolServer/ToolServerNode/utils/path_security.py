import os
from pathlib import PureWindowsPath


def safe_workspace_path(work_directory: str, untrusted_path: str) -> str:
    """Resolve a user-controlled path and ensure it stays in the workspace."""
    if not untrusted_path or "\x00" in untrusted_path or "\\" in untrusted_path:
        raise ValueError("A non-empty workspace path is required.")
    windows_path = PureWindowsPath(untrusted_path)
    if (
        os.path.isabs(untrusted_path)
        or windows_path.is_absolute()
        or windows_path.drive
    ):
        raise ValueError("Absolute paths are not allowed.")

    workspace = os.path.realpath(work_directory)
    target = os.path.realpath(os.path.join(workspace, untrusted_path))
    try:
        if os.path.commonpath([workspace, target]) != workspace:
            raise ValueError("Path is outside the workspace.")
    except ValueError:
        raise ValueError("Path is outside the workspace.")
    return target


def safe_upload_path(work_directory: str, filename: str) -> str:
    """Validate an uploaded filename and return its workspace destination."""
    if (
        not filename
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or "\x00" in filename
    ):
        raise ValueError("Uploaded files must use a plain filename.")
    return safe_workspace_path(work_directory, filename)
