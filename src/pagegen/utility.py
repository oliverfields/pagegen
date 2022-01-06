''' General utility library '''

from sys import exit, stderr
from os import listdir, getcwd, sep, access, X_OK, O_APPEND, environ
from os.path import join, isdir, isfile, expanduser
from configparser import RawConfigParser
from io import StringIO
from re import match, sub, finditer
from subprocess import check_call
import codecs

# Constants
HOME=expanduser("~")
SITECONF='site.conf'
CONFROOT='root'
CONTENTDIR='content'
DIRDEFAULTFILE='index'
TARGETDIR='site'
INCLUDEDIR='include'
SITEMAPFILE='sitemap.xml'
SITEMAPTXTFILE='sitemap.txt'
HOOKDIR='hooks'
DEFAULTPAGETEMPLATE='page.tpl'
TEMPLATEDIR='templates'
NEWLINE='\n'
DATEFORMAT='%Y-%m-%d'
RSSFEEDFILE='feed.rss'
HEADERPROFILEDIR='header_profiles'
STOPWORDSFILE='stopwords.txt'
SEARCHINDEXFILE='search-index.json'


def get_first_words(string, x):
	if len(string) > x:
		string=sub('\ [^ ]*$','...', string[:x])

	return string


def get_environment_config(config):

	if len(config.sections()) == 1:
		return config.sections()[0]
	else:
		default_environment=None
		for section in config.sections():
			try:
				# If true then we have our environment
				config.get(section,'default_environment')
				return section

			except Exception as e:
				pass

		report_error(1, "Unable to load a section from site.conf")


def relative_path(path):
	''' Return path realative to cwd '''

	return path.replace(getcwd()+sep, '')

def urlify(string):
	''' Anything wich isn't alphanumeric, - or _ gets replaced with a - '''
	url=string.lower()
	return sub('[^/a-z0-9-_.]', '-', url)


def report_error(code, message):
	stderr.write('Error:  %s\n' % message)
	exit(code)


def report_warning(message):
	print('Warning: %s' % message)


def report_notice(message):
	print('Notice:  %s' % message)


def load_config(files, add_dummy_section=True):
	''' Load pagegen config according to list of possible config file locations '''

	conf_path=False

	for f in files:
		if isfile(f):
			conf_path=f
			break

	if not conf_path:
		print(files)
		report_error(1, "pagegen.conf, not found in current, ~/.config/ or /etc/ directories")

	try:
		c=RawConfigParser()
		if add_dummy_section:
			# Don't need section headers so just add a dummy root section before passing to confpars
			ini_str=u'['+CONFROOT+']\n' + open(conf_path, 'r').read()
			ini_fp=StringIO(ini_str)
			c.readfp(ini_fp)
		else:
			# Config has sections, so open as normal
			c.readfp(open(conf_path))

	except Exception as e:
		report_error(1,"Unable to read config from '%s': %s" % (conf_path, e))

	return c


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


def load_file(file):
	try:
		with codecs.open (file, "r", 'utf-8') as f:
			data=f.read()
	except Exception as e:
		raise Exception('Unable to load file %s: %s' % (file, e))

	return data



def load_template(template_file):
	''' Load template and for all {{<protocol>:<path>}} replace with contents, currently only protocol file supported '''

	try:
		with codecs.open (template_file, "r", 'utf-8') as f:
			data=f.read()
	except Exception as e:
		raise Exception('Unable to load template %s: %s' % (template_file, e))

	for includes in finditer('{{[^}]*:.*}}', data):
		# Chop off curly brackets
		include_file = includes.group().replace('{{', '')
		include_file = include_file.replace('}}', '')

		include_file_parts = include_file.split(':')
		protocol = include_file_parts[0]
		path = include_file_parts[1]

		if protocol == 'file':

			# Chop off first two slashes to get file path
			include_file_path = path[2:]

			# Load content from include file
			try:
				include_content = load_file(include_file_path).rstrip()
				data = data.replace(includes.group(), include_content)
			except Exception as e:
				raise Exception('Template %s: Unable to load include %s: %s' % (template_file, include_file_path, e))
		else:
			raise Exception('Unsupported protocol %s in %s' % (protocol, include_file)) 

	return data


def write_file(file, content):
	# 'a' -> Open file for appending, will create if not exist
	try:
		with codecs.open(file, 'a', 'utf-8') as f:
			f.write(content)
	except Exception as e:
		raise (Exception('Unable to write file %s: %s' % (file, e)))


def is_default_file(file):
	return match('.*'+DIRDEFAULTFILE+'[.a-z]*$', file)


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


def exec_script(script, env=None):
	''' Run specified script if executable '''

	setup_environment_variables(env)

	try:
		check_call(script)
	except Exception as e:
		report_error(1,"Script '%s' execution failed: %s" % (script, e))

