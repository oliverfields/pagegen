from constants import CONTENT_DIR, BUILD_DIR, ESCAPECODES
from sys import stderr, stdout
from os import system, remove


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
            self.log_notice(f'DRY RUN: Would delete: {path}')
        else:
            if self.settings['verbose']:
                self.log_info(f'Delete: {path}')

            try:
                pass
                #remove(path)
            except Exception as e:
                log_error(f'Unable to delete {path}): {str(e)}')
                raise


    def copy_path(self, source, target):
        '''
        Copy a file or directory, while honoring settings
        '''

        if self.settings['dry_run']:
            self.log_notice(f'DRY RUN: Would copy: {source} to {target}')
        else:
            if self.settings['verbose']:
                self.log_info(f'Copy: {source} to {target}')

            try:
                pass
                #remove(path)
            except Exception as e:
                log_error(f'Unable to copy {source} to {target}): {str(e)}')
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

