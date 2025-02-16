from htmlmin import minify
from jsmin import jsmin
from rcssmin import cssmin
from glob import glob
from configparser import NoSectionError
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)


class Plugin():
    '''
    Minify page html, css and javascript files
    '''

    def hook_page_render(self, objects):
        '''
        Minify page html
        '''
        s = objects['site']

        try:
            minify_html = s.conf.getboolean('minify', 'minify_html')
        except NoSectionError:
            minify_html = True
        except KeyError:
            minify_html = True

        if not minify_html:
            return

        p = objects['page']
        exclude_header = 'minify html'

        if not exclude_header in p.headers.keys() or not p.headers[exclude_header]:
            logger.debug(f'Minifying: {p}')
            p.out = minify(p.out)


    def hook_post_build(self, objects):
        '''
        Minify any css or javascript in build asset and build theme dirs
        '''
        s = objects['site']

        try:
            minify_css = s.conf.getboolean('minify', 'minify_css')
        except KeyError:
            minify_css = True
        except NoSectionError:
            minify_css = True

        try:
            minify_js = s.conf.getboolean('minify', 'minify_js')
        except KeyError:
            minify_js = True
        except NoSectionError:
            minify_js = True


        for d in [s.asset_target_dir, s.theme_asset_target_dir]:
            pathname = d + '/**/*'
            files = glob(pathname, recursive=True)

            for f in files:
                is_css = True if f.endswith('.css') else False
                is_js = True if f.endswith('.js') else False

                if is_css and not minify_css:
                    continue

                if is_js and not minify_js:
                    continue

                if is_css or is_js:
                    logger.debug(f'Minifying: {f}')
                    with open(f, 'r+') as ff:
                        text = cssmin(ff.read()) if is_css else jsmin(ff.read())
                        ff.seek(0)
                        ff.write(text)
                        ff.truncate()

