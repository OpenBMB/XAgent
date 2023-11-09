import asyncio
from config import CONFIG

from core.register import toolwrapper
from core.exceptions import ToolExecutionError

ALL_SHELLS: dict[int, asyncio.subprocess.Process] = {}


async def async_read_pipe(pipe: asyncio.StreamReader):
    ret = b''
    while True:
        try:
            ret += await asyncio.wait_for(pipe.readline(), timeout=0.01)
        except asyncio.TimeoutError:
            return ret
async def read_exec_proc_display(exec_proc: asyncio.subprocess.Process):
    display = ""
    for pipe, name in zip([exec_proc.stderr,exec_proc.stdout], ['stderr','stdout']):
        ret = await async_read_pipe(pipe)
        if ret != b'':
            display += f'\n{name}:\n'+ ret.decode()
    return display

@toolwrapper()
async def shell_command_executor(command: str = '', run_async: bool = False, shell_id: int = None, kill:bool = False):
    """The shell tool that execute shell command in root privilege, return the output and error. 
    You can use this tool to install packages, download files, run programs, etc.
    Set run_async=True to run the command in a new thread and return instantly if your command is time costly like install packages, host services. 
    Example:
    ```
    In: shell_command_executor(command='echo "hello world"')
    Out: "hello world"
    In: shell_command_executor(command='sleep 10', run_async=True)
    Out: {'shell_id': 0} # You can use this id to read the output and error later.
    In: shell_command_executor(shell_id=0, kill=True)
    Out: "" # The shell 0 will be killed.
    ```

    :param string? command: The shell command to be executed, must avoid command requiring additional user input. Default is empty string.
    :param boolean? run_async: Whether to run the command asynchronously, default is False. If True, call this tool again with shell_id to get the final output and error. 
    :param integer? shell_id: The id of shell to execute command, default is None, which means running in a new shell. Change this to execute command in the same shell.
    :param boolean? kill: If True, kill the shell which runs the command after execution. Default is False. Don't use any other kill command!
    """
    if shell_id is not None:
        exec_proc = ALL_SHELLS.get(shell_id, None)
        if exec_proc is None:
            raise ToolExecutionError(
                {'Error': 'Shell not found or has been closed.'})
        if exec_proc.returncode is not None:
            print(exec_proc.returncode)
            ALL_SHELLS.pop(shell_id)
            raise ToolExecutionError({'Error': 'Shell has been closed.'})

    else:
        exec_proc = await asyncio.create_subprocess_shell(
            'bash',
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            cwd=CONFIG['filesystem']['work_directory'])
        shell_id = max(ALL_SHELLS.keys(), default=-1) + 1
        ALL_SHELLS[shell_id] = exec_proc

    if not run_async:
        try:
            ret = await asyncio.wait_for(exec_proc.communicate(command.encode()), timeout=CONFIG['shell']['timeout'])
        except asyncio.TimeoutError:
            des = "Timeout while executing command."
            if kill:
                des += " Shell has been killed."
                exec_proc.kill()
            display = await read_exec_proc_display(exec_proc)
            if display != "":
                des += " But get some response:" + display
                
            raise ToolExecutionError(des)
            
        ALL_SHELLS.pop(shell_id)

        result = {
            'ReturnCode': exec_proc.returncode,
            'display': ''
        }
        if ret[1] != b'':
            result['display'] += f'\nstderr:\n'+ret[1].decode()
        if ret[0] != b'':
            result['display'] = f'\nstdout:\n'+ret[0].decode()
            
        if result['ReturnCode'] != 0 and not kill:
            raise ToolExecutionError(result)
        return result
    else:
        if command[-1] != '\n':
            command += '\n'
        exec_proc.stdin.write(command.encode())
        await exec_proc.stdin.drain()
        await asyncio.sleep(5)
        result = {'shell_id': shell_id , 'display':await read_exec_proc_display(exec_proc)}
        if result['display'] == "":
            await asyncio.sleep(30)
            result['display'] = await read_exec_proc_display(exec_proc)
        if kill:
            exec_proc.kill()
            ALL_SHELLS.pop(shell_id)
            result['status'] = 'shell thread has been killed'
        else:
            result['status'] = 'shell still running, no return code'
        return result
