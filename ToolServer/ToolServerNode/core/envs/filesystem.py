import os
import fnmatch
from typing import Any, Dict

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

    def print_filesys_struture(self,recursive=True,return_root=False)->str:
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

        if recursive:
            for root, dirs, files in os.walk(self.work_directory):
                if self._check_ignorement(root):
                    continue
                level = root.replace(self.work_directory, '').count(os.sep)
                indent = ' ' * 4 * (level)
                full_repr += f'{indent}{os.path.basename(root)}/\n'
                subindent = ' ' * 4 * (level + 1)
                for f in files:    
                    if self._check_ignorement(f):
                        continue
                    full_repr += f'{subindent}{f}\n'
        else:
            for file in os.listdir(self.work_directory):
                if self._check_ignorement(file):
                    continue
                indent = ' ' * 4
                if os.path.isdir(file):
                    full_repr += f'{indent}{file}/*wrapped*\n'
                else:
                    full_repr += f'{indent}{file}\n'
        return full_repr
    
    def read_from_file(self,filepath:str,start_index:int = 0)->str:
        """Open and read the textual file content in the workspace, you will see the content of the target file.
        Don't use this if the give `filepath` is writen or modified before, the content in `filepath` should be already returned.
        
        :param string filepath: The path to the file to be opened, always use relative path to the workspace root.
        :param integer? start_index: The starting line number of the content to be opened. Defaults to 0.
        :return string: The content of the file.
        """
        if not filepath.startswith(self.work_directory):
            filepath = filepath.strip('/')
            full_path = os.path.join(self.work_directory, filepath)            
        if self._check_ignorement(full_path) or not os.path.isfile(full_path):
            raise FileNotFoundError(f"File {filepath} not found in workspace.")
        if not self._is_path_within_workspace(full_path):
            raise ValueError(f"File {filepath} is not within workspace.")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {filepath} not found in workspace.")

        content = ''
        with open(full_path, 'r') as f:
            lines = f.readlines(int(1e6))
            
        read_count = 0
        index = start_index if start_index >= 0 else len(lines) + start_index
        indexed_lines = lines[start_index:]
        for line in indexed_lines:
            content += f'{index}'.rjust(5) + ': '
            content += line
            read_count += len(line)
            index += 1
        return content
    
    def write_to_file(self, filepath:str, content:str):
        """Write the textual file in the workspace with the content provided. 
        Will automatically create the file if it does not exist. Also overwrite the file content if it already exists. If you want to append content to the file, use `modify_file` instead.
        Better check if the file exists before directly writing to it. 
        Return content of the file after writing.
        
        :param string filepath: The path to the file to be saved, always use relative path to the workspace root.
        :param string content: The content to be saved.
        """
        if not filepath.startswith(self.work_directory):
            filepath = filepath.strip('/')
            full_path = os.path.join(self.work_directory, filepath)

        # if not os.path.isfile(full_path):
        #     raise FileNotFoundError(f"File {filepath} not found in workspace.")

        if not self._is_path_within_workspace(full_path):
            raise ValueError(f"File {filepath} is not within workspace.")
        
        os.makedirs(os.path.split(full_path)[0],exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
            
        return self.read_from_file(filepath)

    def modify_file(self, filepath:str,new_content:str, start_index:int = None, end_index:int = None)->str:
        """Modify the textual file lines in slice [start_index:end_index] based on `new_content` provided. Return content of the file after modification so no further need to call `read_from_file`.
        filepath_content_lines[start_index:end_index] = new_content
        
        Example:
        ```
        In[0]: modify_file('test.txt', 'Hello World!') # This will insert a new line `Hello World!` at the end of the file `test.txt`.
        In[1]: modify_file('test.txt', 'Hello World!', 0) # This will insert a new line `Hello World!` at the begin of the file `test.txt`.
        In[2]: modify_file('test.txt', 'Hello World!', 0, 1) # This will replace the first line of the file `test.txt` with `Hello World!`. 
        ```
        
        :param string filepath: The path to the file to be modified, always use relative path to the workspace root.
        :param string new_content: The new content to be replaced with the old content.
        :param integer? start_index: The start position in slice to modified file lines. Defaults to `None`, which means insert the new content at the end of the file. So do not provide this if you want to append the new content to the file.
        :param integer? end_index: The end posistion in slice to modified file lines. Defaults to the value of `start_index`, which means if `start_index` provided, insert the new content at the `start_index` line.
        """
        if not filepath.startswith(self.work_directory):
            filepath = filepath.strip('/')
            full_path = os.path.join(self.work_directory, filepath)
        if self._check_ignorement(full_path) or not os.path.isfile(full_path) and not ((start_index is None or start_index==0)and end_index is None):
            raise FileNotFoundError(f"File {filepath} not found in workspace.")
        
        if not self._is_path_within_workspace(full_path):
            raise ValueError(f"File {filepath} is not within workspace.")
        
        # protential overflow
        with open(full_path, 'r') as f:
            lines = f.readlines()
        
        if start_index is None:
            lines.extend(new_content.splitlines(keepends=True))
        else:
            if end_index is None:
                end_index = start_index
            lines[start_index: end_index] = new_content.splitlines(keepends=True)

        for idx, _ in enumerate(lines):
            if not lines[idx].endswith('\n'):
                lines[idx] += '\n'
                
        with open(full_path, 'w+') as f:
            f.writelines(lines)
            
        return self.read_from_file(filepath)
        

