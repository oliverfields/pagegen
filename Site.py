from Utility import report_error, load_config, SITECONF, CONFROOT, CONTENT_DIR, DIRDEFAULTFILE
from ConfigParser import ConfigParser
from distutils.version import LooseVersion
from os.path import isdir, join, isfile
from os import listdir
from Page import Page

class Site:
	""" Master object """

	def __init__(self, site_dir, config_file):
		self.pages=[]
		self.site_dir=''
		self.base_url=''
		self.menu_changed=False
		self.generate_sitemap=True
		self.omit_menu=False
		self.ignore=[]
		self.home_menu_name=''

		if isdir(site_dir):
			self.site_dir=site_dir
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


		# Load pages
		try:
			content_path=join(self.site_dir, CONTENT_DIR)
			front_page=Page(join(content_path, DIRDEFAULTFILE))
			self.pages.append(front_page)
			self.load_pages(content_path, self.pages)
		except Exception as e:
			raise Exception('Unable to load content: %s' % e)

		self.check_pages(self.pages)


	def menu_changed(self):
		''' Check if need to rebuild menu (is so all pages must be rebuilt because menu used in all pages '''

		#Check all pages, if one has .menu_change = True then set site.menu_changed=True
		pass


	def check_pages(self, page):
		''' Check all files are uniquely named (because of xxx_ prefix potentially can have conflicts, cannot have files called e.g. robots.txt or sitemap.xml) '''
		for p in page:
			print p.source_path
			if p.children:
				self.check_pages(p.children)


	def load_pages(self, dir_path, parent):
		''' Recursively load pages from content directory '''

		file_list = listdir(dir_path)
		file_list.sort(key=LooseVersion)

		for f in file_list:
			f_path=join(dir_path, f)

			# If dir then must have default file defined
			if isdir(f_path):
				dir_page=join(f_path, DIRDEFAULTFILE)
				if isfile(dir_page):
					p=Page(dir_page)
					parent.append(p)
					self.load_pages(f_path, p.children)
				else:
					report_error(1, "Directory '%s' is missing '%s'" % (f_path, dir_page))
			elif f == DIRDEFAULTFILE:
				pass
			elif isfile(f_path):
				parent.append(Page(f_path))
			else:
				raise Exception("Unknown object '%s'" % f_path)
			#if os.path.isdir(package_path):

