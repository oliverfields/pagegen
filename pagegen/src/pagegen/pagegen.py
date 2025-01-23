import argparse
from sys import exit, stdout
from os import system, open, O_CREAT, O_EXCL, remove, environ
from os.path import join, isfile
from traceback import print_exception
from constants import SITE_CONF, LOCK_FILE, CACHE_DIR, BUILD_DIR, DRYRUNMSG
from Site import Site
from pathlib import Path
from Config import Config
from shutil import rmtree
import logger_setup
import logging

logger = logging.getLogger('pagegen')

def find_site_dir(path=False):
    '''
    Returns path to site env if found in current directory or one of its parents
    '''

    if not path:
        path = Path.cwd()

    possible_site_env = path / SITE_CONF

    if possible_site_env.is_file():
        return str(possible_site_env.parent)
    elif path != path.parent:
        return find_site_dir(path.parent)


if __name__ == '__main__':

    site_dir = find_site_dir()

    if site_dir is None:
        logger.error(f'Unable to find {SITE_CONF}')
        exit(1)

    try:
        lock_file = join(site_dir, LOCK_FILE)

        system('') # Enable ansi escape codes

        p = argparse.ArgumentParser()

        p.add_argument('-g', '--generate', action='store_true', help='Generate site')
        p.add_argument('-V', '--verbose', action='store_true', help='Increase verbosity')
        p.add_argument('-d', '--dry-run', action='store_true', help='Do not write to disk')
        p.add_argument('-i', '--ignore-lock', action='store_true', help='Ignore lock file')
        p.add_argument('-c', '--clear-cache', action='store_true', help='Clear caches before building')
        a = p.parse_args()


        if a.verbose:
            logger.setLevel(logging.INFO)

        if a.dry_run:
            environ['PGN_DRY_RUN'] = 'yes'

        if a.clear_cache:
            cache_dir = join(site_dir, CACHE_DIR)
            build_dir = join(site_dir, BUILD_DIR)
            if a.dry_run:
                logger.info(f'{DRYRUNMSG}: Would delete {cache_dir}')
                logger.info(f'{DRYRUNMSG}: Would delete {build_dir}')
            else:
                try:
                    rmtree(cache_dir)
                    logger.warning(f'Deleting {cache_dir}')
                except FileNotFoundError:
                    pass

                try:
                    rmtree(build_dir)
                    logger.warning(f'Deleting {build_dir}')
                except FileNotFoundError:
                    pass

        if a.generate:

            if isfile(lock_file):
                logger.warning(f'Lock file found: {lock_file}')

                if a.ignore_lock == False and stdout.isatty() and input('Delete lock file and continue? [N|y] ') == 'y':

                    remove(lock_file)
                else:
                    exit()
            else:
                open(lock_file, O_CREAT | O_EXCL)

            c = Config(join(site_dir, SITE_CONF))

            s = Site(site_dir=site_dir, site_conf=c.configparser)

        try:
            remove(lock_file)
        except FileNotFoundError:
            pass

    except KeyboardInterrupt:
        if isfile(lock_file):
            remove(lock_file)
        print('')
        exit(1)
    except Exception as e:
        print('cache could be inconsistent, delete it?')
        logger.error('Unknown failure')
        print_exception(type(e), e, e.__traceback__)
        exit(1)
