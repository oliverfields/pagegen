from os.path import join, isdir, isfile
from pagegen.constants import CACHE_DIR
from pagegen.Common import Common
from pagegen.Page import Page
from hashlib import md5
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Plugin(Common):
    '''
    Page header tags allows tagging a page with one or more tags. For each tag create a page that links to all pages for the given tag
    '''

    def hook_post_build(self, objects):

        global i
        i = objects['index']
        global s
        s = objects['site']
        global c
        c = objects['site'].conf

        self.cache_dir = join(s.site_dir, CACHE_DIR, 'Plugins', __name__)
        self.cache_file = 'tag_hashes'
        self.cache_path = join(self.cache_dir, self.cache_file)

        # Check tag dir does not exist in build dir
        try:
            tag_dir = join(s.build_dir, c['tags']['tag_directory'])

            if isdir(tag_dir):
                logger.error(f'Tag directory already exists, can use setting tags section setting tag_directory to change: {tag_dir}')
                raise Exception
        except Exception as e:
            print(type(e))

        self.load_tags()

        self.load_hash_cache()

        self.generate_tag_pages()

        self.write_hash_cache()

        print(self.tags)


    def hash(self, s):
        return md5(s.encode('utf-8')).hexdigest()


    def load_hash_cache(self):
        '''
        Load cached hashes
        '''

        try:
            self.cached_tag_hashes = self.load_pickle(self.cache_path)
            logger.info('Loading cached tags hash')
        except FileNotFoundError:
            self.cached_tag_hashes = {}
            logger.info('No cached tags hash found')


    def write_hash_cache(self):
        hash_cache = {}

        # Add tags
        for k, v in self.tags.items():
            hash_cache[k] = v['hash']

        # Add overview
        hash_cache['__tags_overview'] = self.hash((c['tags']['tags']))

        self.pickle_object(self.cache_dir, self.cache_file, hash_cache)


    def generate_tag_pages(self):
        '''
        Generate one page per tag and one overview tag page
        '''

        #if self.tag'__tags_overview':
        if '__tags_overview' in self.cached_tag_hashes.keys() and self.hash(c['tags']['tags']) == self.cached_tag_hashes['__tags_overview']:
            pass
        else:
            print('build tags overview page')

        for tag, v in self.tags.items():
            if tag in self.cached_tag_hashes.keys() and v['hash'] == self.cached_tag_hashes[tag]:
                build = False
            elif v['pages'] == [] and isfile(v['source_path']):
                build = False
            else:
                build = True

            if build:
                print(f'{tag}: build -> {build}')
                p_content = f'template: tag\ntitle: {v["title"]}\n\n'

                for p in v['pages']:
                    p_content += f'- [{p["title"]}]({p["url"]})\n'

                self.build_tag_page(v, p_content)
            # If build then write page content to cache dir, create Page object and call HOOK_PAGE_RENDER and save output in build dir
            else:
                
                print(f'{tag}: copy ' + v['source_path'] + ' -> ' + v['target_path'])


    def build_tag_page(self, meta, content):
        '''
        Save page content to cache and build page using HOOK_PAGE_RENDER, saving it to build dir
        '''

        print('building')
        #p = Page(content['source_path'], content['target_path'], s)


    def load_tags(self):
        '''
        Load tags
        '''

        self.tags = {}

        try:
            for t in c['tags']['tags'].split(','):
                t_name = t.strip()
                t_url = t_name.lower()
                t_url = t_url.replace(' ', '-')

                self.tags[t_name] = {
                    'url_part': f'/tag/{t_url}',
                    'title': t_name,
                    'target_path': join(s.build_dir, 'tag', t_url),
                    'source_path': join(self.cache_dir, 'pages', t_url),
                    'pages': []
                }
        except KeyError:
            logger.error('No tags defined in site.conf, add [tags] section and then setting tags=Tag1, Tag2 etc')
            raise

        self.assign_pages_to_tags()

        # Generate tag hashes for each tag
        for k, v in self.tags.items():
            tag_hash = self.hash(str(v))
            v['hash'] = tag_hash

        # Generate tag hash for overview page
        self.overview_hash = self.hash(c['tags']['tags'])


    def assign_pages_to_tags(self):
        '''
        Scan index and assigne each page to its respective tag
        '''

        for url, p_meta in i.items():
            try:
                p_tags_csv = p_meta['headers']['tags']
            except KeyError:
                continue

            p_tags = p_tags_csv.split(',')

            for pt in p_tags:
                pt = pt.strip()

                if not pt in self.tags.keys():
                    logger.error(f'Page header contains unknown tag: {pt}: {url}')
                    raise Exception('Unknown tag in header')

                try:
                    self.tags[pt]['pages'].append({
                        'url': p_meta['url'],
                        'title': p_meta['headers']['title']
                    })
                except AttributeError as e:
                    logger.error(f'Page missing {e.name} attribute: {url}')
