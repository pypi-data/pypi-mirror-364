import os, sys

def load_my_library(lib_name, path_template=None):
    lib_abs_path = _expand_lib_path(lib_name, path_template)
    if lib_abs_path not in sys.path:
        sys.path.insert(0, lib_abs_path)
        return True
    return False

def unload_my_module(module_name, path_template=None):
    try:
        sys.path.remove(_expand_lib_path(module_name, path_template))
    except ValueError:
        pass
    unloaded = []
    for name in list(sys.modules):
        if name.startswith(module_name):
            unloaded.append(name)
            del sys.modules[name]
    return unloaded

def reload_my_library(lib_name, path_template=None):
    unload_my_module(lib_name, path_template=path_template)
    return load_my_library(lib_name, path_template=path_template)

def _expand_lib_path(lib_name, path_template):
    path_template = path_template or "$HOME/projects/{lib_name}/source/src"
    return os.path.expanduser(os.path.expandvars(path_template.format(lib_name=lib_name)))
