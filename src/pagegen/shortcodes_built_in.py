from pagegen.utility import DIRDEFAULTFILE, appropriate_markup, generate_menu
import hashlib


def youtube(page, video_id, width=420, height=315):

	html = '<iframe width="420" height="315" src="https://www.youtube.com/embed/' + video_id + '"></iframe>'

	return appropriate_markup(page, html)


def figure(page, caption, alternative_text, src_path):
	''' Make html figure '''

	html = '<figure>\n'
	html += '<img src="' + src_path + '" alt="' + alternative_text + '">\n'
	html += '<figcaption>' + caption + '</figcaption>\n'
	html += '</figure>\n'

	return appropriate_markup(html)


def page_url(site, page_path):
	''' Return url to page, taking into account if default extension '''

	for p in site.page_list:
		if p.url_path.endswith('/'):
			url_path = p.url_path + DIRDEFAULTFILE + site.default_extension
		else:
			url_path = p.url_path

		if url_path == page_path or url_path == page_path + site.default_extension:
			return url_path

	raise Exception('No page matches "' + page_path + '"')


def integrity_hash(file_path):

	try:
		with open(file_path,"rb") as f:
			bytes = f.read() # read entire file as bytes
			file_hash = 'sha256-' + hashlib.sha256(bytes).hexdigest();
	except:
		raise Exception('Unable to generate hash for "' + file_path + '"')

	return file_hash


def menu(pages, page):
	''' Generate fully recursive site menu '''
	generate_menu(pages, page)
	return page.menu
