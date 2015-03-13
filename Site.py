from Utility import report_error, load_config, SITECONF, CONFROOT, CONTENTDIR, DIRDEFAULTFILE, TARGETDIR, INCLUDEDIR, load_file, write_file, report_warning, is_default_file, SITEMAPFILE
from ConfigParser import ConfigParser
from distutils.version import LooseVersion
from os.path import isdir, join, isfile, exists
from os import listdir, getcwd, sep, makedirs
from shutil import rmtree
from Page import Page
from docutils.core import publish_parts
from distutils.dir_util import copy_tree


class Site:
	""" Master object """

	def __init__(self, site_dir, config_file):
		self.pages=[]
		self.site_dir=''
		self.base_url=''
		self.menu_changed=False
		self.omit_menu=False
		self.ignore=[]
		self.home_menu_name=''
		self.header_template=''
		self.footer_template=''
		self.sitemap=''
		self.exclude_sitemap=False

		if isdir(site_dir):
			self.site_dir=site_dir
			self.target_dir=join(site_dir, TARGETDIR)
			self.include_dir=join(site_dir, INCLUDEDIR)
			self.CONTENTDIR=join(site_dir, CONTENTDIR)
		else:
			raise Exception("Site dir '%s' is not a directory" % site_dir)

		try:
			config=load_config([config_file])
		except Exception as e:
			raise Exception("Unable to load site config '%s': %s" % e)

		try:
			self.base_url=config.get(CONFROOT,'base_url')
		except:
			raise Exception('%s must contain base_url setting' % SITECONF)

		try:
			self.exclude_sitemap=config.get(CONFROOT,'exclude_sitemap')
		except Exception as e:
			print e

		try:
			header_template=join(self.site_dir, 'templates', 'header')
			self.header_template=load_file(header_template)
		except:
			raise Exception("Unable to load header template: '%s'" % header_template)

		try:
			footer_template=join(self.site_dir, 'templates', 'footer')
			self.footer_template=load_file(footer_template)
		except:
			raise Exception("Unable to load footer template: '%s'" % footer_template)

		
		content_path=join(self.site_dir, CONTENTDIR)
		# Try to load home page, ok if not there
		try:
			# Get home page, append it as first item
			home_page_path=self.get_dir_default_file(content_path)
			home_page=Page(home_page_path, self.site_dir)
			self.pages.append(home_page)
		except:
			pass

		# Load pages
		try:
			self.load_pages(content_path, self.pages)
		except Exception as e:
			raise Exception('Unable to load content: %s' % e)

		self.check_pages(self.pages)


	def generate_pages(self, pages):
		''' Recursively iterate over pages and generate html '''
		
		for p in pages:
			if p.headers['generate html'] == True:
				self.generate_header(p)
				self.generate_footer(p)
				self.generate_menu(self.pages, p)
				content=self.generate_content(p)
				p.html=p.header+p.menu+p.content+p.footer
			else:
				p.html=p.rst

			if p.children:
				self.generate_pages(p.children)


	def check_pages(self, pages):
		''' Check all files are uniquely named (because of xxx_ prefix potentially can have conflicts) '''
		page_urls={}
		page_target_paths={}

		for p in pages:
			if p.target_path in page_target_paths:
				report_error(1,"Target path '%s' for page '%s' is already set for '%s'" % (p.target_path.replace(getcwd()+sep,''), p.source_path.replace(getcwd()+sep,''), page_target_paths[p.target_path].replace(getcwd()+sep,'')))
			elif p.target_path.endswith(SITEMAPFILE) and self.exclude_sitemap == 'False':
				report_error(1,"Page '%s' illegal name '%s'" % (p.source_path.replace(getcwd()+sep,''), SITEMAPFILE))
			else:
				page_target_paths[p.target_path]=p.source_path

			if p.url_path in page_urls:
				report_error(1,"URL '%s' for page '%s' already set for '%s'" % (p.url_path, p.source_path, page_urls[p.url_path]))
			else:
				page_urls[p.url_path]=p.source_path

			if p.children:
				self.check_pages(p.children)


	def get_dir_default_file(self, path):
		''' Return default file starting with DIRDEFAUTFILE '''
		for f in listdir(path):
			if f.startswith(DIRDEFAULTFILE):
				return join(path, f)
		return False


	def load_pages(self, dir_path, parent):
		''' Recursively load pages from content directory '''

		file_list = listdir(dir_path)
		file_list.sort(key=LooseVersion)

		for f in file_list:
			f_path=join(dir_path, f)

			# If dir then must have default file defined
			if isdir(f_path):
				dir_page=self.get_dir_default_file(f_path)

				if dir_page:
					p=Page(dir_page, self.site_dir)
					parent.append(p)
					self.load_pages(f_path, p.children)
				else:
					report_error(1, "Directory '%s' is missing '%s' file" % (f_path, DIRDEFAULTFILE))
			elif is_default_file(f):
				pass
			elif isfile(f_path):
				parent.append(Page(f_path, self.site_dir))
			else:
				raise Exception("Unknown object '%s'" % f_path)


	def move_to_target(self):
		''' Create generated site in target dir '''

		# Delete target dir if exists
		if exists(self.target_dir):
			try:
				rmtree(self.target_dir)
				makedirs(self.target_dir)
			except Exception as e:
				raise Exception(e)

		# Write pages to disk
		self.save_pages(self.pages)

		# Copy include dir to target dir
		include_dir=join(self.target_dir, INCLUDEDIR)
		if exists(include_dir):
			report_warning('Include exists, skipping copy to site directory')
		else:
			copy_tree(self.include_dir, include_dir)

		# Create sitemap.txt
		write_file(join(self.target_dir, SITEMAPFILE), self.sitemap)


	def save_pages(self, pages):
		''' Create files and 	directories in target dir '''

		for p in pages:
			if p.children:
				dir_path=p.target_path.rpartition(sep)[0]
				makedirs(dir_path)
				write_file(p.target_path, p.html)
				self.save_pages(p.children)
			else:
				write_file(p.target_path, p.html)


	def generate_menu(self, pages, page, level=1):

		if page.menu == '':
			page.menu='<ul>'

		for p in pages:

			if p.headers['menu exclude'] == 'True':
				continue

			# Check if this page is parent of examined page
			try:
				if page.url_path.split('/')[level] == p.url_path.split('/')[level]:
					section_match=True
				else:
					section_match=False
			except:
				section_match=False

			# Check if examined page is same as current page
			if p == page:
				page_match=True
			else:
				page_match=False

			# Check if page is a parent of current page
			if page_match:
				css_class=' class="selected_page"'
			elif section_match:
				css_class=' class="active_section"'
			else:
				css_class=''

			if p.children:
				page.menu+='<li><a href="%s"%s>%s</a>' % (p.url_path, css_class, p.title)
				page.menu+='<ul>'
				self.generate_menu(p.children, page, level=level+1)
				page.menu+='</ul>'
				page.menu+='</li>'
			else:
				page.menu+='<li><a href="%s"%s>%s</a></li>' % (p.url_path, css_class, p.title)

		if level==1:
			page.menu+='</ul>'


	def generate_header(self, page):
		html=self.header_template.replace('{{base_url}}', self.base_url)
		html=html.replace('{{title}}', page.title)

		if page.headers['description']:
			description=page.headers['description']
		else:
			description=''

		html=html.replace('{{description}}', description)

		page.header=html


	def generate_footer(self, page):
		page.footer=self.footer_template


	def generate_content(self, page):
		# Use docutils to convert rst to html
		parts=publish_parts(page.rst, writer_name='html')
		page.content=parts['body']


	def generate_sitemap(self, pages):
		''' Create sitmap.txt '''
		for p in pages:
			if p.headers['sitemap exclude'] == False:
				if p.children or p.url_path == '/':
					self.sitemap+='%s%s%s%s\n' % (self.base_url, p.url_path, DIRDEFAULTFILE, p.extension)
					self.generate_sitemap(p.children)
				else:
					self.sitemap+='%s%s\n' % (self.base_url, p.url_path)