from os import listdir
from os.path import join
from mako import util, lexer
import logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)
#from mako.parsetree import InheritTag, BlockTag, IncludeTag

# Thanks! https://groups.google.com/g/mako-discuss/c/rNj6Vxc984k/m/dVM08xaUAmoJ

class Plugin():

    def pgn_hook_pre_build(self, objects):
        '''
        Parse each template and work out its dependencies
        '''

        self.theme_template_dir = join(objects['site'].theme_dir, 'templates')
        self.template_deps = {}

        print('TODO if no changes to templates since cache then load cache, else reload template deps and write to cache')

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


    def pgn_hook_render_template(self, objects):
        '''
        Apply the templates to the page content
        '''
        print('TODO actually apply templates here?')



    def pgn_hook_page_post_build(self, objects):
        '''
        After page is built add add its templates as dependencies, so in future changing a dependent template will trigger the page to rebuild
        '''

        try:
            template_name = objects['page'].headers['template']
        except KeyError:
            template_name = 'pages'

        template_path = join(self.theme_template_dir, template_name + '.mako')

        td = self.template_deps[template_path]

        # Add header template too
        td.insert(0, template_path)

        # Add page dependencies
        objects['site'].dep_graph.add(objects['page'].source_path, td)


