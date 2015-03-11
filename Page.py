class Page:
	""" Bread and butter of pagegen """

	def __init__(self, path):
		self.url=''
		self.children=[]
		self.rst=''
		self.html=''
		self.source_path=path
		self.target_path=''
		self.source_timestamp=None
		self.target_timestamp=None
		self.menu_change=False
		self.overwrite_target=False

		self.headers={
			'Sitemap exclude': False, 
			'Sitemap frequency': None,
			'Sitemap priority': None,
			'Menu exclude': False,
			'Description': None,
		}

		self.load_page_from_path(self.source_path)


	def convert_rst2html(self):
		''' Convert page rst to html and update attribute'''
		pass


	def check_menu_change(self):
		''' Set menu change flag if page title or url are not the same as previously generated page '''
		pass


	def get_target_title(self):
		''' If target already exists get title update attribute '''
		pass


	def urlify_title(self):
		''' Create url'ed version of title, only alpha numeric, - and _ allowed '''

		pass


	def generate_html(self):
		''' Render page as fully stand alone html document '''
		pass


	def is_header(self, line):
		''' Determine if line matches header syntax '''
		if ':' in line:
			before_colon=line.split(':')[0]

		else:
			return False


	def load_page_from_path(self, path):
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
				if self.is_header(line):
					print 'Set header %s' % line
					in_header=True
					continue

				# First line was a header
				if in_header:
					# Set header
					if self.is_header(line):
						print 'Set header %s' % line 
					# If blank line next lines are content
					elif line == '':
						in_header=False
				else:
					self.rst+=line


