from sys import exit, stderr
from re import sub, match
from os import getcwd, sep, environ
from os.path import isfile
from subprocess import check_call
from pagegen.constants import SITECONF, DIRDEFAULTFILE


def urlify(string):
	''' Anything wich isn't alphanumeric, - or _ gets replaced with a - '''
	url = string.lower()
	url = sub('[^/a-z0-9-_.]', '-', url)
	# Replace any double dashes
	url = sub('--', '-', url)
	return url


def report_error(code, message):
	stderr.write('Error:  %s\n' % message)
	exit(code)


def report_warning(message):
	print('Warning: %s' % message)


def report_notice(message):
	print('Notice:  %s' % message)


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



