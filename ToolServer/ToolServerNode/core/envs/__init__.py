from utils import import_all_modules_in_folder

__all__ = import_all_modules_in_folder(__file__,__name__)

"""
This script is for importing all the modules in a specified folder. The '__all__' variable is a list of public 
objects of that module, as interpreted by 'import *'. The import statement uses the following convention: if a 
package's __init__.py code defines a list named '__all__', it is taken to be the list of module names that 
should be imported when 'from package import *' is encountered. It imports everything until it encounters an 
import error.

The import_all_modules_in_folder function takes the current filename and module name as arguments and returns 
a list of all module names under the current folder.
"""