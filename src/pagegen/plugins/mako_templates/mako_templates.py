from os import listdir
from pagegen.constants import CACHE_DIR
from datetime import date
from os.path import join, getmtime
from mako import util, lexer
from mako.template import Template
from mako.lookup import TemplateLookup
from pagegen.Common import Common
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)
#from mako.parsetree import InheritTag, BlockTag, IncludeTag

# Thanks! https://groups.google.com/g/mako-discuss/c/rNj6Vxc984k/m/dVM08xaUAmoJ

class Plugin(Common):

    def hook_pre_build(self, objects):
        '''
        Create mako template lookup for use when rendering
        Parse each template and work out its dependencies
        '''

        self.theme_template_dir = join(objects['site'].theme_dir, 'templates')
        self.template_deps = {}
        self.cache_dir = join(objects['site'].site_dir, CACHE_DIR, 'mako_templates')
        self.plugin_cache_file_name = 'template_deps'
        self.plugin_cache_path = join(self.cache_dir, self.plugin_cache_file_name)

        self.mako_lookup = TemplateLookup(
            directories=[self.theme_template_dir],
            module_directory=self.cache_dir,
            collection_size=500 # Caching
        )

        self.template_context = {
            'site': objects['site'],
            'year': date.today().strftime('%Y'),
            'month': date.today().strftime('%m'),
            'day': date.today().strftime('%d'),
        }

        # Work out template deps
        try:
            if self.is_newer_than(self.plugin_cache_path, self.theme_template_dir):
                logger.debug('Loading template dependencies from cache')

                self.template_deps = self.load_pickle(self.plugin_cache_path)
                return
        except FileNotFoundError:
            pass

        logger.debug('Template dependency cache not found: Initalizing')

        # Collect dependencies between templates
        for t in listdir(self.theme_template_dir):
            t_path = join(self.theme_template_dir, t)

            self.template_deps[t_path] = []

            text = util.read_file(t_path)
            lex = lexer.Lexer(text=text, filename=t_path)
            lex.parse()

            for n in lex.template.nodes:
                if getattr(n, 'keyword', None) == 'inherit': #if isinstance(n, InheritTag):
                    self.template_deps[t_path].append(join(self.theme_template_dir, n.attributes['file']))
                elif getattr(n, 'keyword', None) == 'block': #elif isinstance(n, BlockTag):
                    for nn in n.nodes:
                        if getattr(nn, 'keyword', None) == 'include': #if isinstance(nn, IncludeTag):
                            self.template_deps[t_path].append(join(self.theme_template_dir, nn.attributes['file']))

        self.pickle_object(self.cache_dir, self.plugin_cache_file_name, self.template_deps)


    def hook_page_render(self, objects):
        '''
        Apply the templates to the page content
        '''

        p = objects['page']
        s = objects['site']

        # If page has template header use it to render template
        template = False

        if 'template' in p.headers.keys():
            template = p.headers['template']
        elif s.conf.has_option('mako_templates', 'default_template'):
            template = s.conf['mako_templates']['default_template']
        else:
            logger.critical('No template defined, set page template header or mako_templates default_template in site.conf: ' + str(p))
            raise Exception

        if template:
            self.template_context['page'] = p

            t = self.mako_lookup.get_template(template + '.mako')

            p.out = t.render(**self.template_context)


    def hook_page_post_build(self, objects):
        '''
        After page is built add add its templates as dependencies, so in future changing a dependent template will trigger the page to rebuild
        '''

        try:
            template_name = objects['page'].headers['template']
        except KeyError:
            # Skip applying template if none defined
            return

        template_path = join(self.theme_template_dir, template_name + '.mako')

        try:
            td = self.template_deps[template_path]
        except KeyError:
            logging.error(f'Template header path {template_path} not found, referenced in in page {objects["page"]}')
            raise

        # Add header template too
        td.insert(0, template_path)

        # Add page dependencies
        objects['site'].dep_graph.add(objects['page'].source_path, td)


