import importlib.util
import sys
from os import sep
from pathlib import Path


class Plugins():
    '''
    Loads plugins from source files
    '''

    def __init__(self, plugins_list):
        self.plugins = []
        self.hooks = {}

        for path in plugins_list:
            plugin_name = path.split(sep)[-2] # ie .../plugins/NAME/class.py
            print('loading: ' + plugin_name)
            plugin = self.import_source_file(path, f'pagegen_plugin_{plugin_name}')
            self.plugins.append(plugin)


    def import_source_file(self, fname, modname):
        """
        Import a Python source file and return the loaded module.

        Args:
            fname: The full path to the source file.  It may container characters like `.`
                or `-`.
            modname: The name for the loaded module.  It may contain `.` and even characters
                that would normally not be allowed (e.g., `-`).
        Return:
            The imported module

        Raises:
            ImportError: If the file cannot be imported (e.g, if it's not a `.py` file or if
                it does not exist).
            Exception: Any exception that is raised while executing the module (e.g.,
                :exc:`SyntaxError).  These are errors made by the author of the module!
        """
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location(modname, fname)
        if spec is None:
            raise ImportError(f"Could not load spec for module '{modname}' at: {fname}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[modname] = module
        try:
            spec.loader.exec_module(module)
        except FileNotFoundError as e:
            raise ImportError(f"{e.strerror}: {fname}") from e
        return module

