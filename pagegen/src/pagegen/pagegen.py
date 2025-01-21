import argparse
from sys import exit, stdout
from os import system, open, O_CREAT, O_EXCL, remove
from os.path import join, isfile
from Common import Common
from traceback import print_exception
from constants import SITE_ENV, LOCK_FILE
from Site import Site
from pathlib import Path
from Environment import Environment


def find_site_dir(path=False):
    '''
    Retrns path to site env if found in current directory or one of its parents
    '''

    if not path:
        path = Path.cwd()

    possible_site_env = path / SITE_ENV

    if possible_site_env.is_file():
        return str(possible_site_env.parent)
    elif path != path.parent:
        return find_site_dir(path.parent)


if __name__ == '__main__':

    site_dir = find_site_dir()
    lock_file = join(site_dir, LOCK_FILE)

    try:
        system('') # Enable ansi escape codes

        p = argparse.ArgumentParser()

        p.add_argument('-g', '--generate', action='store_true', help='Generate site')
        p.add_argument('-V', '--verbose', action='store_true', help='Increase verbosity')
        p.add_argument('-d', '--dry-run', action='store_true', help='Do not write to disk')
        p.add_argument('-i', '--ignore-lock', action='store_true', help='Ignore lock file')
        p.add_argument('-c', '--clear-cache', action='store_true', help='Clear caches before building')
        a = p.parse_args()

        settings = {
            'verbose': a.verbose,
            'dry_run': a.dry_run,
        }

        c = Common(settings=settings)
        env = Environment(join(site_dir, SITE_ENV)).env

        if a.generate:

            if site_dir is None:
                c.log_error(f'Unable to find {SITE_ENV}')
                exit(1)

            if isfile(lock_file):
                c.log_warning(f'Lock file found: {lock_file}')

                if a.ignore_lock == False and stdout.isatty() and input('Delete lock file and continue? [N|y] ') == 'y':

                    remove(lock_file)
                else:
                    exit()
            else:
                open(lock_file, O_CREAT | O_EXCL)

            s = Site(site_dir=site_dir, settings=settings, env=env)

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
        c.log_error('Unknown failure')
        print_exception(type(e), e, e.__traceback__)
        exit(1)
