from os import walk, listdir
from os.path import basename, getmtime, join, isfile, isdir
from constants import CONTENT_DIR, BUILD_DIR, ASSET_DIR
from Common import Common
from Page import Page


class Site(Common):
    '''
    Generate site

    Key concepts:
    content_dir - directory containing site *ahem* content, the Markdown files etc
    build_dir - generated site goes here, e.g. html etc
    '''

    def __init__(self, site_dir=None, settings={}):
        self.site_dir = site_dir

        self.settings = settings
        self.content_dir = join(self.site_dir, CONTENT_DIR)
        self.build_dir = join(self.site_dir, BUILD_DIR)
        self.asset_dir = join(self.content_dir, ASSET_DIR)

        self.log_info(f'site_dir: {self.site_dir}')
        self.log_info(f'content_dir: {self.content_dir}')
        self.log_info(f'build_dir: {self.build_dir}')

        self.content_dir_list = self.get_file_list(self.content_dir)

        self.build_dir_list = self.get_file_list(self.build_dir)

        self.prune_build_dir()

        self.set_build_lists()

        self.build_site()


    def build_site(self):
        '''
        Build according to build_list
        '''

        self.log_info(f'Building content {self.build_dir}')

        # Create directories
        for target_path in self.directories_build_list:
            self.make_dir(target_path)

        # Generate pages
        for src_tgt_paths in self.pages_build_list:
            p = Page(src_tgt_paths[0], settings=self.settings)
            p.write(src_tgt_paths[1])

        # Copy assets
        for src_tgt_paths in self.assets_build_list:
            self.copy_path(src_tgt_paths[0], src_tgt_paths[1])


    def path_relative_to(self, path, relative_to):
        return path[len(relative_to):]


    def set_build_lists(self):
        '''
        Populates various lists of content that needs to be built
        '''

        self.pages_build_list = []
        self.assets_build_list = []
        self.directories_build_list = []

        self.log_info(f'Making build lists {self.build_dir}')

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
                        self.assets_build_list.append((content_path, build_path))
                    elif path_type == 'page':
                        self.log_info(f'Adding to page_build_list: {content_path}')
                        self.pages_build_list.append((content_path, build_path))


    def get_file_list(self, path):
        '''
        Return list of all files and directories
        '''
        self.log_info(f'Get files in {path}')

        l = []

        for root, dirs, files in walk(path):

            for d in dirs:
                path = join(root, d)
                l.append(path)

            for f in files:
                path = join(root, f)
                l.append(path)

        return l


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


