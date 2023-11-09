import asyncio

from config import CONFIG

from core.register import toolwrapper
from core.envs.filesystem import FileSystemEnv

CODE_FS = FileSystemEnv()

@toolwrapper()
async def run_interpreter(code:str=None,command:str=None,filename:str='code.py'):
    """The code interpreter tool that runs code and return the output.

    The `code` will be written to file `filename` and the `command` will be executed in a shell.
    Example:
    ```
    run_interpreter(code='print("hello world")',command='python code.py')
    ```

    :param string? code: The code to be written, default to `None`, which means no code will be written to file.
    :param string? command: The shell command to be executed should avoid requiring additional user input, default to `python {filename}`.
    :param string? filename: The filename to be written in mode `w`, default to `code.py`.

    """
    if code is not None and code != "" and filename != "":
        CODE_FS.write_to_file(filename,code)

    if command is None:
        command = f'python {filename}'
    exec_proc = await asyncio.create_subprocess_shell(
        'bash',
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
        cwd=CODE_FS.work_directory)
    
    ret = await asyncio.wait_for(exec_proc.communicate(command.encode()),timeout=CONFIG['shell']['timeout'])
    
    result = {
        'ReturnCode':exec_proc.returncode,
    }
    if ret[1]!=b'':
        result['Error'] = ret[1].decode()
    if ret[0]!=b'':
        result['Output'] = ret[0].decode()

    return result
