from os.path import basename, getmtime, join, isfile, isdir, sep, abspath, dirname
from os import walk, listdir
from constants import CONTENT_DIR, BUILD_DIR, ASSET_DIR, CACHE_DIR, THEME_DIR, THEME_TEMPLATE_DIR, PLUGIN_DIR
from Common import Common
from Page import Page
from pickle import load, dump
from DepGraph import DepGraph
from TemplateDeps import TemplateDeps
from sys import path as syspath, modules
from importlib import import_module


PLUGINS_CACHE_FILE = 'plugins'


class Site(Common):
    '''
    Generate site

    Key concepts:
    content_dir - directory containing site *ahem* content, the Markdown files etc
    build_dir - generated site goes here, e.g. html etc
    '''

    def __init__(self, site_dir=None, settings={}, env={}):
        self.site_dir = site_dir

        self.settings = settings
        self.env = env
        self.content_dir = join(self.site_dir, CONTENT_DIR)
        self.build_dir = join(self.site_dir, BUILD_DIR)
        self.asset_dir = join(self.content_dir, ASSET_DIR)
        self.cache_dir = join(self.site_dir, CACHE_DIR, self.__class__.__name__)
        self.theme_dir = join(self.get_theme_dir())
        self.theme_template_dir = join(self.theme_dir, THEME_TEMPLATE_DIR)
        self.site_plugin_dir = join(self.site_dir, PLUGIN_DIR)
        self.pgn_plugin_dir = join(dirname(abspath(__file__)), PLUGIN_DIR)

        self.log_info(f'site_dir: {self.site_dir}')
        self.log_info(f'content_dir: {self.content_dir}')
        self.log_info(f'build_dir: {self.build_dir}')

        self.load_plugin_hooks()

        self.exec_hooks('pre_build')

        self.content_dir_list = self.get_file_list(self.content_dir)

        self.build_dir_list = self.get_file_list(self.build_dir)

        self.prune_build_dir()

        self.set_build_lists()

        self.add_broken_page_deps_to_build_list()

        self.build_site()

        # Write caches
        self.dep_graph.save()
        self.write_cache(PLUGINS_CACHE_FILE, self.hooks)

        self.exec_hooks('post_build')


    def write_cache(self, filename, obj):
        self.make_dir(self.cache_dir)
        path = join(self.cache_dir, filename)

        self.log_info('Writing cache: ' + path)

        with open(path, 'wb') as f:
            dump(obj, f)


    def exec_hooks(self, hook_name):
        '''
        Run plugin hooks
        '''

        self.log_info('Executing hooks: ' + hook_name)

        for h in self.hooks[hook_name]:
            h()


    def load_plugin_hooks(self):
        '''
        Load plugins from cache if exists, only load plugins that are defined in .pgn_env
        '''
        plugins_cache = join(self.cache_dir, PLUGINS_CACHE_FILE)

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
            if getmtime(plugins_cache) >= last_plugins_change:
                self.log_info('Loading plugins from cache')

                with open(plugins_cache, 'rb') as f:
                    self.hooks = load(f)
            else:
                self.log_info('Plugin cache stale: Initalizing plugins')
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


    def add_broken_page_deps_to_build_list(self):
        '''
        Pages may have dependencies, add page to build list dependency not satisfied and page needs building
        '''

        self.log_info('Analyzing dependencies')
        self.dep_graph = DepGraph(join(self.cache_dir, 'dep_graph'))

        if self.dep_graph.deps == {}:
            self.log_warning('Dependency graph cache is empty')

        self.exec_hooks('page_dep_check')

        # A page depends on one template, so add that, and also all dependencies that that template has
        # Check that any pages that depend on templates are newer than the templates
        for content_path, depends_on_paths in self.dep_graph.deps.items():
            relative_path = content_path[len(self.content_dir):].lstrip(sep)
            build_path = join(self.build_dir, relative_path)
            for dep_path in depends_on_paths:
                if getmtime(build_path) < getmtime(dep_path): # Yes, build path!
                    self.log_info(dep_path +' is newer than dependency ' + build_path)

                    self.pages_build_list[content_path] = build_path


    def get_theme_dir(self):
        return join(self.site_dir, 'themes', self.env['site']['theme'])


    def build_site(self):
        '''
        Build according to build_list
        '''

        self.log_info(f'Building content {self.build_dir}')

        # Create directories
        for target_path in self.directories_build_list:
            self.make_dir(target_path)

        template_deps = TemplateDeps(self.theme_template_dir)

        # Generate pages
        for src, tgt in self.pages_build_list.items():

            self.exec_hooks('pre_page_build')

            p = Page(src, tgt, settings=self.settings)

            template_path = join(self.theme_template_dir, p.headers['template'] + '.mako')
            td = template_deps.deps[template_path]
            # Add header template too
            td.insert(0, template_path)

            # Add page dependencies
            self.dep_graph.add(p.source_path, td)

            self.exec_hooks('post_page_build')

            p.write()

        # Copy assets
        for src, tgt in self.assets_build_list.items():
            self.copy_path(src, tgt)


    def path_relative_to(self, path, relative_to):
        return path[len(relative_to):]


    def set_build_lists(self):
        '''
        Populates various lists of content that needs to be built
        '''

        # page and asset list is used many places and best use dict so duplicate values are not added
        self.pages_build_list = {}
        self.assets_build_list = {}
        self.directories_build_list = []

        self.log_info(f'Making build lists {self.build_dir}')

        self.exec_hooks('pre_build_lists')

        # content_dir
        for content_path in self.content_dir_list:

            relative_path = self.path_relative_to(content_path, self.content_dir)
            build_path = f'{self.build_dir}{relative_path}'

            path_type = False

            # Set path type
            if isfile(content_path):
                if content_path.startswith(self.asset_dir):
                    path_type = 'asset'
                else:
                    path_type = 'page'
            else:
                path_type = 'dir'


            if path_type == 'dir':
                if not isdir(build_path):
                    self.log_info(f'Adding to directories_build_list: {content_path}')
                    self.directories_build_list.append(build_path)

            else:

                if not isfile(build_path) or getmtime(content_path) > getmtime(build_path):

                    if path_type == 'asset':
                        self.log_info(f'Adding to assets_build_list: {content_path}')
                        self.assets_build_list[content_path] = build_path
                    elif path_type == 'page':
                        self.log_info(f'Adding to page_build_list: {content_path}')
                        self.pages_build_list[content_path] = build_path

        self.exec_hooks('post_build_lists')


    def prune_build_dir(self):
        '''
        Remove all directories and files from build_dir that do not exist in content_dir
        '''

        self.log_info(f'Pruning {self.build_dir}')

        # When compare paths we need to disgard the prefix
        len_build_dir = len(self.build_dir)
        len_content_dir = len(self.content_dir)

        for build_path in self.build_dir_list:
            # Delete all files that only exist in build_dir, but not in content_dir

            relative_build_path = build_path[len_build_dir:]

            delete_path = True

            for content_path in self.content_dir_list:
                relative_content_path = content_path[len_content_dir:]

                if relative_build_path == relative_content_path:
                    delete_path = False
                    break

            if delete_path:
                self.delete_path(build_path)


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
        #modules["module.name"] = mod
        spec.loader.exec_module(mod)
        modules[modname] = mod

        return mod.Plugin()

