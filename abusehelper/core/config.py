import os
import sys
import imp
import hashlib
import inspect

def base_dir(depth=1):
    calling_frame = inspect.stack()[depth]
    calling_file = calling_frame[1]
    return os.path.dirname(os.path.abspath(calling_file))    

def relative_path(*path):
    return os.path.abspath(os.path.join(base_dir(depth=2), *path))

def load_module(module_name, relative_to_caller=True):
    base = base_dir(depth=2)

    path, name = os.path.split(module_name)
    if not path:
        if relative_to_caller:
            paths = [base]
        else:
            paths = None
        found = imp.find_module(name, paths)
        sys.modules.pop(name, None)
        return imp.load_module(name, *found)
    
    if relative_to_caller:
        module_name = os.path.join(base, module_name)
    module_file = open(module_name, "r")
    try:
        name = hashlib.md5(module_name).hexdigest()
        sys.modules.pop(name, None)
        return imp.load_source(name, module_name, module_file)
    finally:
        module_file.close()

def load_configs(module_name, config_func_name="configs"):
    module = load_module(module_name, False)
    configs = getattr(module, config_func_name, None)

    if configs is None or not callable(configs):
        raise ImportError("no callable %r defined" % config_func_name)
    return configs()
