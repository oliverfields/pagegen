from os import sep
from os.path import splitext, join
from re import sub
from datetime import datetime
from Utility import DIRDEFAULTFILE, TARGETDIR, CONTENTDIR, is_default_file


class Page:
	""" Bread and butter of pagegen """

	def __init__(self, path, site_dir):
		self.url_path=''
		self.children=[]
		self.rst=''
		self.title=''
		self.source_path=path
		self.target_path=''
		self.html=''
		self.menu=''
		self.header=''
		self.footer=''
		self.content=''
		self.extension=''

		self.headers={
			'sitemap exclude': False, 
			'menu exclude': False,
			'description': None,
			'title': None,
			'generate html': True,
		}

		self.load_page_from_path(self.source_path, site_dir)


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

		# Remove default file for directories, makes things look nice
		if is_default_file(path_part):
			if path_part == '/%s%s' % (DIRDEFAULTFILE, self.extension):
				self.url_path='/'
			else:
				self.url_path=sub('/%s%s$' % (DIRDEFAULTFILE, self.extension), '', path_part)+'/'
		else:
			self.url_path=path_part

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
				return False
		else:
			return False


	def load_page_from_path(self, path, site_dir):
		'''
		Parse source setting header and content attributes
		Format:
			<header>: <value>	<- Optional
								<-Blanke line, if headers
			<rst content>

		First line must either be header or content
		'''

		in_header=False
		with open(path) as f:
			for line in f:
				# If file starts with lines that match possible headers, then grab values, after first blank line rest is content.
				if self.set_header(line):
					in_header=True
					continue

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
					self.rst+=line

		# Split off extension
		path_part, file_extension=splitext(path)

		if self.headers['title'] != None:
			self.title=self.headers['title']
		else:
			self.set_title_from_path(path)

		if file_extension:
			self.extension=file_extension

		self.set_paths(path, site_dir)