from sys import exit, stderr
from re import sub, match
from os import getcwd, sep, environ, system
from os.path import isfile, splitext
from subprocess import check_call
from pagegen.constants import SITECONF, DIRDEFAULTFILE

system("") # Enable ansi escape codes

ESCAPECODES = {
  "green": "\033[1;32m",
  "yellow": "\033[1;33m",
  "red": "\033[1;31m",
  "default": "\033[0m"
}


def urlify(string):
    ''' Make path name into a url '''

    # Remove ordering prefix
    url = sub('/[0-9]+_', '/', string)

    url = url.lower()

    # Anything wich isn't alphanumeric, - or _ gets replaced with a -

    url = sub('[^/a-z0-9-_.]', '-', url)

    # Replace multiple dashes with a single dash
    url = sub('-+', '-', url)

    return url


def report_error(code, message):
    stderr.write('%sERROR%s: %s\n' % (ESCAPECODES['red'], ESCAPECODES['default'], message))
    exit(code)


def report_warning(message):
    stderr.write('%sWARNING%s: %s\n' % (ESCAPECODES['yellow'], ESCAPECODES['default'], message))


def report_notice(message):
    stderr.write('%sNOTICE%s: %s\n' % (ESCAPECODES['green'], ESCAPECODES['default'], message))


def get_site_conf_path(conf_file=False):
    ''' Return path of site.conf, either current working one or one of its parents '''

    if not conf_file:
        conf_file=SITECONF

    cwd=getcwd()
    dirs=cwd.split(sep)
    # Disgard root dir
    dirs.pop(0)

    for i in range(len(dirs), 0, -1):
        site_dir=''
        for x in range(0, i):
            site_dir+=sep+dirs[x]
        site_conf=site_dir+sep+conf_file
        if isfile(site_conf):
            return site_conf

    return False

def exec_script(script, env=None):
    ''' Run specified script if executable '''

    setup_environment_variables(env)

    try:
        check_call(script)
    except Exception as e:
        report_error(1,"Script '%s' execution failed: %s" % (script, e))


def setup_environment_variables(env):
    # Unset all PAGEGEN_* environment variables
    for env_name, env_value in environ.items():
        if env_name.startswith('PAGEGEN_'):
            environ.pop(env_name)

    # Ensure all environment values are utf-8
    if env != None:
        for name, value in env.items():
            #putenv(name, value.encode('utf-8'))
            environ[name] = value


def is_default_file(file):
    return match('.*'+DIRDEFAULTFILE+'[.a-z]*$', file)


def title_from_path(path):
    # Get path leaf

    # Delete any extension
    path, extension = splitext(path)

    # If Directory, then need to chop off default to get actual title
    if path.endswith('/' + DIRDEFAULTFILE):
        path = sub('/' + DIRDEFAULTFILE + '$', '', path)

    leaf = path.rpartition('/')[2]

    # Remove any XXX_ ordering prefix if present
    if '_' in leaf:
        split_leaf = leaf.split('_')
        title = split_leaf[1]
    else:
        title = leaf

    return title


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


def remove_suffix(text, suffix):
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text
