from pagegen.constants import DEFAULTPAGETEMPLATE, DATEFORMAT, DIRDEFAULTFILE, CONTENTDIR, TARGETDIR
from pagegen.utility_no_deps import urlify, title_from_path
from datetime import date
from re import sub

class virtualpage:
	''' Basic page class '''

	def __init__(self):
		self.url_path='',
		self.absolute_url=''
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
		self.markup='md'
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


	def get_links(self):
		'''
		Extracts list of URLs from html
		'''

		import warnings
		from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
		warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

		self.links = []

		for a in BeautifulSoup(self.html, features='lxml').find_all('a', href=True):
			self.links.append({
				'url': a['href'],
				'title': a.contents[0]
			})


	def generate_crumb_trail(self):
		html=''
		for p in self.crumb_trail:
			html+=' > %s' % p.title
		return html


	def strip_extensions(self, path, extensions_list):
		'''
		Replace file extensions given in list
		'''

		for ext in extensions_list:
			if path.endswith(ext):
				return path[:-len(ext)]

		return path



	def set_paths(self, source_path, site_path, absolute_urls, environment_dir_name, base_url, strip_extensions):
		''' Create url'ed and target version of path '''

		# Remove non site path
		path_part = source_path.replace(site_path + '/' + CONTENTDIR, '')

		if self.headers['preserve file name'] == False and strip_extensions:
			path_part = self.strip_extensions(path_part, strip_extensions)

		self.target_dir = site_path + '/' + environment_dir_name

		# If not preserve file name, then make it nicely urlified
		if self.headers['preserve file name'] == False:
			# Replace anything that isn't a charachter, number, slash, underscore or hyphen with a hyphen
			path_part = urlify(path_part)

		if absolute_urls:
			self.url_path = base_url + path_part
		else:
			self.url_path = path_part

		# If not show index in url, strip it
		if self.url_include_index != True:
			if len(self.extension) > 0 and self.url_path.endswith(self.extension):
				self.url_path = self.url_path[:-len(self.extension)]
			if len(DIRDEFAULTFILE) > 0 and self.url_path.endswith(DIRDEFAULTFILE):
				self.url_path = self.url_path[:-len(DIRDEFAULTFILE)]

		self.absolute_url = base_url + self.url_path


		self.target_path="%s%s%s%s%s%s" % (site_path, '/', TARGETDIR, '/', environment_dir_name, path_part)

		# Set page_file_name after all url_path above stuff is done
		self.page_file_name = path_part
		if self.page_file_name == '':
			self.page_file_name = DIRDEFAULTFILE + self.default_extension

	def set_title_from_path(self, path):
		return title_from_path(path)

