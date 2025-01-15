from sys import stderr, stdout
from os import system
from pathlib import Path
from constants import SITEENV, ESCAPECODES


system("") # Enable ansi escape codes

def log_error(message):
    stderr.write('%sERROR%s: %s\n' % (ESCAPECODES['red'], ESCAPECODES['default'], message))


def log_warning(message):
    stderr.write('%sWARNING%s: %s\n' % (ESCAPECODES['yellow'], ESCAPECODES['default'], message))


def log_notice(message):
    stdout.write('%sNOTICE%s: %s\n' % (ESCAPECODES['green'], ESCAPECODES['default'], message))


def log_info(message):
    stdout.write('%sINFO%s: %s\n' % (ESCAPECODES['blue'], ESCAPECODES['default'], message))


def find_site_dir(path=False):
    if not path:
        path = Path.cwd()

    possible_site_env = path / SITEENV

    if possible_site_env.is_file():
        return possible_site_env.parent
    elif path != path.parent:
        return find_site_dir(path.parent)

