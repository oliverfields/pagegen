import argparse
from sys import exit
from os import system
from Common import Common
from traceback import print_exception
from constants import SITE_ENV
from Site import Site
from pathlib import Path


def generate_site():
    print('hi')


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

    try:
        system('') # Enable ansi escape codes

        p = argparse.ArgumentParser()

        p.add_argument('-g', '--generate', action='store_true', help='Generate site')
        p.add_argument('-V', '--verbose', action='store_true', help='Increase verbosity')
        p.add_argument('-d', '--dry-run', action='store_true', help='Do not write to disk')
        a = p.parse_args()

        settings = {
            'verbose': a.verbose,
            'dry_run': a.dry_run
        }

        c = Common(settings=settings)

        if a.generate:
            site_dir = find_site_dir()

            if site_dir is None:
                c.log_error(f'Unable to find {SITE_ENV}')
                exit(1)

            s = Site(site_dir=site_dir, settings=settings)


    except Exception as e:
        c.log_error('Unknown failure')
        print_exception(type(e), e, e.__traceback__)
        exit(1)
