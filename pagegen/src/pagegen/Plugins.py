import importlib.util
import sys
from os import sep
from pathlib import Path


class Plugins():
    '''
    Loads plugins from source files and adds plugin hook functions to hook lists
    '''

    def __init__(self, plugins_list):
        self.plugins = []
        self.hooks = {}

        # Load plugin modules
        for path in plugins_list:
            plugin_name = path.split(sep)[-2] # ie .../plugins/NAME/class.py
            plugin = self.import_module_from_source(path, f'pgn_plugin_{plugin_name}')

            self.plugins.append(plugin)

        # Add any plugin hook functions to the hook methods
        for h in [
                'pre_build',
                'pre_build_lists',
                'post_build_lists',
                'page_dep_check',
                'pre_page_build',
                'post_page_build',
                'post_build'
            ]:
            self.hooks[h] = []

            # Add hook methods to hooks list
            for p in self.plugins:
                for func in dir(p):
                    if func == f'pgn_hook_{h}':
                        self.hooks[h].append(getattr(p, func))
                        break


    def import_module_from_source(self, fname, modname):
        '''
        Import a Python source file and return the loaded module
        '''

        spec = importlib.util.spec_from_file_location(modname, fname)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["module.name"] = mod
        spec.loader.exec_module(mod)

        return mod.Plugin()
