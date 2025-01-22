from constants import CONTENT_DIR, BUILD_DIR, ESCAPECODES
from sys import stderr, stdout
from os.path import isdir, isfile, join
from os import system, remove, makedirs, walk
from shutil import copyfile, rmtree
from pickle import dump


DRYRUNMSG = f'{ESCAPECODES["yellow"]}DRY RUN{ESCAPECODES["default"]}'


class Common:
    '''
    Base class that contains common functionality
    '''

    def __init__(self, settings={}):
        self.settings = settings


    def delete_path(self, path):
        '''
        Delete a file, while honoring settings
        '''

        if self.settings['dry_run']:
            self.log_notice(f'{DRYRUNMSG}: Would delete: {path}')
        else:
            if self.settings['verbose']:
                self.log_info(f'Deleting {path}')

            try:
                if isfile(path):
                    remove(path)
                elif isdir(path):
                    rmtree(path)
            except Exception as e:
                log_error(f'Unable to delete {path}): {str(e)}')
                raise


    def copy_path(self, source, target):
        '''
        Copy a file or directory, while honoring settings
        '''

        if self.settings['dry_run']:
            self.log_notice(f'{DRYRUNMSG}: Would copy: {source} to {target}')
        else:
            if self.settings['verbose']:
                self.log_info(f'Copying {source} to {target}')

            try:
                copyfile(source, target)
            except Exception as e:
                log_error(f'Unable to copy {source} to {target}): {str(e)}')
                raise


    def write_file(self, file_path, content):
        '''
        Write contents to given file path
        '''

        if self.settings['dry_run']:
            self.log_notice(f'{DRYRUNMSG}: Would write: {file_path}')
        else:
            if self.settings['verbose']:
                self.log_info(f'Writing {file_path}')

            try:
                with open(file_path, 'w') as f:
                    f.write(content)
            except Exception as e:
                self.log_error(f'Unable to write file: {file_path}): {str(e)}')
                raise


    def make_dir(self, dir_path):
        '''
        Make directory
        '''
        if not isdir(dir_path):
            if self.settings['dry_run']:
                self.log_notice(f'{DRYRUNMSG}: Would make {dir_path}')
            else:
                if self.settings['verbose']:
                    self.log_info(f'Making {dir_path}')

                try:
                    makedirs(dir_path)
                except Exception as e:
                    self.log_error(f'Unable to create directory {dir_path}): {str(e)}')
                    raise


    def log_error(self, message):
        stderr.write('%sERROR%s: %s\n' % (ESCAPECODES['red'], ESCAPECODES['default'], message))


    def log_warning(self, message):
        stderr.write('%sWARNING%s: %s\n' % (ESCAPECODES['yellow'], ESCAPECODES['default'], message))


    def log_notice(self, message):
        stdout.write('%sNOTICE%s: %s\n' % (ESCAPECODES['green'], ESCAPECODES['default'], message))


    def log_info(self, message):
        if self.settings['verbose']:
            stdout.write('%sINFO%s: %s\n' % (ESCAPECODES['blue'], ESCAPECODES['default'], message))


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


    def pickle_object(self, cache_dir, cache_file, obj):
        self.make_dir(cache_dir)
        path = join(cache_dir, cache_file)

        if self.settings['dry_run']:
            self.log_notice(f'{DRYRUNMSG}: Would create cache: {path}')
        else:
            if self.settings['verbose']:
                self.log_info(f'Writing cache {path}')
            with open(path, 'wb') as f:
                dump(obj, f)
