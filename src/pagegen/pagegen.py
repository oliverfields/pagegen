import argparse
from functools import partial
from http.server import HTTPServer
from sys import exit, stdout
from os import system, open, O_CREAT, O_EXCL, remove, environ, getcwd, listdir
from os.path import join, isfile, dirname, abspath
from traceback import print_exception
from pagegen.PgnHandler import PgnHandler
from pagegen.constants import SITE_CONF, LOCK_FILE, CACHE_DIR, BUILD_DIR, PAGEGEN_VERSION, ASSET_DIR, THEME_DIR
from pagegen.Site import Site
from pathlib import Path
from pagegen.Config import Config
from shutil import rmtree
from pagegen.Common import Common
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen')


def init_pgn_dir():
    '''
    Copy skeleton directory to current directory for basic setup
    '''

    skel_dir = dirname(abspath(__file__)) + '/skel'
    root_dir=getcwd()

    if listdir(root_dir):
        logger.error("Cannot init non empty directory '%s'" % root_dir)
        exit(1)

    try:
        c = Common()
        c.dir_sync(skel_dir, root_dir)
    except:
        logger.error("Unable to copy '%s' to '%s'" % (skel_dir, root_dir))
        exit(1)


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


def main():
    site_dir = find_site_dir()

    system('') # Enable ansi escape codes

    p = argparse.ArgumentParser()

    p.add_argument('-g', '--generate', action='store_true', help='Generate site')
    p.add_argument('-V', '--verbosity', action='store', help='Increase verbosity, levels are DEBUG, INFO, WARNING, ERROR or CRITICAL')
    p.add_argument('-i', '--ignore-lock', action='store_true', help='Ignore lock file')
    p.add_argument('-n', '--init', action='store_true', help='Initiate current directory as pagegen site')
    p.add_argument('-c', '--clear-cache', action='store_true', help='Clear caches before building')
    p.add_argument('-s', '--serve', action='store_true', help='Serve site on localhost')
    p.add_argument('-v', '--version', action='store_true', help='Show version')
    a = p.parse_args()

    if a.version:
        print(PAGEGEN_VERSION)
        exit(0)

    if a.verbosity == None or a.verbosity == 'WARNING':
        logger.setLevel(logging.WARNING)
    elif a.verbosity == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif a.verbosity == 'INFO':
        logger.setLevel(logging.INFO)
    elif a.verbosity == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif a.verbosity == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
    else:
        logger.critical('Unknown verbosity level ' + a.verbosity + ': Must be DEBUG, INFO, WARNING, ERROR or CRITICAL')
        exit(1)

    if a.init:
        init_pgn_dir()
        exit(0)

    if site_dir is None:
        logger.critical(f'Unable to find {SITE_CONF}')
        exit(1)

    lock_file = join(site_dir, LOCK_FILE)

    try:

        if a.clear_cache:
            cache_dir = join(site_dir, CACHE_DIR)
            build_dir = join(site_dir, BUILD_DIR)

            try:
                rmtree(cache_dir)
                logger.info(f'Deleting {cache_dir}')
            except FileNotFoundError:
                pass

            try:
                rmtree(build_dir)
                logger.info(f'Deleting {build_dir}')
            except FileNotFoundError:
                pass

        site_conf_file = join(site_dir, SITE_CONF)

        c = Config(site_conf_file)

        try:
            # Only set debug level if 
            if a.verbosity == None:
                log_level = c.configparser['site']['log_level']

                if log_level == 'DEBUG':
                    logger.setLevel(logging.DEBUG)
                elif log_level == 'INFO':
                    logger.setLevel(logging.INFO)
                elif log_level == 'WARNING':
                    logger.setLevel(logging.WARNING)
                elif log_level == 'ERROR':
                    logger.setLevel(logging.ERROR)
                elif log_level == 'CRITICAL':
                    logger.setLevel(logging.CRITICAL)
        except KeyError:
            pass


        if a.generate:

            if isfile(lock_file):
                if a.ignore_lock:
                    remove(lock_file)
                else:
                    logger.warning(f'Lock file found: {lock_file}')

                    if stdout.isatty() and input('Delete lock file and continue? [N|y] ') == 'y':

                        remove(lock_file)
                    else:
                        exit()
            else:
                open(lock_file, O_CREAT | O_EXCL)

            s = Site(site_dir=site_dir, site_conf=c.configparser)
            s.build_site()


        if a.serve:
            try:
                site_base_url = c.configparser['site']['base_url']
                theme_name = c.configparser['site']['theme']
            except KeyError as e:
                logger.critical(f'Missing mandatory setting: {e.args[0]}')
                raise

            try:
                serve_ip = c.configparser['site']['serve_ip']
            except:
                serve_ip = '127.0.0.1'

            try:
                serve_port = c.configparser['site']['serve_port']
            except:
                serve_port = 8000

            try:
                directory_index = c.configparser['site']['directory_index']
            except:
                directory_index = 'index.html'

            serve_base_url = f'http://localhost:{serve_port}'

            serve_routes = [
                (f'/assets/', join(site_dir, ASSET_DIR)),
                (f'/theme/', join(site_dir, THEME_DIR, theme_name, ASSET_DIR))
            ]

            serve_dir = join(site_dir, BUILD_DIR)

            handler = partial(PgnHandler, serve_dir, site_base_url, serve_base_url, serve_routes, directory_index)

            print(f'Serving {serve_dir} on {serve_base_url}')

            httpd = HTTPServer((serve_ip, serve_port), handler)
            httpd.serve_forever()


        # Tidy lock file
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
        logger.warning('Cache could be inconsistent, recommend clearing it')
        logger.critical('An unhandeld exception occoured, quitting..')

        #if a.verbose:
        print_exception(type(e), e, e.__traceback__)

        exit(1)


if __name__ == '__main__':
    main()
