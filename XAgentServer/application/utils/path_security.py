import os
from pathlib import PureWindowsPath


def safe_child_path(root: str, untrusted_path: str) -> str:
    """Resolve a user-controlled relative path below root."""
    if not untrusted_path or "\x00" in untrusted_path or "\\" in untrusted_path:
        raise ValueError("A non-empty relative path is required.")
    windows_path = PureWindowsPath(untrusted_path)
    if (
        os.path.isabs(untrusted_path)
        or windows_path.is_absolute()
        or windows_path.drive
    ):
        raise ValueError("Absolute paths are not allowed.")

    resolved_root = os.path.realpath(root)
    target = os.path.realpath(os.path.join(resolved_root, untrusted_path))
    try:
        if os.path.commonpath([resolved_root, target]) != resolved_root:
            raise ValueError("Path is outside the allowed directory.")
    except ValueError:
        raise ValueError("Path is outside the allowed directory.")
    return target


def validate_plain_filename(filename: str) -> str:
    """Reject path components in names received from multipart uploads."""
    if (
        not filename
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or "\x00" in filename
    ):
        raise ValueError("Uploaded files must use a plain filename.")
    return filename
