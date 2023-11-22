import asyncio
import functools
import time
from colorama import Fore
from XAgentServer.exts.exception_ext import XAgentTimeoutError, XAgentCloseError

from inputimeout import inputimeout, TimeoutOccurred
from XAgentServer.application.global_val import redis
import math


def timer(func):
    """
    Decorator function to time the execution of a function.

    Args:
        func (Function): The function to be timed.

    Returns:
        wrapper (Function): The wrapped function with added timing functionality.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
        except:
            pass
    return wrapper


class CommandLineInput:
    """
    Class for handling command line input.

    This child class extends from BaseInput and implements methods to handle and manage command line input data.

    Attributes:
        do_interrupt (bool): If True, input will be interrupted.
        max_wait_seconds (int): Maximum wait time for input in seconds.
    """
    def __init__(self,
                 do_interrupt: bool = False,
                 max_wait_seconds: int = 600,
                 logger=None):
        self.do_interrupt = do_interrupt
        self.max_wait_seconds = max_wait_seconds
        self.logger = logger

    def run(self, input_data):
        """
        Run the command line input method.

        Args:
            input_data (Any): The original input data to be processed.

        Returns:
            data (Any): The processed input data.
        """
        if self.do_interrupt:
            data = self.interrupt(input_data)
        else:
            data = input_data
        return data
    
    def get_each_input(self, key, value, res, timeout):
        """
        Returns the input from the command line for a single key-value pair.

        Args:
            key (str): The key for which to get input.
            value (Any): The current value associated with the key.
            res (dict): The result dictionary where inputs collected will be stored.
            timeout (int): Timeout in seconds for the input.

        Returns:
            Any: The input data.
        """
        self.logger.typewriter_log(
            f"Now, ASK For {key}, Origin Input: {value}",
            Fore.RED,
            f""
        )
        self.logger.typewriter_log(
            f"Now, you can modify the current field by entering some information, and then press 'Enter' to continue, if you want to keep the original input, please enter '-1' and then press 'Enter':",
            Fore.GREEN
        )
        temp = inputimeout(prompt=f'You have {timeout} seconds to input:\n', timeout=timeout)
        if temp == "-1":
            return value
        else:
            return temp
        
    def get_input(self, origin_data):
        """
        Get input for all fields of the original data from the command line.

        Args:
            origin_data (dict): The original data for which to get input.

        Returns:
            dict: The dictionary with updated inputs.
        """
        self.logger.typewriter_log(
                "Next, you can start modifying the original input by typing 'Y/y/yes' or skip this step by typing 'N/n/no' and then press 'Enter' to continue the loop:",
                Fore.RED
            )
        update = inputimeout(prompt=f'You have to make a decision within 60 seconds:\n', timeout=60)
        res = {"args": {}}
        if update in ['y', 'Y', 'yes']:
            execute_time = self.max_wait_seconds
            if isinstance(origin_data, dict):
                args = origin_data.get("args", "")
                self.logger.typewriter_log(
                    f"Next, you will have a total of {self.max_wait_seconds} seconds to modify each option:",
                    Fore.RED,
                )
                for key, value in args.items():
                    if key == "done":
                        res[key] = False
                        continue
                    start_time = time.time()
                    res["args"][key] = self.get_each_input(key, value, res, execute_time)
                    end_time = time.time()
                    execute_time = math.floor(execute_time - (end_time - start_time))
            self.logger.info(f"modify the input, receive the data: {res}")
        else:
            res = origin_data
            self.logger.info("skip this step")
        self.logger.info("continue the loop")
        res["done"] = True
        return res
    
    def interrupt(self, input_data):
        """
        Interrupts the current input process and returns the current data.

        Args:
            input_data (dict): The original input data.

        Returns:
            dict: The current data collected so far.

        Raises:
            XAgentIOTimeoutError: If the input times out.
        """
        try:
            data = self.get_input(input_data)
            return data
        except TimeoutOccurred:
            self.logger.error(f"Waiting timemout, close connection!")
            raise XAgentTimeoutError("timeout!")