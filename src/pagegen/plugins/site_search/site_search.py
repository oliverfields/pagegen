from pagegen.Common import Common
from json import dumps
from re import sub
from pagegen.constants import CACHE_DIR
from os.path import join
from os import linesep
from lxml import etree
import pagegen.logger_setup
import logging


logger = logging.getLogger('pagegen.' + __name__)


class Plugin(Common):
    '''
    Create json index of all page search terms(words)
    Search index created from rendered HTML, weighting the terms based on the HTML tags thet appear in
    '''


    def hook_page_deps(self, objects):
        '''
        load search_index from cache, if exist (pickle object)
        prune any pages not in site index from search index
        '''

        self.cache_dir = join(objects['site'].site_dir, CACHE_DIR, 'site_search')
        self.content_tags=['p','li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'strong', 'em', 'i', 'b', 'a', 'blockquote', 'div', 'span', 'pre', 'abbr', 'address', 'cite', 'code', 'del', 'dfn', 'ins', 'kbd', 'q', 'samp', 'small', 'sub', 'sup', 'var', 'dt', 'dd', 'legend', 'caption', 'article', 'aside', 'details', 'figcaption', 'section', 'summary', 'title'] # HTML tags that may contain searchable content
        self.meta_tags = ['description'] # Meta tags attributes that may contain searchable content

        try:
            self.index_xpaths = objects['site'].conf['site_search']['index_xpaths'].replace(' ', '').split(',') # Xpath to nodes to look for indexable content in
        except KeyError:
            logger.warning('No setting index_xpaths in section site_search, defaulting to body tag')
            self.index_xpaths = ['/html/body']


        stop_words_path = join(objects['site'].site_dir, 'search_site_stopwords.txt')
        try:
            stop_words = self.read_file(stop_words_path)
            self.stop_words = stop_words.rstrip().split(linesep)
            logger.debug('Stop words loaded: ' + stop_words_path)
        except FileNotFoundError:
            logger.debug('No stop words found: ' + stop_words_path)
            self.stop_words = []

        self.index_cache_file_name = 'search_index'
        self.index_cache_path = join(self.cache_dir, self.index_cache_file_name)

        try:
            self.search_index = self.load_pickle(self.index_cache_path)
            logger.debug('Cached search index loaded')
        except FileNotFoundError:
            logger.debug('No cached search index found')
            self.search_index = {}


    def hook_page_post_build(self, objects):
        '''
        index terms for every generated page
        '''

        p = objects['page']

        # Ignore pages with header search: False
        if 'search' in p.headers.keys() and p.headers['search'] == False:
            return

        self.search_index[p.source_path] = {}
        si = self.search_index[p.source_path]

        tree = etree.HTML(p.out)

        # Look for terms in meta tags
        for search_attribute in self.meta_tags:
            try:
                result = tree.xpath("//meta[@name='"+search_attribute+"']")
                for tag in result:
                    self.index_string(si, tag.attrib['content'], 5)
            except:
                raise # No meta tags found, fair enough

        # Look for terms in title tag
        try:
            result = tree.xpath("/html/head/title")
            for tag in result:
                text = ''
                if tag.text:
                    text += tag.text + ' '
                if tag.tail:
                    text += tag.tail

                self.index_string(si, text, 5)
        except:
            raise # Unable to find a title


        # Look for terms in content
        for content_tag in self.index_xpaths:
            for search_tag in self.content_tags:
                xpath = content_tag + "//" + search_tag

                result = tree.xpath(xpath)
                for tag in result:
                    text = ''
                    if tag.text:
                        text += tag.text+' '
                    if tag.tail:
                        text += tag.tail

                    if text:
                        if tag.tag == 'h1':
                            weight = 7
                        elif tag.tag == 'h2':
                            weight = 6
                        elif tag.tag == 'h3':
                            weight = 5
                        elif tag.tag == 'h4':
                            weight = 4
                        elif tag.tag == 'h5':
                            weight = 3
                        elif tag.tag == 'h6':
                            weight = 2
                        elif tag.tag == 'strong' or tag.tag == 'em' or tag.tag == 'b' or tag.tag == 'i':
                            weight=1
                        else:
                            weight=0

                        self.index_string(si, text, weight)


    def hook_post_build(self, objects):
        '''
        prune search_index of deleted pages
        save cache
        '''

        # Prune terms for any pages that no longer exist in site.index
        for source_path in list(self.search_index.keys()):
            if not source_path in objects['site'].index.keys():
                del self.search_index[source_path]

        self.write_search_index()

        # update cache
        self.pickle_object(self.cache_dir, self.index_cache_file_name, self.search_index)


    def index_string(self, terms, string, weight):
        '''
        For each word in string add to terms with given weight, if not a stop word
        '''

        # Index only lowercase
        string_original = string
        string = string.lower()

        if not string:
            return True

        #print("indexing -> %s" % string)

        for word in string.split(' '):

            word = sub('[^a-z0-9]*', '', word)
            word = word.strip()

            if len(word) == 0:
                continue

            if word in self.stop_words:
                #print('Word "%s" is stop word' % (word))
                continue

            term_weight = weight

            # Update weight if is indexed
            if word in terms.keys():
                if terms[word] < term_weight:
                    #print("Increasing weight for term '%s'" % word)
                    terms[word] = term_weight
            else:
                #print('Adding term "%s" to index (weight %s)' % (word, term_weight))
                terms[word] = term_weight

        return terms



    def write_search_index(self):
        '''
        convert search_index to /search.json
        '''

        i = {
            'urls': {
                '1': ['url', 'title', 'description']
            },
            'terms': {
                'static': [1,15,2,8,18,19,23,24],
                'web': [25,23,1,3,9]
            }
        }

        json = dumps(i)
        self.write_file(join(objects['site'].build_dir, 'site-search-index.json'), json)

        '''
{
  "urls": {
    "1": [
      "/",
      "Pagegen static site generator",
      "Pagegen is a static web site generator, it creates web sites from    text files and directories. Manage your site from the command line."
    ]
  },
  "terms": {
    "static": [1,15,2,8,18,19,23,24],
    "web": [25,23,1,3,9,11,18,22,24]
  }
}
        '''

        print('Writing /search.json')
