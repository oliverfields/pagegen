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

from pagegen.utility import DEFAULTPAGETEMPLATE, DATEFORMAT
from datetime import date

class virtualpage:
	''' Basic page class '''

	def __init__(self):
		self.url_path='',
		self.children=[]
		self.rst=''
		self.title=''
		self.source_path=''
		self.target_path=''
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
		}


	def generate_crumb_trail(self):
		html=''
		for p in self.crumb_trail:
			html+=' > %s' % p.title
		return html
