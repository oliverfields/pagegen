#------------------------------------------------------------
# Pagegen - static site generator
# Copyright (C) 2015  Oliver Fields, pagegen@phnd.net
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

''' General utility library '''

from sys import exit, stderr
from os import listdir, getcwd, sep, access, X_OK, putenv
from os.path import join, isdir, isfile, expanduser
from ConfigParser import RawConfigParser
from io import StringIO
from re import match, sub
from subprocess import check_call


# Constants
PAGEGENCONF='pagegen.conf'
HOME=expanduser("~")
SITECONF='site.conf'
CONFROOT='root'
CONTENTDIR='content'
DIRDEFAULTFILE='index'
TARGETDIR='site'
INCLUDEDIR='include'
SITEMAPFILE='sitemap.xml'
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
	print 'Warning: %s' % message


def report_notice(message):
	print 'Notice:  %s' % message


def load_config(files, add_dummy_section=True):
	''' Load pagegen config according to list of possible config file locations '''

	conf_path=False

	for f in files:
		if isfile(f):
			conf_path=f
			break

	if not conf_path:
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
	with open (file, "r") as f:
		data=f.read()#.replace('\n', '')
	return data


def write_file(file, content):
	# 'a' -> Open file for appending, will create if not exist
	with open(file, 'a') as f:
		f.write(content)

def is_default_file(file):
	return match('.*'+DIRDEFAULTFILE+'[.a-z]*$', file)

def exec_hook(hook, env=None):
	''' Run specified hook if executable '''

	for name, value in env.iteritems():
		putenv(name, value)

	if isfile(hook) and access(hook, X_OK):
		try:
			check_call(hook)
		except Exception as e:
			report_error(1,"Hook '%s' execution failed: %s" % (hook, e))
