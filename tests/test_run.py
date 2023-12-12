import pytest
from run import parse_args, execute_command_line_process, start_command_line
from unittest.mock import patch
import sys

@pytest.fixture
def mock_argv(monkeypatch):
    """
    A pytest fixture to mock the command line arguments.
    It sets the sys.argv to mimic command line input for testing.
    """
    test_args = ["--task", "example_task", "--upload-files", "file1", "file2", "--model", "model1"]
    monkeypatch.setattr(sys, 'argv', ['test_script.py'] + test_args)

def test_parse_args(mock_argv):
    """
    Test to ensure that the parse_args function correctly parses command line arguments.
    """
    args = parse_args()
    assert args.task == "example_task", "Task argument did not match."
    assert args.upload_files == ["file1", "file2"], "Upload files argument did not match."
    assert args.model == "model1", "Model argument did not match."

@patch('run.start_command_line')
def test_execute_command_line_process_quiet_mode(mock_start_command_line, mock_argv):
    """
    Test to verify if the execute_command_line_process function correctly handles the 'quiet_mode' argument.
    """
    args = parse_args()
    execute_command_line_process(args, quiet_mode=True)
    mock_start_command_line.assert_called_once()
    print("execute_command_line_process called start_command_line in quiet mode.")

@patch('run.start_command_line')
def test_execute_command_line_process_normal_mode(mock_start_command_line, mock_argv):
    """
    Test to verify if the execute_command_line_process function behaves correctly without the 'quiet_mode' argument.
    """
    args = parse_args()
    execute_command_line_process(args, quiet_mode=False)
    mock_start_command_line.assert_called_once()
    print("execute_command_line_process called start_command_line in normal mode.")

@patch('run.CommandLine')
def test_start_command_line(mock_command_line, mock_argv):
    """
    Test to ensure the start_command_line function correctly initializes the CommandLine class
    with the expected CommandLineParam instance based on the parsed arguments.
    """
    args = parse_args()
    start_command_line(vars(args))

    called_args, _ = mock_command_line.call_args
    called_param = called_args[0]
    assert called_param.task == args.task, "CommandLineParam task attribute did not match."
    assert called_param.upload_files == args.upload_files, "CommandLineParam upload_files attribute did not match."
    assert called_param.mode == args.mode, "CommandLineParam mode attribute did not match."
    print("start_command_line function called with correct CommandLineParam.")
