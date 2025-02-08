from pagegen.Common import Common
from os.path import join, exists
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Plugin(Common):
    '''
    RSS feed
    '''

    def hook_post_build(self, objects):
        '''
        Create rss feed and save index
        remove each item in index that is not in site.content_list
        if item in content_list but not in index throw error, in that case need to rebuild cache (site)
        '''

        s = objects['site']
        i = s.index

        feed_pages = []
        for p_path, p in i.items():
            if not 'rss' in p.headers.keys() or p.headers['rss'] != False:
                if not 'date' in p.headers.keys():
                    logger.error(f'Page is missing mandatory date header: {p_path}')
                    raise Exception(f'Page is missing mandatory date header: {p_path}')
                feed_pages.append(p)

        feed = ''

        # Feed channel info
        try:
            feed += f'<title>{s.conf["rss"]["title"]}</title>\n'
            feed += f'<link>{s.base_url}</link>\n'
            feed += f'<description>{s.conf["rss"]["description"]}</description>\n'

        except KeyError as e:
            logger.error(f'RSS config is missing mandatory setting: {e.args[0]}')
            raise


        # Feed items
        for p in sorted(feed_pages, key=lambda p: p.headers['date']):
            feed += '<item>\n'
            try:
                feed += f'<title>{p.headers["title"]}</title>\n'
                feed += f'<link>{p.absolute_url}</link>\n'
                feed += f'<description>{p.headers["description"]}</description>\n'

            except KeyError as e:
                logger.error(f'Page is missing mandatory {e.args[0]}: {p_path}')
                raise

            feed += '</item>\n'

        feed = '<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0">\n<channel>\n' + feed + '</channel>'

        rss_path = join(s.build_dir, 'feed.rss')

        if not exists(rss_path):
            logger.info(f'Writing RSS: {rss_path}')
            self.write_file(rss_path, feed)
        else:
            logger.warning(f'RSS already exists: {rss_path}')


