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

from os import sep, access, X_OK
from os.path import splitext, join
from re import sub, search
from datetime import datetime
from Utility import DIRDEFAULTFILE, TARGETDIR, CONTENTDIR, is_default_file, report_warning, DEFAULTPAGETEMPLATE, load_file, NEWLINE
from subprocess import check_output


class Page:
	""" Bread and butter of pagegen """

	def __init__(self, path, site_dir, parent=False, base_url='', url_include_index=True, default_extension=''):
		self.url_path='',
		self.children=[]
		self.rst=''
		self.title=''
		self.source_path=path
		self.target_path=''
		self.html=''
		self.menu=''
		self.crumb_trail=[]
		self.extension=''
		self.base_url=base_url
		self.parent=parent
		self.menu_title=''
		self.url_include_index=url_include_index
		self.hook_environment={}

		self.headers={
			'sitemap exclude': False, 
			'menu exclude': False,
			'description': None,
			'title': None,
			'generate html': True,
			'menu title': None,
			'template': DEFAULTPAGETEMPLATE,
		}

		# If file is executable then the contents from it's stdout, else just read the file
		if access(self.source_path, X_OK):
			try:
				content=check_output(self.source_path)
			except Exception as e:
				report_error(1,"File '%s' execution failed: %s" % (self.source_path, e))
		else:
			content=load_file(self.source_path)

		self.load_page_content(self.source_path, content, site_dir,  default_extension)


	def generate_crumb_trail(self):
		html=''
		for p in self.crumb_trail:
			html+=' > %s' % p.title
		return html


	def set_paths(self, path, site_path):
		''' Create url'ed and target version of path '''

		# Remove non site path
		path_part=path.replace(site_path+sep+CONTENTDIR, '')

		self.target_dir=join(site_path, TARGETDIR)

		# Replace os dir seperator with forward slash
		path_part.replace(sep, '/')

		# Remove ordering prefix
		path_part=sub('/[0-9]*_', '/', path_part)

		# Lowercase
		path_part=path_part.lower()

		# Replace anything that isn't a charachter, number, slash, underscore or hyphen with a hyphen
		path_part=sub('[^/a-z0-9-_.]', '-', path_part)

		self.url_path=self.base_url+path_part

		# If not show index in url, strip it
		if self.url_include_index != True:
			self.url_path=sub('%s%s$' % (DIRDEFAULTFILE, self.extension), '', self.url_path)

		# Replace / with os dir seperator for target path
		path_part=path_part.replace('/', sep)

		self.target_path='%s%s%s%s' % (site_path, sep,TARGETDIR, path_part)


	def set_title_from_path(self, path):
		# Get path leaf

		# Delete any extension
		path, extension=splitext(path)

		# If Directory, then need to chop off default to get actual title
		if path.endswith(sep+DIRDEFAULTFILE):
			path=sub(sep+DIRDEFAULTFILE+'$', '', path)

		leaf=path.rpartition(sep)[2]

		# Remove any XXX_ ordering prefix
		split_leaf=leaf.split('_')
		if len(split_leaf) == 1:
			self.title=split_leaf[0]
		else:
			self.title=split_leaf[1]


	def set_header(self, line):
		''' Try to set header value, return false if fail '''

		if ':' in line:
			potential_header=line.split(':')
			potential_name=potential_header[0].lower().strip()
			potential_value=potential_header[1]

			if potential_name in self.headers:
				self.headers[potential_name]=potential_value.strip()
				return self.headers[potential_name]
			else:
				report_warning("Unknown header in '%s': %s" % (self.source_path, line))
				return False
		else:
			return False


	def load_page_content(self, path, content, site_dir, default_extension):
		'''
		Parse source setting header and content attributes
		Format:
			<header>: <value>	<- Optional
								<-Blanke line, if headers
			<rst content>

		First line must either be header or content
		'''

		in_header=None
		for line in content.split(NEWLINE):
			# If file starts with lines that match possible headers, then grab values, after first blank line rest is content.

			if in_header is None and search(r'^[a-zA-Z]+', line) is None:
				in_header=False

			if in_header is None and self.set_header(line):
				in_header=True
				continue

			if line == '' and in_header:
				in_header=False
				continue

			# If blank line definitely not in header
			if line == '':
				in_header=False

			# First line was a header
			if in_header:
				# Set header
				if self.set_header(line):
					continue
				# If blank line next lines are content
				else:
					in_header=False
					continue
			else:
				self.rst+=line+NEWLINE

		# Strip last new line
		self.rst=self.rst.rstrip(NEWLINE)

		# Split off extension
		path_part, file_extension=splitext(path)

		if self.headers['title'] != None:
			self.title=self.headers['title']
		else:
			self.set_title_from_path(path)

		if self.headers['menu title'] != None:
			self.menu_title=self.headers['menu title']
		else:
			self.menu_title=self.title

		if file_extension:
			self.extension=file_extension
			self.set_paths(path, site_dir)
		else:
			self.extension=default_extension
			self.set_paths(path+self.extension, site_dir)

		