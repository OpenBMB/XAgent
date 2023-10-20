import os
import fnmatch
from typing import Any, Dict
from collections import defaultdict

from core.register import toolwrapper
from core.base import BaseEnv

@toolwrapper()
class FileSystemEnv(BaseEnv):
    """Provide a file system operation environment for Agent.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        filesystem_config = self.config['filesystem']
        
        self.ignored_list = filesystem_config["ignored_list"]
        self.work_directory = filesystem_config["work_directory"]
        self.max_entry_nums_for_level = filesystem_config["max_entry_nums_for_level"]
        if not os.path.exists(self.work_directory):
            os.mkdir(self.work_directory,mode=0o777)
        
    def _check_ignorement(self,path:str)->bool:
        for pattern in self.ignored_list:
            if fnmatch.fnmatch(path,pattern):
                return True
        return False
    
    def _is_path_within_workspace(self,path:str)->bool:
        common_prefix = os.path.commonprefix([os.path.realpath(path),
                                            os.path.realpath(self.work_directory)])
        return common_prefix == os.path.realpath(self.work_directory)
    
    def _is_path_exist(self,path:str)->bool:
        """Check if the path exists in the workspace.
        
        :param string path: The path to be checked.
        :return bool: `True` if the path exists, else `False`.
        """

        full_path = os.path.join(self.work_directory, path)
        if not self._is_path_within_workspace(full_path):
            raise ValueError(f"Path {path} is not within workspace.")
        return os.path.exists(full_path)

    def print_filesys_struture(self,return_root=False)->str:
        """Return a tree-like structure for all files and folders in the workspace. Use this tool if you are not sure what files are in the workspace.

        This function recursively walks through all the directories in the workspace
        and return them in a tree-like structure, 
        displaying all the files under each directory.
        
        Example:
        ```
        - root/
            - sub_directory1/
                - file1.txt
                - file2.txt
            - sub_directory2/
                - file3.txt
        ```

        :return string: The tree-like structure of the workspace.
        """
        full_repr = ''
        if return_root:
            full_repr += f'Global Root Work Directory: {self.work_directory}\n'

        folder_counts =  defaultdict(lambda: 0)
        for root, dirs, files in os.walk(self.work_directory):
            if self._check_ignorement(root):
                continue
            level = root.replace(self.work_directory, '').count(os.sep)
            indent = ' ' * 4 * (level)
            
            folder_counts[root] += 1
            if folder_counts[root] > self.max_entry_nums_for_level:
                full_repr += f'{indent}`wrapped`\n'
            
            full_repr += f'{indent}- {os.path.basename(root)}/\n'
            
            idx = 0
            subindent = ' ' * 4 * (level + 1) + '- '
            for f in files:
                if self._check_ignorement(f):
                    continue
                
                idx += 1
                if idx > self.max_entry_nums_for_level:
                    full_repr += f'{subindent}`wrapped`\n'
                    break
                full_repr += f'{subindent}{f}\n'


        return full_repr
    
    def read_from_file(self,filepath:str,line_number:int = 1)->str:
        """Open and read the textual file content in the workspace, you will see the content of the target file.
        Don't use this if the give `filepath` is writen or modified before, the content in `filepath` should be already returned.
        
        :param string filepath: The path to the file to be opened, always use relative path to the workspace root.
        :param integer? line_number: The starting line number of the content to be opened. Defaults to 1.
        :return string: The content of the file.
        """
        if not filepath.startswith(self.work_directory):
            filepath = filepath.strip('/')
            full_path = os.path.join(self.work_directory, filepath)        
        else:
            full_path = filepath
                
        if self._check_ignorement(full_path) or not os.path.isfile(full_path):
            raise FileNotFoundError(f"File {filepath} not found in workspace.")
        if not self._is_path_within_workspace(full_path):
            raise ValueError(f"File {filepath} is not within workspace.")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {filepath} not found in workspace.")

        content = ''
        with open(full_path, 'r') as f:
            lines = f.readlines(int(1e5))
            
        read_count = 0
        if not (abs(line_number) - 1 < len(lines)):
            raise ValueError(f"Line number {line_number} is out of range.")
        index = line_number if line_number >= 0 else len(lines) + line_number
        if index == 0:
            index = 1
            
        if line_number == 0:
            indexed_lines = lines
        elif line_number > 0:
            indexed_lines = lines[line_number-1:]
        else:
            indexed_lines = lines[line_number:]
            
        for line in indexed_lines:
            content += f'{index}'.rjust(5) + ': '
            content += line
            read_count += len(line)
            index += 1
        return content

    def write_to_file(self, filepath:str,content:str,truncating:bool = False,line_number:int = None, overwrite:bool = False)->str:
        """Write or modify the textual file lines based on `content` provided. 
        Return updated content of the file after modification so no further need to call `read_from_file` for this file. Create file if not exists.
        
        Example:
        ```
        In[0]: write_to_file('test.txt', 'Hello World!\\nA new line!')
        Out[0]: '1: Hello World!\\n2: A new line!'
        In[1]: write_to_file('test.txt', 'Hello World 1!', 2)
        Out[1]: '1: Hello World!\\n2: Hello World 1!\\n3: A new line!'
        In[2]: write_to_file('test.txt', 'Hello World 2!', 2, overwrite=True)
        Out[2]: '1: Hello World!\\n2: Hello World 2!\\n3: A new line!'
        ```
        
        :param string filepath: The path to the file to be modified, always use relative path to the workspace root.
        :param boolean? truncating: If `True`, the file will be truncated before writing, else will read current content before writing. Defaults to `False`.
        :param integer? line_number: The start line to modified file. Defaults to `None`, which means insert the new content at the end of the file. So do not provide this if you want to append the new content to the file.
        :param boolean? overwrite: If `True`, the new content will overwrite content started from `line_number` line. Defaults to `False`, which insert the new content at the `line_number` line.
        :param string content: The new content to be replaced with the old content.
        """
        if not filepath.startswith(self.work_directory):
            filepath = filepath.strip('/')
            full_path = os.path.join(self.work_directory, filepath)
        else:
            full_path = filepath
        if not self._is_path_within_workspace(full_path) or  self._check_ignorement(full_path):
            raise ValueError(f"File {filepath} is not within workspace.")
        
        if not os.path.exists(full_path):
            if line_number is None or line_number==0 or line_number == 1:
                os.makedirs(os.path.split(full_path)[0],exist_ok=True)
                open(full_path, 'w+').close()
            else:
                raise FileNotFoundError(f"File {filepath} not found in workspace.")
        elif not os.path.isfile(full_path):
            raise ValueError(f"File {filepath} is not a file.")
            
        # protential overflow
        if truncating:
            lines = []
        else:
            with open(full_path, 'r') as f:
                lines = f.readlines()
        
        
        new_lines = content.splitlines(keepends=True)
        if line_number is None:
            lines.extend(new_lines)
        else:
            if line_number >= 1:
                line_number -= 1
            if overwrite:
                lines[line_number: line_number+len(new_lines)] = new_lines
            else:
                lines[line_number: line_number] = new_lines 

        for idx, _ in enumerate(lines):
            if not lines[idx].endswith('\n'):
                lines[idx] += '\n'
                
        with open(full_path, 'w+') as f:
            f.writelines(lines)
            
        return self.read_from_file(filepath)
        

