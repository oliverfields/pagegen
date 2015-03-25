from Utility import report_error, load_config, SITECONF, CONFROOT, CONTENTDIR, DIRDEFAULTFILE, TARGETDIR, INCLUDEDIR, load_file, write_file, report_warning, is_default_file, SITEMAPFILE, TEMPLATEDIR
from ConfigParser import ConfigParser
from distutils.version import LooseVersion
from os.path import isdir, join, isfile, exists, islink
from os import listdir, getcwd, sep, makedirs, symlink, remove, unlink
from shutil import rmtree
from Page import Page
from docutils.core import publish_parts
from distutils.dir_util import copy_tree
from re import sub
from datetime import date


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
		self.sitemap=''
		self.exclude_sitemap=False
		self.absolute_urls=True
		self.symlink_include=False
		self.page_titles=False
		self.url_include_index=True
		self.default_extension=''

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
		except:
			pass

		try:
			self.absolute_urls=config.get(CONFROOT,'absolute_urls')
		except:
			pass

		try:
			self.default_extension=config.get(CONFROOT,'default_extension')
		except:
			pass

		try:
			self.url_include_index=config.get(CONFROOT,'url_include_index')
		except:
			pass

		try:
			self.symlink_include=config.get(CONFROOT,'symlink_include')
		except:
			pass

		try:
			self.page_titles=config.get(CONFROOT,'page_titles')
		except:
			pass

		content_path=join(self.site_dir, CONTENTDIR)
		# Try to load home page, ok if not there
		try:
			# Get home page, append it as first item
			home_page_path=self.get_dir_default_file(content_path)

			home_page=self.get_directory_page(home_page_path, False)
			self.pages.append(home_page)
		except Exception as e:
			raise Exception("Unable to find home page '%s': %s" % (DIRDEFAULTFILE, e))

		# Load pages
		try:
			self.load_pages(content_path, self.pages, home_page, self.default_extension)
		except Exception as e:
			raise Exception('Unable to load content: %s' % e)

		self.check_pages(self.pages)


	def get_directory_page(self, path, parent):
		''' Return page object set according to configuration settings '''
		if self.absolute_urls != True:
			base_url=''
		else:
			base_url=self.base_url

		if self.url_include_index != True:
			url_include_index=False
		else:
			url_include_index=True

		p=Page(path, self.site_dir, parent=parent, base_url=base_url, url_include_index=url_include_index, default_extension=self.default_extension)

		return p

	def update_place_holder(self, template, name, value):
		return template.replace('{{%s}}' % name, value)

	def generate_pages(self, pages):
		''' Recursively iterate over and generate html for pages '''
		
		for p in pages:
			if p.headers['generate html'] == True:
				try:
					page_html=load_file(join(self.site_dir, TEMPLATEDIR, p.headers['template']))
				except:
					raise Exception("Unable to load page template: '%s'" % join(self.site_dir, TEMPLATEDIR, p.headers['template']))

				page_html=self.update_place_holder(page_html, 'base_url', self.base_url)
				page_html=self.update_place_holder(page_html, 'title', p.title)

				if p.headers['description']:
					description=p.headers['description']
				else:
					description=''
				page_html=self.update_place_holder(page_html, 'description', description)

				# Page content
				if self.page_titles != False:
					underline=sub('.', '#', p.title)
					rst=p.title+'\n'+underline+'\n\n'+p.rst
				else:
					rst=p.rst

				parts=publish_parts(rst, writer_name='html', settings_overrides={'doctitle_xform':False})
				content=parts['html_body']
				page_html=self.update_place_holder(page_html, 'content', content)

				self.generate_menu(self.pages, p)
				self.generate_crumb_trail(p, p)
				page_html=self.update_place_holder(page_html, 'menu', p.menu)

				# Replace time variables year, month and day
				Y=date.today().strftime('%Y')
				M=date.today().strftime('%m')
				D=date.today().strftime('%d')
				page_html=self.update_place_holder(page_html, 'year', Y)
				page_html=self.update_place_holder(page_html, 'month', M)
				page_html=self.update_place_holder(page_html, 'day', D)

				page_html=self.update_place_holder(page_html, 'absolute_url', self.base_url+p.url_path)

				if p.crumb_trail:
					crumb_trail_html='<ul>'
					for crumb in p.crumb_trail:
						crumb_trail_html+='<li><a href="%s">%s</a></li>' % (crumb.url_path, crumb.menu_title)
					crumb_trail_html+=('</ul>')
					page_html=self.update_place_holder(page_html, 'crumb_trail', crumb_trail_html)

				p.html=page_html
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
			elif (p.target_path.endswith(SITEMAPFILE) and self.exclude_sitemap == 'False') or p.target_path==join(self.site_dir, INCLUDEDIR):
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


	def load_pages(self, dir_path, siblings, parent, default_extension):
		''' Recursively load pages from content directory '''

		file_list = listdir(dir_path)
		file_list.sort(key=LooseVersion)

		for f in file_list:
			f_path=join(dir_path, f)

			# If dir then must have default file defined
			if isdir(f_path):
				dir_page=self.get_dir_default_file(f_path)

				if dir_page:
					p=self.get_directory_page(dir_page, parent)
					siblings.append(p)
					self.load_pages(f_path, p.children, p, self.default_extension)
				else:
					report_error(1, "Directory '%s' is missing '%s' file" % (f_path, DIRDEFAULTFILE))
			elif is_default_file(f):
				pass
			elif isfile(f_path):
				if self.absolute_urls != True:
					siblings.append(Page(f_path, self.site_dir, parent=parent, default_extension=self.default_extension))
				else:
					siblings.append(Page(f_path, self.site_dir, parent=parent, base_url=self.base_url, default_extension=self.default_extension))
			else:
				raise Exception("Unknown object '%s'" % f_path)


	def move_to_target(self):
		''' Create generated site in target dir '''

		# Delete target dir if exists
		if exists(self.target_dir):
			try:
				for f in listdir(self.target_dir):
					item=join(self.target_dir, f)
					if islink(item):
						unlink(item)
					elif isdir(item):
						rmtree(item)
					else:
						remove(item)
				
			except Exception as e:
				raise Exception(e)
		else:
			try:
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
			if self.symlink_include == False:
				copy_tree(self.include_dir, include_dir)
			else:
				symlink(self.include_dir, join(TARGETDIR, INCLUDEDIR))

		# Create sitemap.txt
		write_file(join(self.target_dir, SITEMAPFILE), self.sitemap)


	def save_pages(self, pages):
		''' Create files and directories in target dir '''

		for p in pages:
			if p.parent and is_default_file(p.target_path):
				dir_path=p.target_path.rpartition(sep)[0]
				makedirs(dir_path)
				write_file(p.target_path, p.html)
				if p.children:
					self.save_pages(p.children)
			else:
				write_file(p.target_path, p.html)


	def generate_crumb_trail(self, crumb_trail_page, page):
		# page.parent.parent checks for home page, don't want that in trail
		if page.parent:
			crumb_trail_page.crumb_trail.insert(0, page.parent)
			self.generate_crumb_trail(crumb_trail_page, page.parent)
		# Add current page
		if page==crumb_trail_page:
			crumb_trail_page.crumb_trail.append(page)


	def generate_menu(self, pages, page, level=1):

		if page.menu == '':
			page.menu='<ul>'

		for p in pages:

			if p.headers['menu exclude'] == 'True':
				continue

			if p == page:
				css_class=' class="selected_page"'
			else:
				css_class=''

			if p.children:
				page.menu+='<li><a href="%s"%s>%s</a>' % (p.url_path, css_class, p.menu_title)
				page.menu+='<ul>'
				self.generate_menu(p.children, page, level=level+1)
				page.menu+='</ul>'
				page.menu+='</li>'
			else:
				page.menu+='<li><a href="%s"%s>%s</a></li>' % (p.url_path, css_class, p.menu_title)

		if level==1:
			if page.menu=='<ul>':
				page.menu=''
			else:
				page.menu+='</ul>'


	def generate_sitemap(self, pages):
		''' Create sitmap.txt '''
		for p in pages:
			if p.headers['sitemap exclude'] == False:
				if p.children or p.url_path == '/':
					if self.url_include_index != True:
						self.sitemap+='%s%s\n' % (self.base_url, p.url_path.rstrip('/'))
					else:
						self.sitemap+='%s%s%s%s\n' % (self.base_url, p.url_path, DIRDEFAULTFILE, p.extension)
					self.generate_sitemap(p.children)
				else:
					self.sitemap+='%s%s\n' % (self.base_url, p.url_path)