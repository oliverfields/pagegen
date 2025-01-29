from Common import Common
from os.path import join
from constants import CACHE_DIR
import logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Plugin(Common):
    '''
    RSS feed
    '''

    def hook_post_build_lists(self, objects):
        '''
        Load cache
        '''

        self.cache_dir = join(objects['site'].site_dir, CACHE_DIR, 'rss')
        self.plugin_cache_file_name = 'index'
        self.plugin_cache_path = join(self.cache_dir, self.plugin_cache_file_name)

        try:
            logger.info('Loading rss index from cache')
            self.index = self.load_pickle(self.plugin_cache_path)
        except FileNotFoundError:
            logger.info('rss index cache not found')
            self.index = {}


    def hook_page_post_build(self, objects):
        '''
        Add page data to index
        '''

        p = objects['page']

        self.index[p.source_path] = {
            'url': p.absolute_url,
            'headers': p.headers
        }


    def hook_post_build(self, objects):
        '''
        Create rss feed and save index
        remove each item in index that is not in site.content_list
        if item in content_list but not in index throw error, in that case need to rebuild cache (site)
        '''

        s = objects['site']

        # The index must contain same items as content list, remove any from index that no longer exist
        for p_path in self.index.copy().keys():
            if not p_path in s.content_dir_list:
                logger.info(f'Deleting from RSS index: {p_path}')
                del self.index[p_path]

        # Sanity check that the two lists are equal
        if list(self.index.keys()) != s.content_dir_list:
            logger.error('RSS index does not match content list, maybe clear cache and try again?')
            raise

        feed = ''
        for p_path, p in self.index.items():
            if not 'exclude rss' in p['headers'].keys() or not p['headers']['exclude rss']:
                feed += '<item>\n'
                try:
                    feed += f'<title>{p["headers"]["title"]}</title>\n'
                    feed += f'<link>{p["url"]}</link>\n'
                    feed += f'<description>{p["headers"]["description"]}</description>\n'

                except KeyError as e:
                    logger.error(f'Page is missing mandatory {e.args[0]}: {p_path}')
                    raise

                feed += '</item>\n'

        feed = '<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0">\n<channel>\n' + feed + '</channel>'

        logger.info('Writing feed.rss')
        self.write_file(join(s.build_dir, 'feed.rss'), feed)

        self.pickle_object(self.cache_dir, self.plugin_cache_file_name, self.index)
