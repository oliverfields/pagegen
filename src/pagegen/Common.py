from pagegen.constants import CONTENT_DIR, BUILD_DIR, ESCAPECODES
from sys import stderr, stdout
from os.path import isdir, isfile, join, getmtime, relpath, exists
from os import system, remove, makedirs, walk, environ
from shutil import copyfile, rmtree
import codecs
from pickle import dump, load
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Common:
    '''
    Base class that contains common functionality
    '''

    def read_file(self, path):
        try:
            with codecs.open (path, "r", 'utf-8') as f:
                return f.read()
        except Exception as e:
            raise e


    def delete_path(self, path):
        '''
        Delete a file, while honoring settings
        '''

        logger.debug(f'Deleting {path}')

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

        logger.debug(f'Copying {source} to {target}')

        try:
            copyfile(source, target)
        except Exception as e:
            logger.critical(f'Unable to copy {source} to {target}): {str(e)}')
            raise


    def write_file(self, file_path, content):
        '''
        Write contents to given file path
        '''

        logger.debug(f'Writing {file_path}')

        try:
            with open(file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            logger.debug(f'Unable to write file: {file_path}): {str(e)}')
            raise


    def make_dir(self, dir_path):
        '''
        Make directory
        '''
        if not isdir(dir_path):
            logger.debug(f'Making {dir_path}')

            try:
                makedirs(dir_path)
            except Exception as e:
                logger.critical(f'Unable to create directory {dir_path}): {str(e)}')
                raise


    def get_file_list(self, path):
        '''
        Return list of all files
        '''
        logger.debug(f'Get files in {path}')

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

        logger.debug(f'Writing cache {path}')
        with open(path, 'wb') as f:
            dump(obj, f)


    def load_pickle(self, path):
        with open(path, 'rb') as f:
            obj = load(f)

        return obj


    def is_newer_than(self, file_path, dir_path):
        '''
        Check if a file mtmie is newer than the files in a specific directory
        '''

        file_path_mtime = getmtime(file_path)

        for subdir, dirs, files in walk(dir_path):
            for file in files:
                f = join(subdir, file)
                f_mtime = getmtime(f)

                if file_path_mtime < f_mtime:
                    return False

        return True


    def dir_sync(self, src_dir, tgt_dir):
        '''
        Sync from src to tgt

        Thanks! https://developer-service.blog/synchronizing-files-between-two-directories-using-python/
        '''

        logger.debug(f'Syncing {src_dir} -> {tgt_dir}')

        if not isdir(src_dir):
            return False

        if not isdir(tgt_dir):
            makedirs(tgt_dir)

        files_to_sync = []
        for root, dirs, files in walk(src_dir):
            for directory in dirs:
                files_to_sync.append(join(root, directory))
            for file in files:
                files_to_sync.append(join(root, file))

        # Iterate over each file in the source directory
        for source_path in files_to_sync:
            # Get the corresponding path in the replica directory
            replica_path = join(tgt_dir, relpath(source_path, src_dir))

            # Check if path is a directory and create it in the replica directory if it does not exist
            if isdir(source_path):
                if not exists(replica_path):
                    logger.debug(f"Creating directory {replica_path}")
                    makedirs(replica_path)
            # Copy all files from the source directory to the replica directory
            else:
                # Check if the file exists in the replica directory and if it is different from the source file
                if not exists(replica_path) or getmtime(source_path) > getmtime(replica_path):
                    logger.debug(f"Copying {source_path} to {replica_path}")

                    # Copy the file from the source directory to the replica directory
                    copyfile(source_path, replica_path)

