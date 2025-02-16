from pagegen.Common import Common
from os.path import join, exists
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Plugin(Common):
    '''
    Simple sitemap.txt
    '''

    def hook_post_build(self, objects):
        '''
        Write sitemap to build dir
        '''

        s = objects['site']

        sitemap = ''
        for p in s.index.values():
            if not 'sitemap' in p.headers.keys() or p.headers['sitemap'] != False:
                sitemap += p.absolute_url + '\n'

        sitemap_path = join(s.build_dir, 'sitemap.txt')

        if not exists(sitemap_path):
            logger.debug(f'Writing sitemap: {sitemap_path}')
            self.write_file(sitemap_path, sitemap)
        else:
            logger.error(f'Sitemap already exists: {sitemap_path}')
