from pagegen.utility import DEFAULTPAGETEMPLATE, DATEFORMAT
from datetime import date

class virtualpage:
	''' Basic page class '''

	def __init__(self):
		self.url_path='',
		self.absolute_url='',
		self.children=[]
		self.rst=''
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
			'category': None,
			'header profile': None,
			'search index exclude': False,
			'preserve file name': False,
			'sitemap lastmod': None,
			'sitemap changefreq': None,
			'sitemap priority': None,
			'exclude html minify': False
		}


	def generate_crumb_trail(self):
		html=''
		for p in self.crumb_trail:
			html+=' > %s' % p.title
		return html
