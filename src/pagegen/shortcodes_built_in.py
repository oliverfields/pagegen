from pagegen.utility import DIRDEFAULTFILE, appropriate_markup, generate_menu, CONTENTDIR, ASSETDIR
import hashlib
from os.path import isfile, getctime
from PIL import Image, ImageOps


def built_in_youtube(site, page, video_id, width=420, height=315):

	html = '<iframe width="420" height="315" src="https://www.youtube.com/embed/' + video_id + '"></iframe>'

	return appropriate_markup(page, html)


def built_in_figure(site, page, caption, alternative_text, src_path):
	''' Make html figure '''

	html = '<figure>\n'
	html += '<img src="' + src_path + '" alt="' + alternative_text + '">\n'
	html += '<figcaption>' + caption + '</figcaption>\n'
	html += '</figure>\n'

	return appropriate_markup(page, html)


def built_in_page_url(site, page, page_path):
	''' Return url to page, taking into account if default extension '''

	for p in site.page_list:
		if p.url_path.endswith('/'):
			url_path = p.url_path + DIRDEFAULTFILE + site.default_extension
		else:
			url_path = p.url_path

		if url_path == page_path or url_path == page_path + site.default_extension:
			return url_path

	raise Exception('No page matches "' + page_path + '"')


def built_in_integrity_hash(site, page, file_path):

	try:
		with open(file_path,"rb") as f:
			bytes = f.read() # read entire file as bytes
			file_hash = 'sha256-' + hashlib.sha256(bytes).hexdigest();
	except:
		raise Exception('Unable to generate hash for "' + file_path + '"')

	return file_hash


def built_in_menu(site, page):
	''' Generate fully recursive site menu '''
	generate_menu(site.pages, page)
	return page.menu


def built_in_image(site, page, image_source_relative, alt_attribute, image_class=None, image_size=None):
	''' Return img tag and optionally resize image using image_class settings from site.conf or image_size(XxY) argument. Maintains aspect ration by cropping with center gravity and resize to dimensions '''

	# Relative paths are relative to site_dir
	asset_dir = site.site_dir + '/' + CONTENTDIR + '/' + ASSETDIR + '/'
	if image_source_relative.startswith('/') or image_source_relative.startswith('.'):
		raise Exception('Image source path must be relative to ' + site.site_dir + ', must not start with "/" or ".": ' + image_source_relative)

	image_source_full = asset_dir + image_source_relative

	if not isfile(image_source_full):
		raise Exception('Cannot find ' + image_source_full)

	# Lookup class settings if image_class argument
	if image_class:
		image_file_name_part = image_class
		width = site.image_classes[image_class]['width']
		height = site.image_classes[image_class]['height']
	elif image_size:
		image_file_name_part = image_size
		dims = image_size.split('x')

		if len(dims) != 2:
			raise Exception('Unable to parse WidthxHeight: ' + image_size)

		width = int(dims[0])
		height = int(dims[1])
	else:
		raise Exception('Must call with either image_class or image_size arguments')

	image_target_relative = image_source_relative.replace('.', '-' + image_file_name_part + '.')
	image_target_full = site.content_dir + '/' + ASSETDIR + '/' + image_target_relative

	img_src = site.base_url + '/' + ASSETDIR + '/' + image_target_relative

	#If image already exists, check if source is newer than target, else is target has correct dimensions, failing all that then resize
	create_target = False
	if isfile(image_target_full):
		if getctime(image_target_full) < getctime(image_source_full):
			create_target = True
	else:
		create_target = True

	if create_target:
		im = Image.open(image_source_full)	
		im_new = ImageOps.fit(im, (width, height))
		im_new.save(image_target_full)

	html = '<img src="' + img_src + '" alt="' + alt_attribute + '" width="' + str(width) + '" height="' + str(height) + '" />'

	return html
