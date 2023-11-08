import subprocess
import sys
import select
import os
import io

from typing import Union, Dict, Any
from core.base import BaseEnv
from core.register import toolwrapper, get_func_name
from core.exceptions import OutputNotReady


def read_pipe(pipe: Union[io.StringIO, io.BytesIO], text=True) -> Union[str, bytes]:
    """
    Reads the `subprocess.PIPE` when readable.
    
    Args:
        pipe (Union[io.StringIO, io.BytesIO]): The pipe to be read.
        text (bool, optional): Defaults to True. If True, the function returns str, else it returns bytes.
    
    Returns:
        Union[str, bytes]: The content read from the provided pipe.
    """
    output = '' if text else b''
    while True:
        ready_fds, _, _ = select.select([pipe.fileno()], [], [], 0.01)
        if len(ready_fds) == 0:
            break
        output += os.read(ready_fds[0],16384).decode() if text else os.read(ready_fds[0],16384)

    return output

# @toolwrapper()
class ShellEnv(BaseEnv):
    """
    Class that provides and maintains an interactive shell environment, derived from the BaseEnv class.
    
    Attributes:
        shell_program (str): The shell program that will be used. It depends on the operating system.
        work_directory (str): The working directory for the shell environment.
        running_proc (subprocess.Popen): The running shell process.
        output_fileno (str): File number descriptor for the output of the running process.
    """

    def __init__(self,
                 config: Dict[str, Any]):
        """
        Constructor for the ShellEnv class.
        
        Args:
            config (Dict[str, Any]): Configuration parameters for the shell environment.
        """
        super().__init__(config)

        if sys.platform.startswith("linux"):
            self.shell_program = "bash"
        elif sys.platform.startswith("darwin"):
            self.shell_program = "zsh"
        else:
            self.shell_program = "powershell"
        self.work_directory = self.config['filesystem']['work_directory']
        self._restart()

    @property
    def running(self) -> bool:
        """
        Checks whether the shell is running or not.
        
        Returns:
            bool: True if the shell is running, False otherwise.
        """
        if hasattr(self, 'running_proc') and isinstance(
                self.running_proc, subprocess.Popen):
            if self.running_proc.poll() is None:
                return True
        return False

    def _restart(self, program: str = None, shell: bool = True):
        """
        Restarts the shell.
        
        Args:
            program (str, optional): The program to be executed in shell. Defaults to {self.shell_program}.
            shell (bool, optional): Whether to use the shell as the program to execute or not. Defaults to True.
        """
        self._kill()
        if program is None:
            program = self.shell_program
        self.running_proc = subprocess.Popen(
            program,  # adding more shells support
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.work_directory,
            shell=shell,
            text=True
        )
        self.output_fileno = [self.running_proc.stdout.fileno(),self.running_proc.stderr.fileno()]

    def _terminate(self):
        """
        Terminates the shell.
        """
        if self.running:
            self.running_proc.terminate()

    def _kill(self):
        """
        Kills the shell.
        """
        if self.running:
            self.running_proc.kill()

    def read_stdout(self, probe: bool = False) -> str:
        """
        Reads the stdout stream of the shell. If stderr is not empty, it will be returned instead. 
        An empty string will be returned if both stdout and stderr are empty. You can use this function to check if the shell has new content to be read for a running process takes a while.
        
        Args:
            probe (bool, optional): Defaults to False. If True, the function will return immediately 
                                    if no output is ready, else it will raise `OutputNotReady` exception 
                                    and request to call functions in `next_calling` to get the result.
        
        Returns:
            str: The content read from the stdout or stderr stream.
        
        Raises:
            RuntimeError: If the shell is not running.
            OutputNotReady: While using probe mode, if stderr and stdout are empty.
        """
        if not self.running:
            raise RuntimeError('Shell is not running!')

        ready_fds, _, _ = select.select(self.output_fileno, [], [], 0.01)
        if probe and len(ready_fds) == 0:
            raise OutputNotReady('Output is not ready!', next_calling=get_func_name(self.read_stdout, self), arguments={'probe': True})

        error = read_pipe(self.running_proc.stderr)
        if error:
            return error

        return read_pipe(self.running_proc.stdout)

    def write_stdin(self, content: str) -> str:
        """
        Writes into the stdin stream of the shell and gets instant feedback from stderr or stdout.
        
        Example:
        ```
        write_stdin('echo "hello world"')
        ```
        This will execute the command `echo "hello world"` in shell and return the output `hello world`.
        
        Args:
            content (str): The content to be written.
        
        Returns:
            str: Instant shell output.
        
        Raises:
            RuntimeError: If the shell is not running.
            OutputNotReady: If stderr and stdout are empty just after writing into stdin.
        """
        if not self.running:
            raise RuntimeError('Shell is not running!')
        if not content.endswith("\n"):
            content += "\n"
        self.running_proc.stdin.write(content)
        self.running_proc.stdin.flush()

        ready_fds, _, _ = select.select(self.output_fileno, [], [], 0.01)
        if len(ready_fds) == 0:
            raise OutputNotReady('Output is not ready!', next_calling=get_func_name(self.read_stdout, self), arguments={'probe': True})

        return 'Instant shell output: ' + self.read_stdout()