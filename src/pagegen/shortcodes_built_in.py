from pagegen.utility import DIRDEFAULTFILE
import hashlib
 

def figure(page, caption, alternative_text, src_path):
	''' Make html figure '''

	if page.markup == 'rst':
		html_prefix = '.. raw:: html\n\n\t'
		indent = '\t'
	else: # Markdown
		html_prefix = ''
		indent = ''

	html = html_prefix + '<figure>\n'
	html += indent + '<img src="' + src_path + '" alt="' + alternative_text + '">\n'
	html += indent + '<figcaption>' + caption + '</figcaption>\n'
	html += indent + '</figure>\n'

	return html


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
