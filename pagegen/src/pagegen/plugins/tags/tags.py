from os.path import join, isdir, isfile, dirname
from pagegen.constants import CACHE_DIR, HOOK_PAGE_RENDER
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

        if 'directory' in c['tags'].keys():
            self.tag_build_dir_name = c['tags']['directory']
        else:
            self.tag_build_dir_name = 'tag'

        if 'overview_template' in c['tags'].keys():
            self.overview_template = c['tags']['overview_template']
        else:
            self.overview_template = 'tag_overview'

        if 'tag_template' in c['tags'].keys():
            self.tag_template = c['tags']['tag_template']
        else:
            self.tag_template = 'tag_page'

        if 'overview_name' in c['tags'].keys():
            self.overview_name = c['tags']['overview_name']
        else:
            self.overview_name = 'tags.html'

        self.cache_dir = join(s.site_dir, CACHE_DIR, 'Plugins', __name__)
        self.page_cache_dir = join(self.cache_dir, 'tag_pages')
        self.page_build_dir = join(s.build_dir, self.tag_build_dir_name)
        self.cache_file = 'tag_hashes'
        self.cache_path = join(self.cache_dir, self.cache_file)

        self.make_dir(self.cache_dir)
        self.make_dir(self.page_cache_dir)

        # Check tag dir does not exist in build dir
        tag_dir = join(s.build_dir, self.tag_build_dir_name)

        if isdir(tag_dir):
            logger.error(f'Tag directory already exists, can use setting tags section setting tag_directory to change: {tag_dir}')
            raise Exception

        self.make_dir(self.page_build_dir)

        self.load_tags()

        self.load_hash_cache()

        self.generate_tag_pages()

        self.write_hash_cache()


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

        self.pickle_object(self.cache_dir, self.cache_file, hash_cache)


    def generate_tag_pages(self):
        '''
        Generate one page per tag and one overview tag page
        '''

        #Make tags available in templates
        s.cache['tags'] = self.tags

        overview_cache_path = join(self.page_cache_dir, self.overview_name)
        overview_build_path = join(self.page_build_dir, self.overview_name)
        logger.info('Building overview tag page')
        p_content = ''
        for t, data in dict(sorted(self.tags.items())).items():
            p_content += f'<li><a href="{data["rel_url"]}">{["title"]}</a></li>\n'

        p_content = f'template: {self.overview_template}\ntitle: Tags\n\n<ol>\n{p_content}</ol>\n'

        self.build_tag_page(overview_cache_path, p_content)
        self.copy_path(overview_cache_path, overview_build_path)


        # Tag pages
        for tag, v in self.tags.items():
            if tag in self.cached_tag_hashes.keys() and v['hash'] == self.cached_tag_hashes[tag]:
                build = False
            elif v['pages'] == [] and isfile(v['target_path']):
                build = False
            else:
                build = True

            if build:
                logger.info(f'Building tag page: {tag}')
                p_content = ''

                for p in sorted(v['pages'], key=lambda d: d['headers']['title']):
                    p_content += f'<li><a href="{p["rel_url"]}">{p["headers"]["title"]}</a></li>\n'

                p_content = f'template: {self.tag_template}\ntitle: {tag}\ntag_key: {tag}\n\n<ol>\n{p_content}</ol>\n'

                self.build_tag_page(v['target_path'], p_content)

            logger.info(f'Copying tag page to build dir: {tag}')
            self.copy_path(v['target_path'], v['build_path'])


    def build_tag_page(self, cache_path, content):
        '''
        Generate page and save it to cache dir using HOOK_PAGE_RENDER
        '''

        p = Page()
        p.load(cache_path, s, raw_string=content)
        s.exec_hooks(HOOK_PAGE_RENDER, {'site': s, 'page': p})
        p.write()


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
                    'rel_url': f'/{self.tag_build_dir_name}/{t_url}',
                    'title': t_name,
                    'target_path': join(self.page_cache_dir, t_url),
                    'build_path': join(s.build_dir, self.tag_build_dir_name, t_url), 
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


    def assign_pages_to_tags(self):
        '''
        Scan index and assigne each page to its respective tag
        '''

        for url, p_meta in i.items():
            try:
                p_tags_csv = p_meta.headers['tags']
            except KeyError:
                continue

            p_tags = p_tags_csv.split(',')

            for pt in p_tags:
                pt = pt.strip()

                if not pt in self.tags.keys():
                    logger.error(f'Page header contains unknown tag, add it to site.config if you want to create the new tag: {pt}: {url}')
                    raise Exception('Unknown tag in header')

                try:
                    self.tags[pt]['pages'].append({
                        'relative_url': p_meta.relative_url,
                        'absolute_url': p_meta.absolute_url,
                        'rel_url': p_meta.url[len(s.base_url):],
                        'headers': p_meta.headers
                    })
                except AttributeError as e:
                    logger.error(f'Page missing {e.name} attribute: {url}')
                    raise Exception
