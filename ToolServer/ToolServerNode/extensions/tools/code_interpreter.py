import asyncio

from config import CONFIG

from core.register import toolwrapper
from core.envs.filesystem import FileSystemEnv

CODE_FS = FileSystemEnv()

@toolwrapper()
async def run_interpreter(code:str=None, command:str=None, filename:str='code.py'):
    """The code interpreter tool that runs code and return the output.

    The 'code' will be written to file 'filename' and then 'command' will be executed in a shell. 
    If 'command' is not provided, 'python {filename}' will be used as the default.
    The output includes the return code, error message (if any), and the command output (if any). 

    Args: 
        code (str, optional): The code to be written to the file. Default is None.
        command (str, optional): The shell command to be executed. Default is None.
        file (str, optional): The file name where the code will be written. Default is 'code.py'.

    Returns: 
        dict: A dictionary containing 'ReturnCode', 'Error' (if any), and 'Output' (if any).

    Raises:
        asyncio.TimeoutError: If the execution of the command takes more than 'shell' key value (in seconds) 
        from the CONFIG dictionary.

    Usage:
        run_interpreter(code='print("hello world")',command='python code.py')
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