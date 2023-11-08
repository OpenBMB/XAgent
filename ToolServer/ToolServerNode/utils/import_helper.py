import os
import importlib
def import_all_modules_in_folder(file,name):
    current_dir = os.path.dirname(file)
    all_modules = []
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isfile(item_path) and item != '__init__.py' and item.endswith('.py'):
            module_name = item[:-3]
        elif os.path.isdir(item_path) and item != '__pycache__' and os.path.exists(os.path.join(item_path, '__init__.py')) and os.path.isfile(os.path.join(item_path, '__init__.py')):
            module_name = item
        else:
            continue

        full_module_path = f"{name}.{module_name}"
        # print(module_name,full_module_path)
        imported_module = importlib.import_module(full_module_path)
        globals()[module_name] = imported_module
        all_modules.append(imported_module)
    return all_modules