from constants import CONTENT_DIR, BUILD_DIR, ESCAPECODES, DRYRUNMSG
from sys import stderr, stdout
from os.path import isdir, isfile, join
from os import system, remove, makedirs, walk, environ
from shutil import copyfile, rmtree
from pickle import dump, load
import logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

DRY_RUN = environ.get('PGN_DRY_RUN', False)

class Common:
    '''
    Base class that contains common functionality
    '''

    def delete_path(self, path):
        '''
        Delete a file, while honoring settings
        '''

        if DRY_RUN:
            logger.notice(f'{DRYRUNMSG}: Would delete: {path}')
        else:
            logger.info(f'Deleting {path}')

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

        if DRY_RUN:
            logger.notice(f'{DRYRUNMSG}: Would copy: {source} to {target}')
        else:
            logger.info(f'Copying {source} to {target}')

            try:
                copyfile(source, target)
            except Exception as e:
                log_error(f'Unable to copy {source} to {target}): {str(e)}')
                raise


    def write_file(self, file_path, content):
        '''
        Write contents to given file path
        '''

        if DRY_RUN:
            logger.notice(f'{DRYRUNMSG}: Would write: {file_path}')
        else:
            logger.info(f'Writing {file_path}')

            try:
                with open(file_path, 'w') as f:
                    f.write(content)
            except Exception as e:
                logger.error(f'Unable to write file: {file_path}): {str(e)}')
                raise


    def make_dir(self, dir_path):
        '''
        Make directory
        '''
        if not isdir(dir_path):
            if DRY_RUN:
                logger.notice(f'{DRYRUNMSG}: Would make {dir_path}')
            else:
                logger.info(f'Making {dir_path}')

                try:
                    makedirs(dir_path)
                except Exception as e:
                    logger.error(f'Unable to create directory {dir_path}): {str(e)}')
                    raise


    def get_file_list(self, path):
        '''
        Return list of all files and directories
        '''
        logger.info(f'Get files in {path}')

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

        if DRY_RUN:
            logger.notice(f'{DRYRUNMSG}: Would create cache: {path}')
        else:
            logger.info(f'Writing cache {path}')
            with open(path, 'wb') as f:
                dump(obj, f)


    def load_pickle(self, path):
        with open(path, 'rb') as f:
            obj = load(f)

        return obj
