import importlib.util
from pathlib import Path

import pytest

from XAgentServer.application.utils.path_security import safe_child_path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _load_toolserver_path_security():
    module_path = (
        REPOSITORY_ROOT
        / "ToolServer"
        / "ToolServerNode"
        / "utils"
        / "path_security.py"
    )
    spec = importlib.util.spec_from_file_location(
        "toolserver_path_security", module_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_toolserver_upload_rejects_path_components(tmp_path):
    security = _load_toolserver_path_security()

    for filename in ("../../../tmp/hacked", r"..\..\tmp\hacked", "/tmp/hacked"):
        with pytest.raises(ValueError):
            security.safe_upload_path(str(tmp_path), filename)

    assert security.safe_upload_path(str(tmp_path), "report.txt") == str(
        tmp_path / "report.txt"
    )


def test_workspace_file_cannot_escape_record_directory(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    for filename in ("../../../../etc/passwd", "/etc/passwd", r"..\..\secret"):
        with pytest.raises(ValueError):
            safe_child_path(str(workspace), filename)

    assert safe_child_path(str(workspace), "results/report.txt") == str(
        workspace / "results" / "report.txt"
    )


def test_workspace_path_rejects_symlink_escape(tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    (workspace / "escape").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError):
        safe_child_path(str(workspace), "escape/secret.txt")


def test_runtime_tool_registration_is_not_exposed():
    node_source = (
        REPOSITORY_ROOT / "ToolServer" / "ToolServerNode" / "main.py"
    ).read_text()
    manager_config = (
        REPOSITORY_ROOT / "assets" / "config" / "manager.yml"
    ).read_text()

    assert "@app.post('/register_new_tool')" not in node_source
    assert "- /register_new_tool" not in manager_config
