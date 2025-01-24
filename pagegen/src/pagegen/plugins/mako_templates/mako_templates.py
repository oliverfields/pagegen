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
        #Add deps to dep_graph
        self.theme_template_dir = join(objects['site'].theme_dir, 'templates')
        template_deps = self.get_template_deps(self.theme_template_dir)
        print(template_deps)


    def pgn_hook_page_deps(self, objects):
        '''
        Add template dependencies
        '''

    def pgn_hook_render_template(self, objects):
        '''
        
        '''


    def pgn_hook_page_post_build(self, objects):
        '''
        
        '''

        # Add new page dependencies 
        try:
            template_name = objects['page'].headers['template']
        except KeyError:
            template_name = 'pages'

        template_path = join(self.theme_template_dir, template_name + '.mako')
        td = self.template_deps[template_path]

        # Add header template too
        td.insert(0, template_path)

        # Add page dependencies
        self.dep_graph.add(p.source_path, td)



    def get_template_deps(self, template_dir):
        '''
        Parse each template and work out its dependencies
        '''
        self.deps = {}

        for t in listdir(template_dir):
            t_path = join(template_dir, t)

            self.deps[t_path] = []

            text = util.read_file(t_path)
            lex = lexer.Lexer(text=text, filename=t_path)
            lex.parse()

            for n in lex.template.nodes:
                if getattr(n, 'keyword', None) == 'inherit': #if isinstance(n, InheritTag):
                    self.deps[t_path].append(join(template_dir, n.attributes['file']))
                elif getattr(n, 'keyword', None) == 'block': #elif isinstance(n, BlockTag):
                    for nn in n.nodes:
                        if getattr(nn, 'keyword', None) == 'include': #if isinstance(nn, IncludeTag):
                            self.deps[t_path].append(join(template_dir, nn.attributes['file']))
