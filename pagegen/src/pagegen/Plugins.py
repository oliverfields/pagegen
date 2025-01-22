from os.path import basename, getmtime, join, isdir, dirname
from os import walk, listdir
from Common import Common
from pickle import load
from sys import path as syspath, modules
from importlib import import_module


class Plugins(Common):
    '''
    Load plugins using caching
    '''

    def __init__(self, site_plugin_dir, pgn_plugin_dir, site_cache_dir, settings={}, env={}):
        self.site_plugin_dir = site_plugin_dir
        self.pgn_plugin_dir = pgn_plugin_dir
        self.cache_dir = join(site_cache_dir, self.__class__.__name__)
        self.hooks_cache_file_name = 'hooks'
        self.hooks_cache_path = join(self.cache_dir, self.hooks_cache_file_name)
        self.settings = settings
        self.env = env


    def write_cache(self):
        self.pickle_object(self.cache_dir, self.hooks_cache_file_name, self.hooks)
        #self.pickle_object(self.cache_dir, 'plugins', self.plugins)


    def load_plugin_hooks(self):
        '''
        Load plugins from cache if exists, only load plugins that are defined in .pgn_env
        '''

        # First look for builtin plugins
        pgn_plugins = self.find_plugins(self.pgn_plugin_dir)
        site_plugins = self.find_plugins(self.site_plugin_dir)

        # Make list of plugins that only exist in pgn or site, if in both choose site ones

        all_plugins_dict = {}
        for pp in pgn_plugins:
            name = basename(pp).replace('.py', '')
            all_plugins_dict[name] = pp

        for sp in site_plugins:
            name = basename(sp).replace('.py', '')
            all_plugins_dict[name] = sp

        all_plugins = []
        for k, v in all_plugins_dict.items():
            all_plugins.append(v)

        if all_plugins == []:
            self.log_info('No plugins found')
            return

        # Get most recent changed time for plugin files
        for src in all_plugins:
            for subdir, dirs, files in walk(dirname(src)):
                for file in files:
                    f = join(subdir, file)
                    fmtime = getmtime(f)

                    try:
                        if last_plugins_change < fmtime:
                            last_plugins_change = fmtime
                    except UnboundLocalError:
                        last_plugins_change = fmtime


        # Add plugin dirs to, site first, then pgn
        for d in site_plugins:
            syspath.append(dirname(d))

        for d in pgn_plugins:
            syspath.append(dirname(d))


        try:
            if getmtime(self.hooks_cache_path) >= last_plugins_change:
                self.log_info('Loading plugins from cache')

                with open(self.hooks_cache_path, 'rb') as f:
                    self.hooks = load(f)
            else:
                self.log_info('Plugin cache stale: Initalizing plugins')
                self.plugins = self.load_plugins(all_plugins)
        except NotADirectoryError:
            self.log_info('No plugin directory found: Initalizing plugins')
            self.plugins = self.load_plugins(all_plugins)
        except FileNotFoundError:
            self.log_info('No plugin cache found: Initalizing plugins')
            self.plugins = self.load_plugins(all_plugins)
        except EOFError:
            self.log_info('Corrupted plugin cache: Initalizing plugins')
            self.plugins = self.load_plugins(all_plugins)


    def find_plugins(self, dir_name):

        plugin_sources = []

        try:
            for p in listdir(dir_name):
                full_path = join(dir_name,p)
                if isdir(full_path) and not p.startswith('__'):
                    # Check plugin enabled in env
                    if f'plugin_{p}' in self.env.sections():
                        plugin_path = join(full_path, p) + '.py'
                        plugin_sources.append(plugin_path)
        except FileNotFoundError:
            pass

        return plugin_sources


    def load_plugins(self, plugins):
        self.plugins = []
        self.hooks = {}

        # Load plugin modules
        for path in plugins:
            plugin_name = basename(path).replace('.py', '')

            self.log_info('Loading plugin: ' + path)

            module = import_module(plugin_name)
            plugin_class = getattr(module, 'Plugin')
            plugin_instance = plugin_class()

            self.plugins.append(plugin_instance)

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
        spec.loader.exec_module(mod)
        modules[modname] = mod

        return mod.Plugin()

