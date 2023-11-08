import abc
import json
import logging
import os
import random
import re
import time
import uuid
from logging import LogRecord
from typing import Any

from colorama import Fore, Style

class JsonFileHandler(logging.FileHandler):
    """
    A class to handle JSON file logging.

    Inherited from `logging.FileHandler`, allows emitting logs directly to a JSON file.

    Attributes:
        baseFilename (str): Path to the file in which the log records are written to.

    """
    def __init__(self, filename, mode="a", encoding=None, delay=False):
        """
        Initialize the JsonFileHandler class with the name of the log file.

        Args:
            filename (str): Specifies the file that the handler should log to.
            mode (str, optional): mode to open the file with. Defaults to "a".
            encoding (str, optional): encoding to use for opening the file. Defaults to None.
            delay (bool, optional): If delay is true, then file opening is deferred until the first call to emit(). Defaults to False.

        """
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        """
        Emit a formatted log record into the log file.

        Args:
            record (logging.LogRecord): Log record which is to be formatted into json data and emitted.

        """
        json_data = json.loads(self.format(record))
        with open(self.baseFilename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)


class JsonFormatter(logging.Formatter):
    """
    Formatter for JSON log data.
    """
    def format(self, record):
        """
        Log record formatter for JSON log data.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: Formatted log record as a string.

        """
        return record.msg

class Logger(metaclass=abc.ABCMeta):
    """
    Abstract Base Class for Loggers with different types of handlers. 
    Allows setting up multiple loggers with different settings.

    Args:
        log_dir (str): Path of the directory where the log files should be stored.
        log_name (str): Logger's name.
        log_file (str): The name of the main log file.
        error_file (str): The name of the error log file.

    """
    
    def __init__(self, log_dir: str = None, log_name: str= "", log_file: str = "activity.log", error_file: str = "errors.log"):
        """
        Initialize the Logger class with the path to log directory, name of the logs and log files.

        Args:
            log_dir (str, optional): Path of the directory where log files should be stored. Defaults to None.
            log_name (str, optional): Name of the logger. Defaults to "".
            log_file (str, optional): Name of the main log file. Defaults to "activity.log".
            error_file (str, optional): Name of the error log file. Defaults to "errors.log".

        """
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.log_name = time.strftime("%Y-%m-%d", time.localtime()) if not log_name else log_name
        self.logger = logging.getLogger(self.log_name)
        console_formatter = RecordFormatter("%(title_color)s %(message)s")

        # Create a handler for console which simulate typing
        self.typing_console_handler = TypingConsoleHandler()
        self.typing_console_handler.setLevel(logging.INFO)
        self.typing_console_handler.setFormatter(console_formatter)

        # Create a handler for console without typing simulation
        self.console_handler = ConsoleHandler()
        self.console_handler.setLevel(logging.DEBUG)
        self.console_handler.setFormatter(console_formatter)
        
        
        self.speak_mode = False
        self.chat_plugins = []

        # Info handler in activity.log
        self.file_handler = logging.FileHandler(
            os.path.join(log_dir, log_file), "a", "utf-8"
        )
        self.file_handler.setLevel(logging.DEBUG)
        info_formatter = RecordFormatter(
            "%(asctime)s [%(threadName)s] %(levelname)s: %(title)s %(message)s"
        )
        self.file_handler.setFormatter(info_formatter)

        # Error handler error.log
        error_handler = logging.FileHandler(
            os.path.join(log_dir, error_file), "a", "utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = RecordFormatter(
            "%(asctime)s [%(threadName)s] %(levelname)s %(module)s:%(funcName)s:%(lineno)d %(title)s"
            " %(message_no_color)s"
        )
        error_handler.setFormatter(error_formatter)

        # self.typing_logger = logging.getLogger(self.log_name)
        # if not self.typing_logger.handlers:
        #     self.typing_logger.addHandler(self.typing_console_handler)
        #     self.typing_logger.addHandler(self.file_handler)
        #     self.typing_logger.addHandler(error_handler)
        # self.typing_logger.setLevel(logging.DEBUG)

        if self.log_name.endswith("_INTERACT") or not self.logger.handlers:
            self.logger.addHandler(self.console_handler)
            self.logger.addHandler(error_handler)
            self.logger.addHandler(self.file_handler)
            self.logger.setLevel(logging.DEBUG)

    
    def typewriter_log(
        self, title="", title_color="", content="", speak_text=False, level=logging.INFO
    ):
        # if speak_text and self.speak_mode:
        #     say_text(f"{title}. {content}")

        for plugin in self.chat_plugins:
            plugin.report(f"{title}. {content}")

        if content:
            if isinstance(content, list):
                content = " ".join(content)
        else:
            content = ""

        self.logger.log(
            level, content, extra={"title": title, "color": title_color}
        )

    def debug(
        self,
        message,
        title="",
        title_color="",
    ):
        self._log(title, title_color, message, logging.DEBUG)

    def info(
        self,
        message,
        title="",
        title_color="",
    ):
        self._log(title, title_color, message, logging.INFO)

    def warn(
        self,
        message,
        title="",
        title_color="",
    ):
        self._log(title, title_color, message, logging.WARN)

    def error(self, title, message=""):
        self._log(title, Fore.RED, message, logging.ERROR)

    def _log(
        self,
        title: str = "",
        title_color: str = "",
        message: str = "",
        level=logging.INFO,
    ):
        if message:
            if isinstance(message, list):
                message = " ".join(message)
        self.logger.log(
            level, message, extra={"title": str(title), "color": str(title_color)}
        )

    def set_level(self, level):
        self.logger.setLevel(level)
        self.typing_logger.setLevel(level)

    def double_check(self, additionalText=None):
        if not additionalText:
            additionalText = (
                "Please ensure you've setup and configured everything"
                " correctly. Read https://github.com/Torantulino/Auto-GPT#readme to "
                "double check. You can also create a github issue or join the discord"
                " and ask there!"
            )

        self.typewriter_log("DOUBLE CHECK CONFIGURATION", Fore.YELLOW, additionalText)

    def log_json(self, data: Any, file_name: str) -> None:
        # Define log directory
        this_files_dir_path = os.path.dirname(__file__)
        log_dir = os.path.join(this_files_dir_path, "../logs")

        # Create a handler for JSON files
        json_file_path = os.path.join(log_dir, file_name)
        json_data_handler = JsonFileHandler(json_file_path)
        json_data_handler.setFormatter(JsonFormatter())

        # Log the JSON data using the custom file handler
        self.json_logger.addHandler(json_data_handler)
        self.json_logger.debug(data)
        self.json_logger.removeHandler(json_data_handler)

    def get_log_directory(self):
        this_files_dir_path = os.path.dirname(__file__)
        log_dir = os.path.join(this_files_dir_path, "../logs")
        return os.path.abspath(log_dir)


"""
Output stream to console using simulated typing
"""
    

class TypingConsoleHandler(logging.StreamHandler):
    """
    A logging.StreamHandler subclass that outputs logs to the console like a typewriter.
    
    This class simulates typing with varying speed when emitting log records. 

    """

    def emit(self, record):
        """
        Emit a log record in a typing style with varying speed.

        Args:
            record (logging.LogRecord): Log record to be emitted.

        """
        min_typing_speed = 0.05
        max_typing_speed = 0.01

        msg = self.format(record)
        try:
            words = msg.split()
            for i, word in enumerate(words):
                print(word, end="", flush=True)
                if i < len(words) - 1:
                    print(" ", end="", flush=True)
                typing_speed = random.uniform(min_typing_speed, max_typing_speed)
                time.sleep(typing_speed)
                min_typing_speed = min_typing_speed * 0.95
                max_typing_speed = max_typing_speed * 0.95
            print()
        except Exception:
            self.handleError(record)


class ConsoleHandler(logging.StreamHandler):
    """
    A logging.StreamHandler subclass that outputs logs to the console.

    """
    def emit(self, record) -> None:
        """
        Emit a log record to the console.

        Args:
            record (logging.LogRecord): Log record to be emitted.

        """
        msg = self.format(record)
        try:
            print(msg)
        except Exception:
            self.handleError(record)

            
class RecordFormatter(logging.Formatter):
    """
    A custom log formatter allowing logging with colors in the console output.

    It recognizes the custom placeholders 'title_color' and 'message_no_color'.
    To use this formatter, the log function should pass 'color' and 'title' as log extras.

    """

    def format(self, record: LogRecord) -> str:
        """
        Format a log record with title color and message with no color.

        Args:
            record (logging.LogRecord): Log record to be formatted.

        Returns:
            str: The formatted log record as a string.

        """
        if hasattr(record, "color"):
            record.title_color = (
                getattr(record, "color")
                + getattr(record, "title", "")
                + " "
                + Style.RESET_ALL
)
        else:
            record.title_color = getattr(record, "title", "")

        # Add this line to set 'title' to an empty string if it doesn't exist
        record.title = getattr(record, "title", "")

        if hasattr(record, "msg"):
            record.message_no_color = remove_color_codes(getattr(record, "msg"))
        else:
            record.message_no_color = ""
        return super().format(record)


def remove_color_codes(s: str) -> str:
    """
    Utility function to remove color codes from a string.

    Args:
        s (str): The input string from which the color codes are removed.

    Returns:
        str: A string with all color codes removed.

    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", s)