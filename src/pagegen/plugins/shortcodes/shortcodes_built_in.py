from os.path import isfile, join, sep, getmtime
from os import makedirs
from PIL import Image
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)


def built_in_quote(site, page, quote, by=False):
    '''
    Add a quote markup
    '''

    html = '<div class="quote"><q class="quote-text">' + quote + '</q>'

    if by:
        html += '<div class="quote-by">— ' + by + '</div>'

    html += '</div>'

    return html


def built_in_image(site, page, image_source, alt_attribute, image_class=None, image_size=None):
    '''
    Return img tag and optionally create resized copy of image in assets dir using image_class settings from site.conf or image_size(XxY) argument. Maintains aspect ratio by cropping with center gravity and resize to dimensions
    '''

    resize = False

    image_source = join(site.asset_source_dir, image_source)

    t = image_source.rpartition('/')
    source_dir = t[0]
    source_file = t[2]

    try:
        sc_cache = site.plugins['shortcodes'].cache
    except AttributeError:
        site.plugins['shortcodes'].cache = {}
        sc_cache = site.plugins['shortcodes'].cache

    # Lookup class settings if image_class argument
    if image_class:
        # See if we have this cached
        try:
            nd = sc_cache['named_dimensions']
        except KeyError:
            nd = sc_cache['named_dimensions'] = {}

        try:
            ic = nd[image_class]
        except KeyError:
            ic = nd[image_class] = {}

        try:
            width = ic['width']
            height = ic['height']
        except KeyError:
            logger.debug('Loading image_named_dimensions settings to cache')
            # Add named dims to cache
            try:
                for i_class in site.conf['shortcodes']['image_named_dimensions'].split(','):
                    dims = i_class.split(':')
                    class_name = dims[0]
                    dims = dims[1].split('x')

                    nd[class_name] = {
                        'width': int(dims[0]),
                        'height': int(dims[1])
                    }

                width = nd[image_class]['width']
                height = nd[image_class]['height']
            except KeyError:
                raise #Exception('Unable to find image class: ' + image_class)


        target_file = source_file.replace('.', '_' + image_class + '.')
        resize = True
    elif image_size:
        dims = image_size.split('x')
        target_file = source_file.replace('.', '_' + image_size + '.')

        if len(dims) != 2:
            raise Exception('Unable to parse WidthxHeight: ' + image_size)

        width = int(dims[0])
        height = int(dims[1])
        resize = True
    else:
        target_file = source_file
        resize = False

    # Image src
    relative_target_url = join(site.asset_source_dir[len(site.site_dir):], 'sc_img')
    relative_target_url = relative_target_url.replace(sep, '/')
    img_src = site.base_url + relative_target_url + '/' + target_file

    # Create target dir if needed
    target_dir = join(site.asset_source_dir, 'sc_img')
    makedirs(target_dir, exist_ok=True)

    target_file_path = join(target_dir, target_file)


    #If image already exists, check if source is newer than target, else is target has correct dimensions, failing all that then resize
    create_target = False
    if isfile(target_file_path):
        if getmtime(target_file_path) < getmtime(image_source):
            create_target = True
    else:
        create_target = True

    if create_target:
        logger.debug('Resizing image: ' + image_source)
        im = Image.open(image_source)

        # Rotate if specified in exif
        #exif = im._getexif()
        #ORIENTATION = 274
        #if exif is not None and ORIENTATION in exif:
        #    orientation = exif[ORIENTATION]
        #    method = {2: Image.FLIP_LEFT_RIGHT, 4: Image.FLIP_TOP_BOTTOM, 8: Image.ROTATE_90, 3: Image.ROTATE_180, 6: Image.ROTATE_270, 5: Image.TRANSPOSE, 7: Image.TRANSVERSE}
        #    if orientation in method:
        #        im = im.transpose(method[orientation])

        im.thumbnail((width, height), Image.ANTIALIAS)
        im.save(target_file_path)
    else:
        logger.debug('Getting cached image: ' + image_source)
        im = Image.open(target_file_path)

    img_width, img_height = im.size

    html = '<img src="' + img_src + '" alt="' + alt_attribute + '" width="' + str(img_width) + '" height="' + str(img_height) + '" />'

    return html

