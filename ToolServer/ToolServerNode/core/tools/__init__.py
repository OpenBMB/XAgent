"""
This module provides a utility function to import all modules 
in a specified folder.

The "__all__" variable is a list that defines the public interface of a module.
Here it is utilized to dynamically import all modules in the current directory.
"""

from utils import import_all_modules_in_folder

# dynamically import all modules in the current directory 
__all__ = import_all_modules_in_folder(__file__,__name__)