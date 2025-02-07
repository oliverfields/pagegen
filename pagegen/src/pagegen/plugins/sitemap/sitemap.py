from pagegen.Common import Common
from os.path import join
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
            if not 'sitemap exclude' in p.headers.keys() or not p.headers['sitemap exclude']:
                sitemap += p.absolute_url + '\n'

        logger.info('Writing sitemap.txt')
        self.write_file(join(s.build_dir, 'sitemap.txt'), sitemap)
