''' General utility library '''

from sys import exit, stderr
from os import listdir, getcwd, sep
from os.path import join, isdir, isfile, expanduser
from ConfigParser import RawConfigParser
from io import StringIO
from re import match


# Constants
PAGEGENCONF='pagegen.conf'
HOME=expanduser("~")
SITECONF='site.conf'
CONFROOT='root'
CONTENTDIR='content'
DIRDEFAULTFILE='index'
TARGETDIR='site'
INCLUDEDIR='include'
SITEMAPFILE='sitemap.txt'
HOOKDIR='hooks'
DEFAULTPAGETEMPLATE='page.tpl'
TEMPLATEDIR='templates'
NEWLINE='\n'


def report_error(code, message):
	stderr.write('Error: %s\n' % message)
	exit(code)


def report_warning(message):
	print 'Warning: %s' % message


def report_notice(message):
	print 'Notice: %s' % message


def load_config(files):
	''' Load pagegen config according to list of possible config file locations '''

	conf_path=False

	for f in files:
		if isfile(f):
			conf_path=f
			break

	if not conf_path:
		repot_error(1, "Pagegen.conf, not found in '%s', '%s' or '%s'" % (current_conf, home_conf, etc_conf))

	try:
		# Don't need section headers so just add a dummy root section before passing to confpars
		ini_str=u'[root]\n' + open(conf_path, 'r').read()
		ini_fp=StringIO(ini_str)
		c=RawConfigParser()
		c.readfp(ini_fp)
	except Exception as e:
		report_error(1,"Unable to read config from '%s': %s" % (conf_path, e))

	return c


def get_site_conf_path():
	''' Return path of site.conf, either current working one or one of its parents '''

	cwd=getcwd()
	dirs=cwd.split(sep)
	# Disgard root dir
	dirs.pop(0)

	for i in range(len(dirs), 0, -1):
		site_dir=''
		for x in range(0, i):
			site_dir+=sep+dirs[x]
		site_conf=site_dir+sep+SITECONF
		if isfile(site_conf):
			return site_conf

	return False


def load_file(file):
	with open (file, "r") as f:
		data=f.read()#.replace('\n', '')
	return data


def write_file(file, content):
	with open(file, 'a') as f:
		f.write(content)

def is_default_file(file):
	return match('.*'+DIRDEFAULTFILE+'[.a-z]*$', file)
