from os.path import basename, getmtime, join, isfile, isdir, sep, abspath, dirname
from os import walk, listdir, environ
from constants import CONTENT_DIR, BUILD_DIR, ASSET_DIR, CACHE_DIR, THEME_DIR, THEME_TEMPLATE_DIR, PLUGIN_DIR, SITE_CONF
from Common import Common
from Page import Page
from pickle import load, dump
from DepGraph import DepGraph
from TemplateDeps import TemplateDeps
from sys import path as syspath, modules
from importlib import import_module
from Plugins import Plugins
import logger_setup
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

        logger.info('Site logger working')

        self.site_dir = site_dir
        self.conf = site_conf

        self.content_dir = join(self.site_dir, CONTENT_DIR)
        self.build_dir = join(self.site_dir, BUILD_DIR)
        self.asset_dir = join(self.content_dir, ASSET_DIR)
        self.cache_dir = join(self.site_dir, CACHE_DIR, self.__class__.__name__)
        self.theme_dir = join(self.get_theme_dir())
        self.theme_template_dir = join(self.theme_dir, THEME_TEMPLATE_DIR)

        logger.info(f'site_dir: {self.site_dir}')
        logger.info(f'content_dir: {self.content_dir}')
        logger.info(f'build_dir: {self.build_dir}')

        self.plugins = Plugins(
            join(self.site_dir, PLUGIN_DIR), # Site plugins dir
            join(dirname(abspath(__file__)), PLUGIN_DIR), # pagegen plugins dir
            join(self.site_dir, CACHE_DIR), # Cache dir
            conf=self.conf
        )

        self.plugins.load_plugin_hooks()

        self.exec_hooks('pre_build', site=self)

        self.content_dir_list = self.get_file_list(self.content_dir)

        self.build_dir_list = self.get_file_list(self.build_dir)

        self.prune_build_dir()

        self.set_build_lists()

        self.add_broken_page_deps_to_build_list()

        self.build_site()

        self.exec_hooks('post_build', site=self)

        # Write caches
        self.dep_graph.write_cache()
        self.plugins.write_cache()


    def exec_hooks(self, hook_name, site=False, page=False):
        '''
        Run plugin hooks
        '''

        logger.info('Executing hooks: ' + hook_name)

        for h in self.plugins.hooks[hook_name]:
            try:
                if site != False and page != False:
                    h(site, page)
                elif site != False:
                    h(site)
                else:
                    h()
            except TypeError as e:
                logger.error(f'Plugin hook {hook_name} failed: {h}')
                raise


    def add_broken_page_deps_to_build_list(self):
        '''
        Pages may have dependencies, add page to build list dependency not satisfied and page needs building
        '''

        logger.info('Analyzing dependencies')
        self.dep_graph = DepGraph(self.cache_dir, 'dep_graph')

        self.exec_hooks('page_dep_check', site=self)

        # A page depends on one template, so add that, and also all dependencies that that template has
        # Check that any pages that depend on templates are newer than the templates
        for content_path, depends_on_paths in self.dep_graph.deps.items():
            relative_path = content_path[len(self.content_dir):].lstrip(sep)
            build_path = join(self.build_dir, relative_path)
            for dep_path in depends_on_paths:
                if getmtime(build_path) < getmtime(dep_path): # Yes, build path!
                    logger.info(dep_path +' is newer than dependency ' + build_path)

                    self.pages_build_list[content_path] = build_path


    def get_theme_dir(self):
        return join(self.site_dir, 'themes', self.conf['site']['theme'])


    def build_site(self):
        '''
        Build according to build_list
        '''

        logger.info(f'Building content {self.build_dir}')

        # Create directories
        for target_path in self.directories_build_list:
            self.make_dir(target_path)

        template_deps = TemplateDeps(self.theme_template_dir)

        # Generate pages
        for src, tgt in self.pages_build_list.items():

            self.exec_hooks('page_pre_build', site=self)

            p = Page(src, tgt)

            self.exec_hooks('page_render_markup', site=self, page=p)

            self.exec_hooks('page_render_template', site=self, page=p)

            template_path = join(self.theme_template_dir, p.headers['template'] + '.mako')
            td = template_deps.deps[template_path]
            # Add header template too
            td.insert(0, template_path)

            # Add page dependencies
            self.dep_graph.add(p.source_path, td)

            self.exec_hooks('page_post_build', site=self, page=p)

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

        logger.info(f'Making build lists {self.build_dir}')

        self.exec_hooks('pre_build_lists', site=self)

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
                    logger.info(f'Adding to directories_build_list: {content_path}')
                    self.directories_build_list.append(build_path)

            else:

                if not isfile(build_path) or getmtime(content_path) > getmtime(build_path):

                    if path_type == 'asset':
                        logger.info(f'Adding to assets_build_list: {content_path}')
                        self.assets_build_list[content_path] = build_path
                    elif path_type == 'page':
                        logger.info(f'Adding to page_build_list: {content_path}')
                        self.pages_build_list[content_path] = build_path

        self.exec_hooks('post_build_lists', site=self)


    def prune_build_dir(self):
        '''
        Remove all directories and files from build_dir that do not exist in content_dir
        '''

        logger.info(f'Pruning {self.build_dir}')

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

