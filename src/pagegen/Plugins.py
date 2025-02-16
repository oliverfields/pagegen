from os.path import basename, getmtime, join, isdir, dirname
from pagegen.constants import SITE_CONF
from os import walk, listdir
from pagegen.Common import Common
from pickle import load
from sys import path as syspath, modules
from importlib import import_module
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Plugins(Common):
    '''
    Load plugins using caching
    '''

    def __init__(self, site_plugin_dir, pgn_plugin_dir, site_cache_dir, site_dir, conf={}):
        self.site_plugin_dir = site_plugin_dir
        self.pgn_plugin_dir = pgn_plugin_dir
        self.cache_dir = join(site_cache_dir, self.__class__.__name__)
        self.plugin_cache_file_name = 'plugins'
        self.plugin_cache_path = join(self.cache_dir, self.plugin_cache_file_name)
        self.site_conf_path = join(site_dir, SITE_CONF)
        self.conf = conf
        self.load_plugins()


    def load_plugins(self):
        '''
        Load plugins from cache if exists, only load plugins that are defined in site config
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
            logger.warning('No plugins found')
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

        # Use cache if it is newer than both mtimes of site conf and plugin files
        try:
            cache_mtime = getmtime(self.plugin_cache_path)
            if cache_mtime >= last_plugins_change and cache_mtime >= getmtime(self.site_conf_path):
                logger.debug('Loading plugins from cache')

                with open(self.plugin_cache_path, 'rb') as f:
                    self.plugins = load(f)

                return
            else:
                logger.debug('Plugin cache stale: Initalizing plugins')
        except NotADirectoryError:
            logger.debug('No plugin directory found: Initalizing plugins')
        except ModuleNotFoundError:
            logger.debug('Plugin module not found: Initalizing plugins')
        except FileNotFoundError:
            logger.debug('No plugin cache found: Initalizing plugins')
        except EOFError:
            logger.warning('Corrupted plugin cache: Initalizing plugins')

        self.find_and_load_plugins(all_plugins)

        self.pickle_object(self.cache_dir, self.plugin_cache_file_name, self.plugins)


    def find_plugins(self, dir_name):

        plugin_sources = []

        try:
            for p in listdir(dir_name):
                full_path = join(dir_name,p)
                if isdir(full_path) and not p.startswith('__'):
                    # Check plugin enabled in conf
                    if p in self.conf['site']['enabled_plugins']:
                        plugin_path = join(full_path, p) + '.py'
                        plugin_sources.append(plugin_path)
        except FileNotFoundError:
            pass

        return plugin_sources


    def find_and_load_plugins(self, plugin_paths):
        self.plugins = {}

        # Load plugin modules
        for path in plugin_paths:
            plugin_name = basename(path).replace('.py', '')

            logger.debug('Loading plugin: ' + path)

            module = import_module(plugin_name)
            plugin_class = getattr(module, 'Plugin')
            plugin_instance = plugin_class()

            self.plugins[plugin_name] = plugin_instance


    def import_module_from_source(self, fname, modname):
        '''
        Import a Python source file and return the loaded module
        '''

        spec = importlib.util.spec_from_file_location(modname, fname)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        modules[modname] = mod

        return mod.Plugin()

