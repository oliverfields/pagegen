import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Plugin():

    def hook_post_build(self, objects):
        i = objects['index']
        tags = {}

        for url, p_meta in i.items():
            try:
                p_tags_csv = p_meta['headers']['tags']
            except KeyError:
                continue

            p_tags = p_tags_csv.split(',')

            for t in p_tags:
                if not t in tags.keys():
                    tags[t] = []

                try:
                    tags[t].append({
                        'url': p_meta['url'],
                        'title': p_meta['headers']['title']
                    })
                except AttributeError as e:
                    logger.error(f'Page missing {e.name} attribute: {url}')

        print(tags)
