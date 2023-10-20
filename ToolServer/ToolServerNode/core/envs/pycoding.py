import os
import re
import asyncio
import nbformat

from typing import Dict,Any
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError,DeadKernelError
from nbclient.client import ensure_async

from core.register import toolwrapper
from core.base import BaseEnv
from core.exceptions import ToolExecutionError

@toolwrapper()
class PythonNotebook(BaseEnv):
    """Python Notebook Environment. Provide a notebook interface to run python code."""
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        filesystem_config = self.config['filesystem']
        
        self.work_directory = filesystem_config["work_directory"]
        
        self.nb_cfg = self.config['notebook']
        
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory,mode=0o777)

        # make a new notebook
        self.nb = nbformat.v4.new_notebook(
            metadata = {'kernelspec': {'name': 'python', 'language': 'python', 'display_name': 'python'}})
        self.nbc = NotebookClient(self.nb,timeout=self.nb_cfg['timeout'])
    
    async def _running(self):
        if self.nbc.kc is not None:
            return await ensure_async(self.nbc.kc.is_alive())
        return False
    
    async def _reset(self):
        if await self._running():
            await self.nbc._async_cleanup_kernel()
        self.nbc.create_kernel_manager()
        await self.nbc.async_start_new_kernel(cwd=self.work_directory)
        await self.nbc.async_start_new_kernel_client()

    @staticmethod
    def _fix_escape(problematic_code: str) -> str:
        for str_sign in ['"', "'", '"""', "'''"]:

            pattern = rf'{str_sign}(.*?){str_sign}'
            in_line_strs = re.findall(pattern, problematic_code, re.DOTALL)
            replaced_in_line_strs = []
            for in_line_str in in_line_strs:
                replaced_in_line_strs.append(in_line_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))
            for original_str, modified_str in zip(in_line_strs, replaced_in_line_strs):
                fixed_code = problematic_code.replace(f'{str_sign}' + original_str + f'{str_sign}',
                                                            f'{str_sign}' + modified_str + f'{str_sign}')

        return fixed_code

        
    async def execute_cell(self,code:str,cell_index:int=None,reset:bool=False) -> str:
        """Create or replace a notebook cell and execute it, return the output.
        Use this tool to test your idea quickly. Carefully examine the output to make sure it is what you want.
        
        Example:
        ```
        In[0]: code='print("hello world")' # This will create a new cell and execute it.
        Out[0]: ['cell_index: 0', 'hello world']
        In[1]: code='print("hello world")',cell_index=0 # This will overwrite the first cell and execute it.
        In[2]: code='print("hello world")',cell_index=-1 # This will overwrite the last cell and execute it.
        ```
        
        :param string code: python code to be executed, make sure it is valid python code with right format. don't provide shell command that started with '!' here.
        :param integer? cell_index: the index of the cell to be insert and overwrite `code`, default to `None`, which means append new cell.
        :param boolean? reset: whether to reset the kernel before executing the code. Default to `False`.
        :return string: execution result.
        """
        # code = self._fix_escape(code)
        if reset or not await self._running():
            await self._reset()
        if cell_index is None or cell_index == len(self.nb.cells) or len(self.nb.cells) == 0:
            self.nb.cells.append(nbformat.v4.new_code_cell(code))
            cell_index = len(self.nb.cells)-1
        else:
            self.nb.cells[cell_index] = nbformat.v4.new_code_cell(code)
        
        try:
            await self.nbc.async_execute_cell(self.nb.cells[-1],len(self.nb.cells)-1)
        except CellExecutionError as e:
            pass
        except DeadKernelError as e:
            await self._reset()
            
        nbformat.write(self.nb,os.path.join(self.work_directory,self.nb_cfg['save_name']))
        
        return self._format_outputs(self.nb.cells[cell_index].outputs,cell_index,reraise=True,return_binary=True)
        
    def print_notebook(self)->str:
        """print all notebook cells' content and output.
        
        :return string: all notebook cells description.
        """
        ret = ''
        for i,cell in enumerate(self.nb.cells):
            ret += f'= Cell {i} =\n'
            if cell['cell_type'] == 'code':
                ret += f'{cell["source"]}\n'
                if len(cell['outputs']) != 0:
                    ret += f'= Output {i} =\n'
                    ret += f'{self._format_outputs(cell["outputs"])}\n'
        return ret
    def _format_outputs(self,outputs,cell_index=None,reraise=False,return_binary=False):
        ret = None
        if len(outputs) == 0:
            ret = '' if cell_index is None else f'cell_index: {cell_index}'
        elif len(outputs) == 1:
            if cell_index is not None:
                ret = {
                    'type':'composite',
                    'data':[
                        f'cell_index: {cell_index}',
                        self._format_output(outputs[0],cell_index,reraise,return_binary)
                    ]
                }
            else:
                ret = self._format_output(outputs[0],cell_index,reraise,return_binary)
        else:
            ret = {
                'type':'composite',
                'data':[
                    self._format_output(output,cell_index,reraise,return_binary) for output in outputs
                ]
            }
            if cell_index is not None:
                ret['data'].insert(0,f'cell_index: {cell_index}')
        return ret
        
    def _format_output(self,output,cell_index=None,reraise=False,return_binary=False):
        def format_single_data(data,data_type:str):
            if data_type.startswith('image/'):
                return {
                    'type': 'binary',
                    'media_type':data_type,
                    'data': data if return_binary else '`Wrapped`'
                }
            elif data_type.startswith('text/'):
                return ''.join(data)
            elif data_type.startswith('application/'):
                return data
            return data
            
        ret = None
        match output['output_type']:
            case 'execute_result' | 'display_data':
                keys = list(output['data'].keys())
                if 'text/html' in keys and 'text/plain' in keys:
                    keys.remove('text/html') # remove html
                if len(keys) == 1:
                    ret = format_single_data(output['data'][keys[0]],keys[0])
                elif len(keys) > 1:
                    ret = {
                        'type': 'composite',
                        'data':[]
                    }
                    for k in keys:
                        ret['data'].append(format_single_data(output['data'][k],k))
                    
            case 'error':
                if reraise:
                    raise ToolExecutionError(f'cell_index: {cell_index}\n'+'\n'.join(output['traceback']))
                else:
                    return '\n'.join(output['traceback'])
            case 'stream':
                ret = output['text']
            case _:
                ret = output
        return ret

    
