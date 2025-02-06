from os.path import basename, getmtime, join, isfile, isdir, sep, abspath, dirname, exists
from os import walk, listdir, environ
from pagegen.constants import CONTENT_DIR, BUILD_DIR, ASSET_DIR, CACHE_DIR, THEME_DIR, THEME_TEMPLATE_DIR, PLUGIN_DIR, SITE_CONF, HOOK_PRE_BUILD, HOOK_PRE_BUILD_LISTS, HOOK_POST_BUILD_LISTS, HOOK_PAGE_DEPS, HOOK_PAGE_PRE_BUILD, HOOK_PAGE_RENDER, HOOK_PAGE_POST_BUILD, HOOK_POST_BUILD, THEME_ASSET_SOURCE_DIR, THEME_ASSET_TARGET_DIR, PGN_LIVE_RELOAD
from pagegen.Common import Common
from pagegen.Page import Page
from pickle import load, dump
from pagegen.DepGraph import DepGraph
from sys import path as syspath, modules
from importlib import import_module
from pagegen.Plugins import Plugins
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Site(Common):
    '''
    Generate site

    Key concepts:
    content_dir - directory containing site *ahem* content, the Markdown files etc
    build_dir - generated site goes here, e.g. html etc
    '''

    def __init__(self, site_dir=None, site_conf=None):
        self.site_dir = site_dir
        self.conf = site_conf
        self.cache = {} # Convinience for use by plugins, convention to save stuff as self.cache[plugin name][key][value]

        self.content_dir = join(self.site_dir, CONTENT_DIR)
        self.build_dir = join(self.site_dir, BUILD_DIR)
        self.asset_source_dir = join(self.site_dir, ASSET_DIR)
        self.asset_target_dir = join(self.build_dir, ASSET_DIR)
        self.cache_dir = join(self.site_dir, CACHE_DIR, self.__class__.__name__)
        self.plugin_dir = join(self.site_dir, PLUGIN_DIR)

        try:
            self.base_url = self.conf['site']['base_url']
        except KeyError:
            logger.error('Unable to get mandatory base_url setting from site section. Ensure it is defined')
            raise

        self.theme_dir = join(self.site_dir, 'themes', self.conf['site']['theme'])
        self.theme_asset_source_dir = join(self.theme_dir, THEME_ASSET_SOURCE_DIR)
        self.theme_asset_target_dir = join(self.build_dir, THEME_ASSET_TARGET_DIR)

        self.index_cache_file_name = 'index'
        self.index_cache_path = join(self.cache_dir, self.index_cache_file_name)

        logger.info(f'site_dir: {self.site_dir}')
        logger.info(f'content_dir: {self.content_dir}')
        logger.info(f'build_dir: {self.build_dir}')


    def build_site(self):

        plugin_module = Plugins(
            self.plugin_dir, # Site plugins dir
            join(dirname(abspath(__file__)), PLUGIN_DIR), # pagegen plugins dir
            join(self.site_dir, CACHE_DIR), # Cache dir
            self.site_dir,
            conf=self.conf
        )
        self.plugins = plugin_module.plugins

        self.load_index()

        self.exec_hooks(HOOK_PRE_BUILD, {'site': self})

        self.sync_asset_dirs()

        self.content_dir_list = self.get_file_list(self.content_dir)

        self.prune_index()

        self.exec_hooks(HOOK_PRE_BUILD_LISTS, {'site': self})

        self.build_dir_list = self.get_file_list(self.build_dir)

        self.prune_build_dir()

        self.set_build_lists()

        self.exec_hooks(HOOK_POST_BUILD_LISTS, {'site': self})

        self.add_broken_page_deps_to_build_list()

        self.exec_hooks(HOOK_PAGE_DEPS, {'site': self})

        self.build_pages()

        # Sanity check that index and content list are equal
        #print(self._index.keys())
        #print(self.content_dir_list)
        #if list(self._index.keys()) != self.content_dir_list:
        #    raise Exception('Index does not match content list, maybe clear cache and try again?')

        self.exec_hooks(HOOK_POST_BUILD, {'site': self, 'index': self._index})

        self.dep_graph.write_cache()
        self.pickle_object(self.cache_dir, self.index_cache_file_name, self._index)


    def prune_index(self):
        '''
        The index must contain same items as content list, remove any from index that no longer exist
        '''

        for p_path, data in self._index.copy().items():
            delete_path = False

            if not p_path in self.content_dir_list:
                delete_path = True

            if delete_path:
                logger.info(f'Deleting from index: {p_path}')
                del self._index[p_path]


    def load_index(self):
        '''
        Site index is meta data of all pages, it is only garuanteed to be complete AFTER all pages have been generated, and as such is only made available to plugins in the hooks after page generation
        '''

        try:
            logger.info('Loading index from cache')
            self._index = self.load_pickle(self.index_cache_path)
        except FileNotFoundError:
            logger.info('rss index cache not found')
            self._index = {}


    def sync_asset_dirs(self):
        '''
        Ensure assets dir in content dir is synced to assets dir in build. Same for theme asset dir.
        '''

        wrong_asset_dir = join(self.content_dir, ASSET_DIR)
        if exists(self.asset_source_dir) and exists(wrong_asset_dir):
            logger.warning(f'Asset path exists, it will not be copied to build directory: {wrong_asset_dir}')

        wrong_theme_asset_dir = join(self.content_dir, THEME_ASSET_TARGET_DIR)
        if exists(self.theme_asset_source_dir) and exists(wrong_theme_asset_dir):
            logger.warning(f'Asset path exists, it will not be copied to build directory: {wrong_theme_asset_dir}')

        for sync_dirs in [
            (self.asset_source_dir, self.asset_target_dir),
            (self.theme_asset_source_dir, self.theme_asset_target_dir)
        ]:
            self.dir_sync(sync_dirs[0], sync_dirs[1])


    def exec_hooks(self, hook_name, objects):
        '''
        Run plugin hooks
        '''

        logger.info('Executing hooks: ' + hook_name)

        # If hook queue specified in site conf then execute according to it
        if hook_name in self.conf['site'].keys():
            for plugin_name in self.conf['site'][hook_name].split(','):
                plugin_name = plugin_name.strip()
                if plugin_name in self.plugins.keys():
                    if hasattr(self.plugins[plugin_name], hook_name):
                        logger.info(f'{plugin_name}: Executing hook: {hook_name}')
                        getattr(self.plugins[plugin_name], hook_name)(objects)
                else:
                    logger.warning(f'Config setting site[{hook_name}] references {plugin_name}, but this plugin is not enabled, add it to site[enabled_plugins]?')

        # If no queue/sequence specified then execute all plugins in whatever order they where loaded
        else:
            for plugin_name, plugin_module in self.plugins.items():
                if hasattr(plugin_module, hook_name):
                    logger.info(f'{plugin_name}: Executing hook: {hook_name}')
                    getattr(plugin_module, hook_name)(objects)


    def add_broken_page_deps_to_build_list(self):
        '''
        Pages may have dependencies, add page to build list dependency not satisfied and page needs building
        '''

        logger.info('Analyzing dependencies')
        self.dep_graph = DepGraph(self.cache_dir, 'dep_graph')

        # Add path to build list whene source is newer than its dependancies
        for content_path, depends_on_paths in self.dep_graph.deps.items():
            relative_path = content_path[len(self.content_dir):].lstrip(sep)
            build_path = join(self.build_dir, relative_path)
            for dep_path in depends_on_paths:
                try:
                    if getmtime(build_path) < getmtime(dep_path): # Yes, build path!
                        logger.info(dep_path +' is newer than dependency ' + build_path)

                        self.pages_build_list[content_path] = build_path
                except NotADirectoryError:
                    # Probably the content path is a directory in the cache, but now it is a file
                    logger.error('Cache mismatch: ' + dep_path + ' : ' + build_path)
                    raise Exception
                except FileNotFoundError:
                    pass


    def build_pages(self):
        '''
        Build pages according to build_list
        '''

        logger.info(f'Building content {self.build_dir}')

        # Create directories
        for target_path in self.directories_build_list:
            self.make_dir(target_path)

        # If argument --serve(serve_mode) then add javascript script to each page that reloads page if site is regenerated
        if PGN_LIVE_RELOAD in environ.keys() and environ[PGN_LIVE_RELOAD] == 'yes':
            js_reload_poll_script = self.read_file(join(dirname(__file__), 'live-reload.js'))

        # Generate pages
        for src, tgt in self.pages_build_list.items():
            logger.info(f'Generating page: {src}')

            p = Page()

            self.exec_hooks(HOOK_PAGE_PRE_BUILD, {'site': self, 'page': p})

            p.load(tgt, self, source_path=src)

            self.exec_hooks(HOOK_PAGE_RENDER, {'site': self, 'page': p})

            # If argument --serve(serve_mode) then add javascript script to each page that reloads page if site is regenerated
            if PGN_LIVE_RELOAD in environ.keys() and environ[PGN_LIVE_RELOAD] == 'yes':
                p.out += '<script>' + js_reload_poll_script + '</script>'

            p.write()

            self.exec_hooks(HOOK_PAGE_POST_BUILD, {'site': self, 'page': p})

            self._index[p.source_path] = {
                'url': p.absolute_url,
                'headers': p.headers
            }


    def set_build_lists(self):
        '''
        Populates various lists of content that needs to be built
        '''

        # page list is used many places and best use dict so duplicate values are not added
        self.pages_build_list = {}
        self.directories_build_list = []

        logger.info(f'Making build lists {self.build_dir}')

        # content_dir
        for content_path in self.content_dir_list:

            relative_path =  content_path[len(self.content_dir):]
            build_path = f'{self.build_dir}{relative_path}'

            path_type = False

            # Ignore asset and theme directories
            if content_path.startswith(self.asset_source_dir) or content_path.startswith(self.theme_asset_source_dir):
                continue

            # Set path type
            if isfile(content_path):
                path_type = 'page'
            else:
                path_type = 'dir'


            if path_type == 'dir':
                if not isdir(build_path):
                    logger.info(f'Adding to directories_build_list: {content_path}')
                    self.directories_build_list.append(build_path)

            else:

                if not isfile(build_path) or getmtime(content_path) > getmtime(build_path):

                    if path_type == 'page':
                        logger.info(f'Adding to page_build_list: {content_path}')
                        self.pages_build_list[content_path] = build_path


    def prune_build_dir(self):
        '''
        Remove all directories and files from build_dir that do not exist in content_dir
        '''

        logger.info(f'Pruning {self.build_dir}')

        # When compare paths we need to disgard the prefix
        len_build_dir = len(self.build_dir)
        len_content_dir = len(self.content_dir)

        for build_path in self.build_dir_list:

            # Ignore asset and theme directories
            if build_path.startswith(self.asset_target_dir) or build_path.startswith(self.theme_asset_target_dir):
                continue

            relative_build_path = build_path[len_build_dir:]

            delete_path = True

            # Delete all files that only exist in build_dir, but not in content_dir
            for content_path in self.content_dir_list:
                relative_content_path = content_path[len_content_dir:]

                if relative_build_path == relative_content_path:
                    # Check the content and build paths are still of same type, if not the build path gotta go
                    cp_type = 'f' if isfile(content_path) else 'd'
                    bp_type = 'f' if isfile(build_path) else 'd'

                    if cp_type == bp_type:
                        delete_path = False
                        break

            if delete_path:
                self.delete_path(build_path)

