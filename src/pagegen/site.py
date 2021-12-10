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

from pagegen.utility import report_error, load_config, SITECONF, CONFROOT, CONTENTDIR, DIRDEFAULTFILE, TARGETDIR, INCLUDEDIR, load_file, write_file, report_warning, is_default_file, SITEMAPFILE, SITEMAPTXTFILE, TEMPLATEDIR, exec_hook, HOOKDIR, DATEFORMAT, report_notice, RSSFEEDFILE, NEWLINE, urlify, get_first_words, relative_path, SEARCHINDEXFILE, STOPWORDSFILE, load_template
from configparser import ConfigParser
from distutils.version import LooseVersion
from os.path import isdir, join, isfile, exists, islink
from os import listdir, sep, makedirs, symlink, remove, unlink
from shutil import rmtree
from pagegen.page import page
from pagegen.virtualpage import virtualpage
from docutils.core import publish_parts
from distutils.dir_util import copy_tree
from re import sub, search
from datetime import date
from datetime import datetime
from operator import itemgetter
from pagegen.searchindex import searchindex
from pagegen.upload import upload


class site:
	""" Master object """

	def __init__(self, site_dir, config_file, environment):
		self.pages=[]
		self.site_dir=''
		self.base_url=''
		self.menu_changed=False
		self.omit_menu=False
		self.ignore=[]
		self.home_menu_name=''
		self.sitemap=''
		self.sitemaptxt=''
		self.exclude_sitemap=False
		self.absolute_urls=True
		self.symlink_include=False
		self.page_titles=False
		self.url_include_index=True
		self.default_extension=''
		self.title_warn_min=0
		self.title_warn_max=0
		self.description_warn_min=0
		self.description_warn_max=0
		self.link_sequence=[]
		self.include_rss=False
		self.rss_sequence=[]
		self.max_rss_items=15
		self.rss_title=''
		self.rss_description=''
		self.rss=''
		self.tags={}
		self.tag_dir='tag'
		self.tag_title='Tags'
		self.categories={}
		self.category_dir='category'
		self.category_title='Categories'
		self.include_search=False
		self.search_index=SearchIndex(join(site_dir, STOPWORDSFILE))
		self.search_xpaths=[]
		self.environment=environment
		self.deploy_mode=None
		self.ftp_host=None
		self.ftp_username=None
		self.ftp_password=None
		self.ftp_target_directory=None
		#self.ftp_directory_permissions=None
		#self.ftp_file_permissions=None

		if isdir(site_dir):
			self.site_dir=site_dir
			self.include_dir=join(site_dir, INCLUDEDIR)
			self.CONTENTDIR=join(site_dir, CONTENTDIR)
		else:
			raise Exception("Site dir '%s' is not a directory" % site_dir)

		try:
			config=load_config([config_file], add_dummy_section=False)
		except Exception as e:
			raise Exception("Unable to load site config '%s': %s" % e)

		# If no section supplied, look for first section containing default_section=True
		if self.environment == None:
			if len(config.sections()) == 1:
				default_environment=config.sections()[0]
			else:
				default_environment=None
				for section in config.sections():
					try:
						# If true then we have our environment
						config.get(section,'default_environment')
						default_environment=section
						break

					except Exception as e:
						pass

			# No default env set, exit
			if default_environment==None:
				report_error(1,"No environment specified from command arguments (-e or --environment) and no default_environment setting found in '%s'" % config_file)
			else:
				self.environment=default_environment

		# Set target dir based on environment
		self.target_dir=join(site_dir, TARGETDIR, self.environment)


		try:
			self.base_url=config.get(self.environment,'base_url')
		except:
			raise Exception('%s must contain base_url setting' % SITECONF)


		try:
			self.exclude_sitemap=config.get(self.environment,'exclude_sitemap')
		except:
			pass

		try:
			self.tag_dir=config.get(self.environment,'tag_url')
		except:
			pass

		try:
			self.tag_title=config.get(self.environment,'tag_title')
		except:
			pass

		try:
			self.category_dir=config.get(self.environment,'category_url')
		except:
			pass

		try:
			self.category_title=config.get(self.environment,'category_title')
		except:
			pass


		try:
			self.include_rss=config.get(self.environment,'include_rss')
		except:
			pass

		if self.include_rss != False:
			try:
				self.rss_title=config.get(self.environment,'rss_title')
			except:
				pass

			try:
				self.rss_description=config.get(self.environment,'rss_description')
			except:
				pass

		try:
			self.max_rss_items=int(config.get(self.environment,'max_rss_items'))
		except:
			pass

		try:
			self.absolute_urls=config.get(self.environment,'absolute_urls')
		except:
			pass

		try:
			title_length_range=config.get(self.environment,'title_length_range').split('-')
			min=int(title_length_range[0])
			max=int(title_length_range[1])

			if min < max:
				self.title_warn_min=min
				self.title_warn_max=max
		except:
			pass

		try:
			description_length_range=config.get(self.environment,'description_length_range').split('-')
			min=int(description_length_range[0])
			max=int(description_length_range[1])

			if min < max:
				self.description_warn_min=min
				self.description_warn_max=max
		except:
			pass

		try:
			self.default_extension=config.get(self.environment,'default_extension')
		except:
			pass

		try:
			self.url_include_index=config.get(self.environment,'url_include_index')
		except:
			pass

		try:
			self.symlink_include=config.get(self.environment,'symlink_include')
		except:
			pass

		try:
			self.page_titles=config.get(self.environment,'page_titles')
		except:
			pass

		try:
			self.include_search=config.get(self.environment,'include_search')
		except:
			pass

		try:
			xpaths=config.get(self.environment,'search_xpaths').split(',')
			for xpath in xpaths:
				self.search_index.index_xpaths.append(xpath)
		except:
			self.search_index.index_xpaths.append('/html/body')

		try:
			self.deploy_mode=config.get(self.environment, 'deploy_mode')
		except:
			pass

		if self.deploy_mode == 'ftp':
			try:
				self.ftp_host=config.get(self.environment, 'ftp_host')
				self.ftp_username=config.get(self.environment, 'ftp_username')
				self.ftp_password=config.get(self.environment, 'ftp_password')
				self.ftp_target_directory=config.get(self.environment, 'ftp_target_directory')
				#self.ftp_directory_permissions=config.get(self.environment, 'ftp_directory_permissions')
				#self.ftp_file_permissions=config.get(self.environment, 'ftp_file_permissions')
			except:
				report_error(1,'Unable to load ftp settings')


	def prepare(self):
		''' Prepare site for generation '''

		content_path=join(self.site_dir, CONTENTDIR)

		# Try to load home page, ok if not there
		try:
			# Get home page, append it as first item
			home_page_path=self.get_dir_default_file(content_path)
			home_page=self.get_directory_page(home_page_path, False)

			if self.publish_page(home_page):
				self.pages.append(home_page)
			else:
				report_error(1, "Home page not publishable because publish date not reached yet '%s': %s" % (home_page.headers['publish'], relative_path(home_page.source_path)))
		except Exception as e:
			raise Exception("Unable to find home page '%s': %s" % (DIRDEFAULTFILE, e))

		# Load pages
		try:
			self.load_pages(content_path.decode('utf-8'), self.pages, home_page, self.default_extension)
		except Exception as e:
			raise Exception('Unable to load content: %s' % e)


		self.set_tags(self.pages)
		self.set_categories(self.pages)
		if self.tags:
			self.load_list_pages('tag', home_page)
		if self.categories:
			self.load_list_pages('category', home_page)

		self.check_pages(self.pages)
		self.set_link_sequence(self.pages)
		self.set_next_previous_links()


	def get_url(self, url):
		''' Return relative of absolute url depending on config setting '''

		if self.absolute_urls == True:
			url=self.base_url+url

		return url


	def html_tag_list(self):
		''' Generate html list of tags'''

		html='<div id="tags"><h1>%s</h1><ul>' % self.tag_title

		for tag, pages in self.tags.iteritems():
			url='/'+self.tag_dir+'/'+urlify(tag)+self.default_extension
			url=self.get_url(url)
			html+='<li><a href="%s">%s</a>' % (url, tag)

		html+='</ul>'

		return html


	def html_category_list(self):
		''' Generate html list of categories'''

		html='<div id="categories"><h1>%s</h1><ul>' % self.category_title

		for c, page in self.categories.iteritems():
			url='/'+self.category_dir+'/'+urlify(c)+self.default_extension
			url=self.get_url(url)
			html+='<li><a href="%s">%s</a>' % (url, c)

		html+='</ul>'

		return html


	def html_page_tag_list(self, tags):
		''' Generate list of tags for a page '''

		if len(tags) == 0:
			return ''

		html='<ul id="page_tags">'

		for tag in tags:
			url='/'+self.tag_dir+'/'+urlify(tag)+self.default_extension
			url=self.get_url(url)
			html+='<li><a href="%s">%s</a>' % (url, tag)

		html+='</ul>'

		return html


	def html_page_category(self, category):
		''' Generate link to category for a page '''

		if category is None:
			return ''

		url='/'+self.category_dir+'/'+urlify(category)+self.default_extension
		url=self.get_url(url)

		return '<a href="%s">%s</a>' % (url, category)

	def html_sub_menu(self, page):
		''' Return list of page child elements '''

		if not page.children:
			return ''
		else:
			html='<ul class="sub_menu">'

			for p in page.children:
				html+='<li><a href="%s">%s</a></li>' % (p.url_path, p.menu_title)

			html += '</ul>'

			return html


	def generate_page_indexes(self, pages):
		''' Index all pages with header no index=True '''
		for p in pages:
			if p.headers['search index exclude'] == False:
				if p.headers['description'] != None:
					description=p.headers['description']
				else:
					description=''
				self.search_index.index_file(p.target_path, p.url_path, p.title, get_first_words(description, 150))
			if p.children:
				self.generate_page_indexes(p.children)


	def generate_search_index(self):
		''' For all indexable files get their terms and create json index file for site search use (requires javascript '''
		si=SearchIndex()
		self.generate_page_indexes(self.pages)
		write_file(join(self.target_dir, SEARCHINDEXFILE), self.search_index.build_json_index())


	def load_list_pages(self, type, parent_page):
		''' For each tag, create page objects and replace their content with list of tagged pages. and index page, which is list of tags. Type can be tag or category '''

		if type == 'tag':
			title=self.tag_title
			dir=self.tag_dir
			items=self.tags.iteritems()
		else:
			title=self.category_title
			dir=self.category_dir
			items=self.categories.iteritems()

		# Create top level overview page (o)
		o=virtualpage()
		o.headers['sitemap exclude']=True
		o.headers['menu exclude']=True
		o.headers['link chain exclude']=True
		o.parent=parent_page
		o.title=title
		o.menu_title=title
		o.target_path=self.environment+'/'+dir+'/'+DIRDEFAULTFILE+self.default_extension
		o.url_path='/'+dir+'/'+DIRDEFAULTFILE+self.default_extension

		o.url_path=self.get_url(o.url_path)

		# Create each list page (l)
		for item, pages in items:
			l=virtualpage()
			l.headers['sitemap exclude']=True
			l.headers['menu exclude']=True
			l.headers['link chain exclude']=True
			l.title=item.capitalize()
			l.menu_title=item.capitalize()
			l.target_path=self.environment+'/'+dir+'/'+urlify(item)+self.default_extension
			l.url_path='/'+dir+'/'+urlify(item)+self.default_extension
			l.parent=o
			
			l.url_path=self.get_url(l.url_path)

			for p in pages:
				l.rst+='* %s `%s <%s>`_ %s%s' % (p.headers['publish'], p.menu_title, p.url_path, p.headers['description'], NEWLINE)

			o.children.append(l)

		# Create tag overview content now so get right urls etc
		for p in o.children:
			o.rst+='* `%s <%s>`_%s' % (p.menu_title, p.url_path, NEWLINE)

		self.pages.append(o)


	def set_tags(self, pages):
		''' Get all tags that are defined in page headers '''

		for p in pages:
			if len(p.headers['tags']):

				for t in p.headers['tags']:
					# If tag not existing, create tag list
					if not t in self.tags.keys():
						self.tags[t]=[]
					self.tags[t].append(p)

			if p.children or p.url_path == '/':
				self.set_tags(p.children)


	def set_categories(self, pages):
		''' Get all categories that are defined in page headers '''

		for p in pages:
			if p.headers['category']:

				# If Category not existing, create category list
				if not p.headers['category'] in self.categories.keys():
					self.categories[p.headers['category']]=[]
				self.categories[p.headers['category']].append(p)

				if p.children or p.url_path == '/':
					self.set_categories(p.children)


	def set_next_previous_links(self):
		''' Add previous and next links to pages according to thier link sequence '''

		previous=False

		for i, p in enumerate(self.link_sequence):

			try:
				next=self.link_sequence[i+1]
			except:
				next=False

			p.previous_page=previous
			p.next_page=next

			previous=p


	def set_link_sequence(self, pages):
		''' Add all pages to link sequence (for use with previous/next links) '''
		for p in pages:
			if p.headers['link chain exclude'] == False:
				self.link_sequence.append(p)
				if p.children:
					self.set_link_sequence(p.children)


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

		p=Page()

		p.load(path, self.site_dir, self.environment, parent=parent, base_url=base_url, url_include_index=url_include_index, default_extension=self.default_extension)

		return p

	def update_place_holder(self, template, name, value):

		result = template.replace('{{%s}}' % name, value)
		try:

			result = template.replace('{{%s}}' % name, value)
		except Exception as e:
			raise Exception("Unable to update name '%s' with value '%s'" % (name, value))

		return result

	def generate_pages(self, pages):
		''' Recursively iterate over and generate html for pages '''

		for p in pages:

			# Set environment variable for hooks
			# Seems to require 
			p.hook_environment={
				'PAGEGEN_SITE_DIR': self.site_dir,
				'PAGEGEN_SOURCE_DIR': join(self.site_dir, CONTENTDIR),
				'PAGEGEN_TARGET_DIR': self.target_dir,
				'PAGEGEN_HOOK_DIR': join(self.site_dir, HOOKDIR),
				'PAGEGEN_BASE_URL': self.base_url,
				'PAGEGEN_PAGE_TITLE': p.title,
				'PAGEGEN_PAGE_URL': p.url_path,
				'PAGEGEN_PAGE_SOURCE_PATH': p.source_path,
				'PAGEGEN_PAGE_TARGET_PATH': p.target_path,
				'PAGEGEN_ENVIRONMENT': self.environment,
				'PAGEGEN_HOOK': 'pre_generate_page'
			}

			# Run hook
			exec_hook(join(self.site_dir,HOOKDIR,'pre_generate_page'), p.hook_environment)

			if p.headers['generate html'] == True:
				try:
					page_html = load_template(join(self.site_dir, TEMPLATEDIR, p.headers['template']))
				except Exception as e:
					raise Exception("Unable to load page template: '%s': %s" % (join(self.site_dir, TEMPLATEDIR, p.headers['template']), e))

				page_html=self.update_place_holder(page_html, 'base_url', self.base_url)
				page_html=self.update_place_holder(page_html, 'title', p.title)
				page_html=self.update_place_holder(page_html, 'publish', p.headers['publish'])

				if p.headers['description']:
					description=p.headers['description']
				else:
					description=''
				page_html=self.update_place_holder(page_html, 'description', description)
				page_html=self.update_place_holder(page_html, 'page_tags', self.html_page_tag_list(p.headers['tags']))
				page_html=self.update_place_holder(page_html, 'page_category', self.html_page_category(p.headers['category']))
				page_html=self.update_place_holder(page_html, 'tags', self.html_tag_list())
				page_html=self.update_place_holder(page_html, 'categories', self.html_category_list())
				page_html=self.update_place_holder(page_html, 'sub_menu', self.html_sub_menu(p))

				# Page content
				if self.page_titles != False:
					underline=sub('.', '#', p.title)
					rst=p.title+'\n'+underline+'\n\n'+p.rst
				else:
					rst=p.rst

				# Previous and next links
				if p.previous_page is False:
					page_html=self.update_place_holder(page_html, 'previous_link', '')
				else:
					page_html=self.update_place_holder(page_html, 'previous_link', '<a href="%s">%s</a>' % (p.previous_page.url_path, p.previous_page.menu_title))

				if p.next_page is False:
					page_html=self.update_place_holder(page_html, 'next_link', '')
				else:
					page_html=self.update_place_holder(page_html, 'next_link', '<a href="%s">%s</a>' % (p.next_page.url_path, p.next_page.menu_title))

				try:
					#overrides = {'input_encoding': 'utf-8', 'output_encoding': 'unicode','doctitle_xform': False}
					overrides = {'doctitle_xform': False}
					parts = publish_parts(rst, writer_name='html', settings_overrides=overrides)
				except:
					raise(Exception('docutils.publish_parts failed'))

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

			# Check title length if range set
			if self.title_warn_min > 0 and self.title_warn_max > 0:
				if self.title_warn_min > len(p.title):
					report_warning("Title too short '%s' (%s), minimum length %s characters: '%s'" % (p.title, len(p.title), self.title_warn_min, relative_path(p.source_path)))
				elif self.title_warn_max < len(p.title):
					report_warning("Title too long '%s' (%s), maximum length %s characters: '%s'" % (p.title, len(p.title), self.title_warn_max, relative_path(p.source_path)))

			# Check description length if range set
			if self.description_warn_min > 0 and self.description_warn_max > 0:
				if  p.headers['description'] is None:
					report_warning("Missing description '%s'" % relative_path(p.source_path))
				elif self.description_warn_min > len(p.headers['description']):
					report_warning("Description too short '%s' (%s), minimum lenght %s characters: '%s'" % (p.headers['description'], len(p.headers['description']), self.description_warn_min, relative_path(p.source_path)))
				elif self.description_warn_max < len(p.headers['description']):
					report_warning("Description too long '%s' (%s), maximum lenght %s characters: '%s'" % (p.headers['description'], len(p.headers['description']), self.description_warn_max, relative_path(p.source_path)))

			if p.target_path in page_target_paths:
				report_error(1,"Target path '%s' for page '%s' is already set for '%s'" % (relative_path(p.target_path), relative_path(p.source_path), relative_path(page_target_paths[p.target_path])))
			# TODO Better checking than ends with
			elif ((p.target_path.endswith(SITEMAPFILE) or p.target_path.endswith(SITEMAPTXTFILE)) and self.exclude_sitemap == 'False') or p.target_path==join(self.site_dir, INCLUDEDIR):
				report_error(1,"Page '%s' illegal name, cannot be either '%s' or '%s'" % (relative_path(p.source_path), SITEMAPFILE, SITEMAPTXTFILE))
			elif p.target_path.endswith(RSSFEEDFILE) and self.include_rss != False:
				report_error(1,"Page '%s' illegal name '%s'" % (relative_path(p.source_path), RSSFEEDFILE))
			elif p.target_path.endswith(SEARCHINDEXFILE) and self.include_search != False:
				report_error(1,"Page '%s' illegal name '%s'" % (relative_path(p.source_path), SEARCHINDEXFILE))

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
					if self.publish_page(p):
						siblings.append(p)
						try:
							self.load_pages(f_path, p.children, p, self.default_extension)
						except Exception as e:
							raise Exception('Unable to load pages for %s: %s' % (f, e))
				else:
					report_error(1, "Directory '%s' is missing '%s' file" % (f_path, DIRDEFAULTFILE))
			elif is_default_file(f):
				pass
			elif isfile(f_path):
				if self.absolute_urls != True:
					p=Page()
					p.load(f_path, self.site_dir, self.environment, parent=parent, default_extension=self.default_extension)
				else:
					p=Page()
					p.load(f_path, self.site_dir, self.environment, parent=parent, base_url=self.base_url, default_extension=self.default_extension)

				if self.publish_page(p):
					siblings.append(p)
			else:
				raise Exception("Unknown object '%s'" % f_path)


	def publish_page(self, page):
		''' If page publish header date is today or in past return true. Pagegen dates are always strings, so need to convert '''

		try:
			page_publish_date=datetime.strptime(page.headers['publish'], DATEFORMAT)
		except Exception as e:
			report_error(1, "Unable to parse date '%s': %s: %s" % (page.headers['publish'], relative_path(page.source_path), e))

		publish=page_publish_date < datetime.now()

		if publish is False:
			report_notice("Not publishing '%s' (or any child pages) until '%s': %s" % (page.title, page.headers['publish'], relative_path(page.source_path)))

		return publish

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
				symlink(self.include_dir, join(self.target_dir, INCLUDEDIR))

		# Create sitemap
		if self.exclude_sitemap == False:
			write_file(join(self.target_dir, SITEMAPFILE), self.sitemap)
			write_file(join(self.target_dir, SITEMAPTXTFILE), self.sitemaptxt)

		# Create rss feed
		if self.include_rss != False:
			write_file(join(self.target_dir, RSSFEEDFILE), self.rss)

		if self.include_search != False:
			self.generate_search_index()


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

			p.hook_environment['PAGEGEN_HOOK']='post_generate_page'
			exec_hook(join(self.site_dir,HOOKDIR,'post_generate_page'), p.hook_environment)


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

			if p.headers['menu exclude'] != False:
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


	def sitemap_url(self, page):
		url='<url><loc>%s%s</loc>' % (self.base_url, page.url_path.rstrip('/'))

		# Add lastmod if set
		if page.headers['sitemap lastmod']:
			try:
				date=datetime.strptime(page.headers['sitemap lastmod'], '%Y-%m-%d')
				url+='<lastmod>%s</lastmod>' % date.strftime('%Y-%m-%d')
			except:
				report_warning("Page header sitemap lastmod '%s' does not seem to be valid date: %s" % (page.headers['sitemap lastmod'], relative_path(page.source_path)))


		# Add change freq if set
		if page.headers['sitemap changefreq'] != None:
			valid_changefreq='always hourly daily weekly monthly yearly never'
			if page.headers['sitemap changefreq'] in valid_changefreq:
				url+='<changefreq>%s</changefreq>' % page.headers['sitemap changefreq']
			else:
				report_warning("Page header sitemap changefreq '%s' does not seem to be valid (%s): %s" % (page.headers['sitemap changefreq'], valid_changefreq, relative_path(page.source_path)))

		# Add priority
		if page.headers['sitemap priority'] != None:
			if search(r'^0.[0-9]*$', page.headers['sitemap priority']) or search(r'^1.0*$', page.headers['sitemap priority']):
				url+='<priority>%s</priority>' % page.headers['sitemap priority']
			else:
				report_warning("Page header sitemap priority '%s' does not seem to be valid, must be valur between 0.0 and 1.0 : %s" % (page.headers['sitemap priority'], relative_path(page.source_path)))

		url+='</url>'

		return url

	def generate_sitemap_urls(self, pages):
		''' Create sitmap.txt '''
		for p in pages:
			if p.headers['sitemap exclude'] == False:
				if p.children or p.url_path == '/':
					self.sitemap+=self.sitemap_url(p)
					self.sitemaptxt += self.base_url + p.url_path.rstrip('/') + '\n'

					self.generate_sitemap_urls(p.children)
				else:
					self.sitemap+=self.sitemap_url(p)
					self.sitemaptxt += self.base_url + p.url_path + '\n'


	def generate_sitemap(self, pages):

		self.sitemap='<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">'

		self.generate_sitemap_urls(pages)

		self.sitemap+='</urlset>'


	def generate_rss(self):
		''' Create rss feed '''

		self.create_rss_sequence(self.pages)

		# Sort rss pages by header publish value
		self.rss_sequence=sorted(self.rss_sequence, key=lambda k: k.headers['publish'], reverse=True) 

		self.rss='<?xml version="1.0" encoding="UTF-8" ?>'+NEWLINE
		self.rss+='<rss version="2.0">'+NEWLINE
		self.rss+='<channel>'+NEWLINE
		self.rss+='<title>'+self.rss_title+'</title>'+NEWLINE
		self.rss+='<link>'+self.base_url+'/'+RSSFEEDFILE+'</link>'+NEWLINE
		self.rss+='<description>'+self.rss_description+'</description>'+NEWLINE
		self.rss+='<generator>Pagegen - pagegen.phnd.net</generator>'+NEWLINE

		count=1
		for p in self.rss_sequence:

			try:
				page_publish_date=datetime.strptime(p.headers['publish'], DATEFORMAT)
			except Exception as e:
				report_error(1, "Unable to parse date '%s': %s: %s" % (p.headers['publish'], relative_path(p.source_path), e))

			self.rss+='<item>'+NEWLINE
			self.rss+='<title>'+p.title+'</title>'+NEWLINE
			self.rss+='<link>'+self.base_url+p.url_path+'</link>'+NEWLINE
			self.rss+='<pubDate>'+page_publish_date.strftime('%a, %d %b %Y')+' 00:00:00 +0000</pubDate>'+NEWLINE
			if p.headers['description'] != None:
				self.rss+='<description>'+p.headers['description']+'</description>'+NEWLINE
			self.rss+='</item>'+NEWLINE

			count+=1

			if count > self.max_rss_items:
				break

		self.rss+='</channel>'+NEWLINE
		self.rss+='</rss>'+NEWLINE


	def create_rss_sequence(self, pages):
		''' Get all pages with header rss include True '''
		for p in pages:
			if p.headers['rss include'] != False:
				self.rss_sequence.append(p)
				if p.children or p.url_path == '/':
					self.create_rss_sequence(p.children)


	def ftp_upload(self):
		''' Upload to ftp '''

		u = Upload()

		u.ftp_upload(
			self.target_dir,
			{
				'ftp_host': self.ftp_host,
				'ftp_username': self.ftp_username,
				'ftp_password': self.ftp_password,
				'ftp_target_directory': self.ftp_target_directory
			}
		)
