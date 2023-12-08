"""A simple spinner module"""
import itertools
import sys
import threading
import time


class Spinner:
    """
    A simple class for implementing a spinner functionality. It starts a new
    thread on initialization and can be used in with statement.
    
    Attributes:
        delay (float): The delay between each spinner update.
        message (str): The message to display along with the spinner.
        plain_output (bool): Whether to display the spinner or not.
        running (bool): Indicates whether the spinner is currently running.
        spinner (iter): An infinite iterator cycling over spinner characters.
        spinner_thread (Thread): The thread on which the spinner is running.
    """

    def __init__(
        self,
        message: str = "Loading...",
        delay: float = 0.1,
        plain_output: bool = False,
    ) -> None:
        """Initializes the spinner with the given message, delay, and output type.

        Args:
            message (str): The message to display. Defaults to 'Loading...'.
            delay (float): The delay in seconds between each spinner update. Defaults to 0.1.
            plain_output (bool): If True, the spinner will not be displayed.
                                  Defaults to False.
        """
        self.plain_output = plain_output
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.delay = delay
        self.message = message
        self.running = False
        self.spinner_thread = None

    def spin(self) -> None:
        """Runs the spinner while it is marked as running.

        If plain_output is set to True, it will only print the message and return.
        """
        if self.plain_output:
            self.print_message()
            return
        while self.running:
            self.print_message()
            time.sleep(self.delay)

    def print_message(self):
        """
        Prints the message with spinner symbol at the beginning and then erases it.
        """
        sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
        sys.stdout.write(f"{next(self.spinner)} {self.message}\r")
        sys.stdout.flush()

    def __enter__(self):
        """Sets the running marker to True and starts the spinner thread."""
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """Stops the spinner.

        Args:
            exc_type (Exception): The exception type.
            exc_value (Exception): The exception value.
            exc_traceback (Exception): The exception traceback.
        """
        self.running = False
        if self.spinner_thread is not None:
            self.spinner_thread.join()
        sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
        sys.stdout.flush()

    def update_message(self, new_message, delay=0.1):
        """Updates the message and the delay for the spinner.

        Args:
            new_message (str): New message to display.
            delay (float): The delay in seconds between each spinner update.
                           Defaults to 0.1.
        """
        self.delay = delay
        self.message = new_message
        if self.plain_output:
            self.print_message()