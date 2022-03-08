from pagegen.utility import DEFAULTPAGETEMPLATE, DATEFORMAT, DIRDEFAULTFILE, CONTENTDIR, urlify, TARGETDIR
from datetime import date
from os.path import splitext
from re import sub

class virtualpage:
	''' Basic page class '''

	def __init__(self):
		self.url_path='',
		self.absolute_url='',
		self.children=[]
		self.content=''
		self.title=''
		self.source_path=''
		self.target_path=''
		self.page_file_name=''
		self.html=''
		self.menu=''
		self.crumb_trail=[]
		self.extension=''
		self.base_url=''
		self.parent=False
		self.menu_title=''
		self.url_include_index=''
		self.hook_environment={}
		self.next_page=False
		self.previous_page=False
		self.site_dir=''
		self.default_extension=''
		self.raw_headers=[]
		self.target_dir=None
		self.custom_headers={}
		self.markup='rst'
		self.toc=False
		self.authors = []
		self.excerpt = False
		self.headers={
			'sitemap exclude': False, 
			'menu exclude': False,
			'description': None,
			'title': None,
			'generate html': True,
			'link chain exclude': False,
			'menu title': None,
			'template': DEFAULTPAGETEMPLATE,
			# Use string so consistent with what is read from files, all date functions must take this into account
			'publish': date.today().strftime(DATEFORMAT),
			'rss include': False,
			'tags': [],
			'categories': [],
			'search index exclude': False,
			'preserve file name': False,
			'sitemap lastmod': None,
			'sitemap changefreq': None,
			'sitemap priority': None,
			'exclude html minify': False,
			'markup': None,
			'number headings': False,
			'toc': False,
			'disable shortcodes': False,
			'authors': None,
			'series': False,
		}


	def __str__(self):
		return '<page: ' + self.title + ' ' + self.url_path + '>'


	def __repr__(self):
		r = '{\n'

		for attribute in sorted(self.__dict__):
			value = self.__dict__[attribute]
			if isinstance(value, str) or isinstance(value, bool) or isinstance(value, int):
				r += "\t'" + attribute + "': " + str(value) + ",\n"
			elif isinstance(value, list):
				if len(value) > 0:
					r += "\t'" + attribute + "': [\n"
					for i in value:
						r += "\t\t" + str(i) + ",\n"
					r = r.rstrip(",\n")
					r += "\n\t]\n"
				else:
					r += "\t'" + attribute + "': []\n"
			elif isinstance(value, dict):
				if len(value.keys()):
					r += "\t'" + attribute + "': {\n"
					for k, v in value.items():
						r += "\t\t'" + k + "': " + str(v) + ",\n"
					r = r.rstrip("\n,")
					r += "\n\t},\n"
				else:
					r += "\t'" + attribute + "': {}\n"

		r = r.rstrip("\n,")
		r += "\n}"

		return r


	def set_excerpt(self):
		''' Add everything preceeding <!-- more --> to self.excerpt '''
		maybe_excerpt = self.content.split('<!-- more -->', 1)
		if len(maybe_excerpt) == 2:
			self.excerpt = maybe_excerpt[0]


	def generate_crumb_trail(self):
		html=''
		for p in self.crumb_trail:
			html+=' > %s' % p.title
		return html


	def set_title_from_path(self, path):
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


	def set_paths(self, source_path, site_path, absolute_urls, environment_dir_name, base_url):
		''' Create url'ed and target version of path '''
		# Remove non site path
		path_part = source_path.replace(site_path + '/' + CONTENTDIR, '')

		self.target_dir = site_path + '/' + environment_dir_name

		# If not preserve file name, then make it nicely urlified
		if self.headers['preserve file name'] == False:
			# Remove ordering prefix
			path_part=sub('/[0-9]*_', '/', path_part)

			# Lowercase
			path_part=path_part.lower()

			# Replace anything that isn't a charachter, number, slash, underscore or hyphen with a hyphen
			path_part = urlify(path_part)

		if absolute_urls:
			self.url_path = base_url + path_part
		else:
			self.url_path = path_part

		self.absolute_url = base_url + path_part

		# If not show index in url, strip it
		if self.url_include_index != True:
			self.url_path = sub('%s%s$' % (DIRDEFAULTFILE, self.extension), '', self.url_path)

		self.target_path="%s%s%s%s%s%s" % (site_path, '/', TARGETDIR, '/', environment_dir_name, path_part)

		# Set page_file_name after all url_path above stuff is done
		self.page_file_name = path_part
		if self.page_file_name == '':
			self.page_file_name = DIRDEFAULTFILE + self.default_extension
