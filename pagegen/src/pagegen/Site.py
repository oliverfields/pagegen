from os import walk
from os.path import basename, getmtime
from constants import CONTENT_DIR, BUILD_DIR
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
        self.content_dir = site_dir / CONTENT_DIR
        self.build_dir = site_dir / BUILD_DIR

        self.get_content_list()
        self.prune_build_dir()


    def get_content_list(self):
        '''
        Find and add all files in content_dir to list
        '''

        self.content_list = {}

        for root, dirs, files in walk(self.content_dir):
            for file in files:
                path = f'{root}/{file}'
                self.content_list[path] = {
                    'modified': getmtime(path)
                }


    def prune_build_dir(self):
        '''
        Remove all files and directories from build_dir that do not exist in content_dir
        '''

        for f in self.content_list:
            print(f)

        for root, dirs, files in walk(self.build_dir):
            for file in files:
                build_path = f'{root}/{file}'
                if not build_path in self.content_list.keys():
                    self.delete_path(build_path)


