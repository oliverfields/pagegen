from pagegen.utility import appropriate_markup, generate_menu
from pagegen.constants import DIRDEFAULTFILE, CONTENTDIR, ASSETDIR
from os.path import isfile, getctime
from os import makedirs
from PIL import Image, ImageOps
from hashlib import md5


def built_in_page_url(site, page, page_path):
    """Return url to page, taking into account if default extension."""

    for p in site.page_list:
        if p.url_path.endswith('/'):
            url_path = p.url_path + DIRDEFAULTFILE + site.default_extension
        else:
            url_path = p.url_path

        if url_path == page_path or url_path == page_path + site.default_extension:
            return url_path

    raise Exception('No page matches "' + page_path + '"')


def built_in_menu(site, page):
    """Generate fully recursive site menu"""
    generate_menu(site.pages, page)
    return page.menu


def built_in_image(site, page, image_source, alt_attribute, target_dir=None, image_class=None, image_size=None):
    """Return img tag and optionally resize image using image_class settings from site.conf or image_size(XxY) argument. Maintains aspect ratio by cropping with center gravity and resize to dimensions"""

    resize = False

    # Path cannot start with .
    if image_source.startswith('.'):
        raise Exception('Image source cannot start with .')

    # If path is relative, prefix with site_dir
    if not image_source.startswith('/'):
        image_source = site.site_dir + '/' + image_source

    # Check source image exists
    if not isfile(image_source):
        raise Exception('No file: ' + image_source)

    t = image_source.rpartition('/')
    source_dir = t[0]
    source_file = t[2]

    # Target dir defults to assets
    if target_dir is None:
        target_dir = site.asset_dir
    else:
        # Target dir cannot start with .
        if target_dir.startswith('.'):
            raise Exception('target_dir cannot start with .')

        # Target_dir is always relative to asset dir
        if target_dir.startswith('/'):
            target_dir = site.asset_dir + target_dir
        else:
            target_dir = site.asset_dir + '/' + target_dir

    # Lookup class settings if image_class argument
    if image_class:
        width = site.image_classes[image_class]['width']
        height = site.image_classes[image_class]['height']
        target_file = source_file.replace('.', '_' + image_class + '.')
        resize = True
    elif image_size:
        dims = image_size.split('x')
        target_file = source_file.replace('.', '-' + image_size + '.')

        if len(dims) != 2:
            raise Exception('Unable to parse WidthxHeight: ' + image_size)

        width = int(dims[0])
        height = int(dims[1])
        resize = True
    else:
        target_file = source_file
        resize = False

    # Image src
    length_content_dir_path = len(site.site_dir + '/' + CONTENTDIR)
    img_src = site.base_url + target_dir[length_content_dir_path:] + '/' + target_file

    # Create target dir if needed
    makedirs(target_dir, exist_ok=True)

    target_file_path = target_dir + '/' + target_file

    #If image already exists, check if source is newer than target, else is target has correct dimensions, failing all that then resize
    create_target = False
    if isfile(target_file_path):
        if getctime(target_file_path) < getctime(image_source):
            create_target = True
    else:
        create_target = True

    if create_target:
        im = Image.open(image_source)

        # Rotate if specified in exif
        exif = im._getexif()
        ORIENTATION = 274
        if exif is not None and ORIENTATION in exif:
            orientation = exif[ORIENTATION]
            method = {2: Image.FLIP_LEFT_RIGHT, 4: Image.FLIP_TOP_BOTTOM, 8: Image.ROTATE_90, 3: Image.ROTATE_180, 6: Image.ROTATE_270, 5: Image.TRANSPOSE, 7: Image.TRANSVERSE}
            if orientation in method:
                im = im.transpose(method[orientation])

        im.thumbnail((width, height), Image.ANTIALIAS)
        im.save(target_file_path)
    else:
        im = Image.open(target_file_path)

    img_width, img_height = im.size

    html = '<img src="' + img_src + '" alt="' + alt_attribute + '" width="' + str(img_width) + '" height="' + str(img_height) + '" />'

    return appropriate_markup(page, html)


def built_in_list_posts(site, page, posts_dir, max_posts_limit):
    """List posts found in posts_dir"""

    html = ''
    posts = []
    counter = 0

    if not isinstance(max_posts_limit, int):
        max_posts_limit = int(max_posts_limit)

    # Strip leading / if present
    if posts_dir.startswith('/'):
        posts_dir = posts_dir[1:]

    for p in site.page_list:
        if p.source_path.startswith(site.content_dir + '/' + posts_dir):
            posts.append(p)

    if len(posts) == 0:
        return 'No posts yet..'

    sorted_posts = sorted(posts, key=lambda d: d.headers['publish'], reverse=True)

    for p in sorted_posts:
        counter += 1

        if counter == max_posts_limit:
            break

        if p.excerpt:
            excerpt = '<br />' + p.excerpt
        else:
            excerpt = ''

        html += '<li>' + p.headers['publish'] + ' <a href="' + p.url_path + '">' + p.title + '</a>' + excerpt + '</li>'

    return appropriate_markup(page, '<ol>' + html + '</ol>')


def built_in_tags(site, page):
    """List page tags"""

    html = ''
    if 'tags' in page.headers.keys():
        for t in page.headers['tags']:
            html += '<li><a href="' + site.tags[t]['url'] + '">' + t + '</a></li>'

    return appropriate_markup(page, '<ol>' + html + '</ol>')


def built_in_list_authors(site, page):
    """List authors"""

    for author in page.authors:
        if 'name' in author.keys():
            name = author['name']
        else:
            name = author['id']

        html = '<li><a href="' + author['author_page'] + '">' + name + '</a></li>'

    html = '<ol>' + html + '</ol>'

    return appropriate_markup(page, html)


def built_in_quote(site, page, quote, by=False):
    """ Add a quote markup """

    html = '<div class="quote"><q class="quote-text">' + quote + '</q>'

    if by:
        html += '<div class="quote-by">— ' + by + '</div>'

    html += '</div>'

    return appropriate_markup(page, html)


