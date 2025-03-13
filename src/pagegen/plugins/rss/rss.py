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
                    logger.critical(f'Page is missing mandatory date header: {p_path}')
                    raise Exception(f'Page is missing mandatory date header: {p_path}')
                feed_pages.append(p)

        feed = ''

        # Feed channel info
        try:
            feed += f'<title>{s.conf["rss"]["title"]}</title>\n'
            feed += f'<link>{s.base_url}</link>\n'
            feed += f'<description>{s.conf["rss"]["description"]}</description>\n'

        except KeyError as e:
            logger.critical(f'RSS config is missing mandatory setting: {e.args[0]}')


        # Feed items
        for p in sorted(feed_pages, key=lambda p: p.headers['date']):
            feed += '<item>\n'
            try:
                feed += f'<title>{p.headers["title"]}</title>\n'
                feed += f'<link>{p.absolute_url}</link>\n'
                feed += f'<guid>{p.absolute_url}</guid>\n'
                feed += f'<pubDate>{p.headers["date"]}T06:00:00-02:00</pubDate>\n'
                feed += f'<description>{p.headers["description"]}</description>\n'

            except KeyError as e:
                logger.critical(f'Page is missing mandatory {e.args[0]}: {p_path}')
                raise

            feed += '</item>\n'

        feed = f'<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n<atom:link href="{s.base_url}/feed.rss" rel="self" type="application/rss+xml" />\n' + feed + '</channel></rss>'

        rss_path = join(s.build_dir, 'feed.rss')

        if not exists(rss_path):
            logger.info(f'Writing RSS: {rss_path}')
            self.write_file(rss_path, feed)
        else:
            logger.debug(f'RSS already exists: {rss_path}')


