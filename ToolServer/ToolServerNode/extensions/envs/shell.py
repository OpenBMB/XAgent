import subprocess
import sys
import select
import os
import io

from typing import Union,Dict,Any
from core.base import BaseEnv
from core.register import toolwrapper,get_func_name
from core.exceptions import OutputNotReady

def read_pipe(pipe:Union[io.StringIO,io.BytesIO],text=True)->Union[str,bytes]:
    """Reading the `subprocess.PIPE` when readable.
    If `text` is `True`, return str, else return bytes.
    """
    output = '' if text else b''
    while True:
        ready_fds,_,_ = select.select( [pipe.fileno()],[],[],0.01)
        if len(ready_fds) == 0:
            break
        output += os.read(ready_fds[0],16384).decode() if text else os.read(ready_fds[0],16384)

    return output

# @toolwrapper()
class ShellEnv(BaseEnv):
    """Provide and maintain an interactive shell environment.
    """
    def __init__(self,
                 config:Dict[str,Any]):
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
    def running(self)->bool:
        """`True` if shell is running, else `False`
        """
        if hasattr(self,'running_proc') and isinstance(self.running_proc,subprocess.Popen):
            if self.running_proc.poll() is None:
                return True
        return False
    
    def _restart(self,program:str=None,shell:bool=True):
        f"""Restart the shell.
        
        :param string? program: The program to be executed in shell, the default is `{self.shell_program}`.
        """
        self._kill()
        if program is None:
            program = self.shell_program
        self.running_proc = subprocess.Popen(
            program, # adding more shells support
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.work_directory,
            shell=shell,
            text=True
        )
        self.output_fileno = [self.running_proc.stdout.fileno(),self.running_proc.stderr.fileno()]
    
    def _terminate(self):
        """Terminate the shell.
        """
        if self.running:
            self.running_proc.terminate()

    def _kill(self):
        """Kill the shell.
        """
        if self.running:
            self.running_proc.kill()

    def read_stdout(self, probe: bool = False) -> str:
        """Read the stdout stream of the shell. If stderr is not empty, it will be returned instead.
        
        Empty string will be returned if both stdout and stderr are empty.
        You can use this function to check if the shell has new content to be read for a running process takes a while.
        
        :param boolean? probe: If `True`, the function will return immediately if no output is ready, else it will raise `OutputNotReady` exception and request to call functions in `next_calling` to get result.
        """
        if not self.running:
            raise RuntimeError('Shell is not running!')
        
        ready_fds,_,_ = select.select(self.output_fileno,[],[],0.01)
        if probe and len(ready_fds) == 0 :
            raise OutputNotReady('Output is not ready!',next_calling=get_func_name(self.read_stdout,self),arguments={'probe':True})
        
        error = read_pipe(self.running_proc.stderr)
        if error:
            return error

        return read_pipe(self.running_proc.stdout)
    
    
    def write_stdin(self, content:str) -> str:
        """Write the stdin stream of the shell and get instant feedback from stderr or stdout.
        
        Example:
        ```
        write_stdin('echo "hello world"')
        ```
        This will execute the command `echo "hello world"` in shell and return the output `hello world`.
        
        :param string content: The content to be written.
        """

        # removed temporarily, maybe put back later?
        # You may need to call `read_stdout` to get further feedback for running process takes a while.
        if not self.running:
            raise RuntimeError('Shell is not running!')
        if not content.endswith("\n"):
            content += "\n"
        self.running_proc.stdin.write(content)
        self.running_proc.stdin.flush()
        
        ready_fds,_,_ = select.select(self.output_fileno,[],[],0.01)
        if len(ready_fds) == 0:
            raise OutputNotReady('Output is not ready!',next_calling=get_func_name(self.read_stdout,self),arguments={'probe':True})
        
        return 'Instant shell output: ' + self.read_stdout()
    
