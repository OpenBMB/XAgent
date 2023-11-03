import asyncio
import functools
import time
from colorama import Fore
from XAgentIO.exception import XAgentIOCloseError, XAgentIOTimeoutError
from XAgentIO.input.base import BaseInput
from inputimeout import inputimeout, TimeoutOccurred
import math


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
        except:
            pass

    return wrapper


class CommandLineInput(BaseInput):
    def __init__(self, do_interrupt: bool = False, max_wait_seconds: int = 600):
        super().__init__(do_interrupt, max_wait_seconds)

    async def run(self, input_data):
        if self.do_interrupt:
            data = await self.interrupt(input_data)
        else:
            data = input_data
        return data

    async def get_each_input(self, key, value, res, timeout):
        self.logger.typewriter_log(
            f"Now, ASK For {key}, Origin Input: {value}", Fore.RED, f""
        )
        self.logger.typewriter_log(
            f"Now, you can modify the current field by entering some information, and then press 'Enter' to continue, if you want to keep the original input, please enter '-1' and then press 'Enter':",
            Fore.GREEN,
        )
        temp = inputimeout(
            prompt=f"You have {timeout} seconds to input:\n", timeout=timeout
        )
        if temp == "-1":
            return value
        else:
            return temp

    async def get_input(self, origin_data):
        self.logger.typewriter_log(
            "Next, you can start modifying the original input by typing 'Y/y/yes' or skip this step by typing 'N/n/no' and then press 'Enter' to continue the loop:",
            Fore.RED,
        )
        update = inputimeout(
            prompt=f"You have to make a decision within 60 seconds:\n", timeout=60
        )
        res = {"args": {}}
        if update in ["y", "Y", "yes"]:
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
                    res["args"][key] = await self.get_each_input(
                        key, value, res, execute_time
                    )
                    end_time = time.time()
                    execute_time = math.floor(execute_time - (end_time - start_time))
            self.logger.info(f"modify the input, receive the data: {res}")
        else:
            res = origin_data
            self.logger.info("skip this step")
        self.logger.info("continue the loop")
        res["done"] = True
        return res

    async def interrupt(self, input_data):
        try:
            data = await self.get_input(input_data)
            return data
        except TimeoutOccurred:
            self.logger.error(f"Waiting timemout, close connection!")
            raise XAgentIOTimeoutError("timeout!")

    def close(self):
        raise XAgentIOCloseError("close connection!")
