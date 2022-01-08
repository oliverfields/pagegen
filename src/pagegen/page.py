from pagegen.virtualpage import virtualpage
from os import sep, access, X_OK, environ
from os.path import splitext, join
from re import sub, search
from pagegen.utility import DIRDEFAULTFILE, CONTENTDIR, is_default_file, report_warning, load_file, NEWLINE, urlify, HEADERPROFILEDIR, relative_path, TARGETDIR, report_error, setup_environment_variables
from subprocess import check_output


class page(virtualpage):
	""" Bread and butter of pagegen """

	def __init__(self):
		virtualpage.__init__(self)

	def load(self, path, site_dir, target_dir_name, parent=False, base_url='', url_include_index=True, default_extension='', environment='', absolute_urls=False):

		self.source_path=path
		self.site_dir=site_dir
		self.target_dir_name=target_dir_name
		self.parent=parent
		self.base_url=base_url
		self.url_include_index=url_include_index
		self.default_extension=default_extension

		# If file is executable then the contents from it's stdout, else just read the file
		if access(self.source_path, X_OK):
			page_environment={
				'PAGEGEN_SITE_DIR': self.site_dir,
				'PAGEGEN_SOURCE_DIR': self.source_path,
				'PAGEGEN_TARGET_DIR': self.target_dir_name,
				'PAGEGEN_ENVIRONMENT': environment,
				'PAGEGEN_BASE_URL': self.base_url,
				'PAGEGEN_DEFAULT_EXTENSION': self.default_extension
			}

			setup_environment_variables(page_environment)

			try:
				content=check_output(self.source_path, text=True)

			except Exception as e:
				report_error(1,"File '%s' execution failed: %s" % (self.source_path, e))
		else:
			content=load_file(self.source_path)

		self.load_page_content(self.source_path, content, self.site_dir, self.default_extension, absolute_urls)


	def set_paths(self, path, site_path, absolute_urls):
		''' Create url'ed and target version of path '''

		# Remove non site path
		path_part=path.replace(site_path+sep+CONTENTDIR, '')

		self.target_dir=join(site_path, self.target_dir_name)

		# Replace os dir seperator with forward slash
		path_part.replace(sep, '/')

		# If not preserve file name, then make it nicely urlified
		if self.headers['preserve file name'] == False:
			# Remove ordering prefix
			path_part=sub('/[0-9]*_', '/', path_part)

			# Lowercase
			path_part=path_part.lower()

			# Replace anything that isn't a charachter, number, slash, underscore or hyphen with a hyphen
			path_part=urlify(path_part)


		if absolute_urls:
			self.url_path = self.base_url+path_part
		else:
			self.url_path = path_part

		self.absolute_url = self.base_url + path_part

		# If not show index in url, strip it
		if self.url_include_index != True:
			self.url_path=sub('%s%s$' % (DIRDEFAULTFILE, self.extension), '', self.url_path)

		# Replace / with os dir seperator for target path
		path_part=path_part.replace('/', sep)

		self.target_path="%s%s%s%s%s%s" % (self.site_dir, sep, TARGETDIR, sep, self.target_dir_name, path_part)
		self.target_path = self.target_path

		# Set page_file_name after all url_path above stuff is done
		self.page_file_name = path_part
		if self.page_file_name == '':
			self.page_file_name = DIRDEFAULTFILE + self.default_extension


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

			if potential_name == 'tags':
				tags=potential_value.split(',')
				for t in tags:
					self.headers['tags'].append(t.strip())
				return self.headers['tags']
			elif potential_name in self.headers:
				self.headers[potential_name]=potential_value.strip()
				return self.headers[potential_name]
			else:
				self.custom_headers[potential_name] = potential_value.strip()
				return self.custom_headers[potential_name]
		else:
			return False


	def is_header(self, line):
		if ':' in line:
			potential_header=line.split(':')
			potential_name=potential_header[0].lower().strip()
			potential_value=potential_header[1]

			if isinstance(potential_name, str) and isinstance(potential_value, str):
				return True
			else:
				report_warning("Unknown header in '%s': %s" % (self.source_path, line))
				return False
		else:
			return False


	def load_header_profile(self, site_dir):
		''' If header profile specified, load header values from profile file '''
		for h in self.raw_headers:
			header=h.split(':')
			if header[0].lower().strip() == 'header profile':
				profile_file=join(site_dir, HEADERPROFILEDIR, header[1].strip())
				try:
					profile=load_file(profile_file)
				except:
					report_warning("Unable to open header profile '%s'" % relative_path(profile_file))
				
				for header in profile.split(NEWLINE):
					self.set_header(header)
				# Remember to set header profile
				self.headers['header profile']=profile_file
				break


	def load_page_content(self, path, content, site_dir, default_extension, absolute_urls):
		'''
		Parse source and save headers and content attributes
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

			if in_header is None and self.is_header(line):
				self.raw_headers.append(line)
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
				if self.is_header(line):
					self.raw_headers.append(line)
					continue
				# If blank line next lines are content
				else:
					in_header=False
					continue
			else:
				self.rst+=line+NEWLINE


		# Check if using a header profile
		self.load_header_profile(site_dir)

		# Load headers from page, can overwrite header profiles
		for header in self.raw_headers:
			self.set_header(header)

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
			self.set_paths(path, site_dir, absolute_urls)
		else:
			if self.headers['preserve file name'] == False:
				self.extension=default_extension
			self.set_paths(path+self.extension, site_dir, absolute_urls)

