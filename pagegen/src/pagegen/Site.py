from os import walk, listdir 
from os.path import basename, getmtime, join, isfile, isdir
from constants import CONTENT_DIR, BUILD_DIR, ASSET_DIR
from Common import Common


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
        self.content_dir = self.site_dir / CONTENT_DIR
        self.build_dir = self.site_dir / BUILD_DIR
        self.asset_dir = self.content_dir / ASSET_DIR

        self.content_dir_list = self.get_file_list(self.content_dir)

        print('TODO refactor build list so there are less checks, maybe need lists for assets, list for dirs and list for pages, instead of all in one?')
        print('TODO build lists should have both source and target paths set, so dont have to compute again')

        self.build_dir_list = self.get_file_list(self.build_dir)

        self.prune_build_dir()

        self.build_list = self.get_build_list()

        self.build_site()


    def build_site(self):
        '''
        Build according to build_list
        '''

        self.log_info(f'Building content {self.build_dir}')

        # First create directories
        for p in self.build_list:
            if isdir(p):
                self.log_info(f'Create directory: {p} in build')

        # Now copy/generate files
        for p in self.build_list:
            if p.startswith(str(self.asset_dir)):
                if not isdir(p):
                    self.log_info(f'Copy: {p} to build')
                #self.copy_path(p, 'build')
            elif isfile(p):
                self.log_info(f'Generate: {p} to build')


    def path_relative_to(self, path, relative_to):
        return path[len(str(relative_to)):]


    def get_build_list(self):
        '''
        Return list of content that is newer than it's target in build_dir
        Assumes build_dir has been cleared of files not in content_dir
        '''

        self.log_info(f'Making build list {self.build_dir}')
        bl = []

        for content_path in self.content_dir_list:

            relative_path = self.path_relative_to(content_path, self.content_dir)
            build_path = f'{self.build_dir}{relative_path}'

            add_build_list = False

            if isfile(build_path):
                if getmtime(content_path) > getmtime(build_path):
                    add_build_list = True
            else:
                add_build_list = True

            if add_build_list:
                self.log_info(f'Adding to build_list: {content_path}')
                bl.append(content_path)

        return bl



    def get_file_list(self, path):
        '''
        Return list of all files and directories
        '''

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
        len_build_dir = len(str(self.build_dir))
        len_content_dir = len(str(self.content_dir))

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


